from .utils import (
    lonlat2aeqd,
    aeqd2lonlat_3d,
    has_normal,
    count_overlapping_features,
    calculate_normal,
    make_clockwise
)
from .analysis import get_timetable
from .pybdshadow import bdshadow_sunlight
from shapely.geometry import Polygon,  MultiPolygon, MultiPolygon, GeometryCollection
import geopandas as gpd
import numpy as np
import pandas as pd
import suncalc
from suncalc import get_times

def cal_multiple_wall_overlap_count(walls):
    def to_3d(result_wall):
        # 2d转3d
        # 提取并集或交集的坐标
        if isinstance(result_wall, Polygon):
            # 如果结果是单一多边形
            coords = np.array(result_wall.exterior.coords)
        elif isinstance(result_wall, MultiPolygon):
            # 如果结果是多边形集合，合并它们的坐标
            coords = np.concatenate([np.array(poly.exterior.coords)
                                    for poly in result_wall.geoms])
        else:
            return np.array([])
        # 计算平面方程中的常数 d
        d = -np.dot(normal_vector, p1)

        # 根据选择的坐标轴，反推缺失的坐标
        if coords_plane == (1, 2):  # y和z轴，需要反推x坐标
            if nx == 0:
                raise ValueError("平面方程无法解出唯一的x值")  # 无法处理垂直于x轴的平面
            x = -(ny * coords[:, 0] + nz * coords[:, 1] + d) / nx
            result = np.c_[x, coords]

        elif coords_plane == (0, 2):  # x和z轴，需要反推y坐标
            if ny == 0:
                raise ValueError("平面方程无法解出唯一的y值")
            y = -(nx * coords[:, 0] + nz * coords[:, 1] + d) / ny
            result = np.c_[coords[:, 0], y, coords[:, 1]]
        return Polygon(result)

    walls = list(walls['geometry'].apply(lambda x: list(x.exterior.coords)))
    p1 = walls[0][0]
    normal_vector = calculate_normal(walls[0])
    nx, ny, nz = normal_vector

    # 根据法向量的方向选择坐标轴
    if abs(nx) > abs(ny):
        # 法向量主要指向x轴，选择y和z轴
        coords_plane = (1, 2)
    else:
        # 法向量主要指向y轴，选择x和z轴
        coords_plane = (0, 2)

    gdf = gpd.GeoDataFrame(
        geometry=[Polygon(np.array(wall)[:, coords_plane]) for wall in walls])

    overlap = count_overlapping_features(gdf, buffer=False)

    overlap['geometry'] = overlap['geometry'].apply(to_3d)
    return overlap

def cal_multiple_wall_union(walls):
    """
    计算多个墙（平面）的并集。

    此函数通过接收一个包含多个墙面顶点的列表来计算它们的并集。每个墙面由至少三个顶点在三维空间中定义。

    参数:
    walls: 一个三维数组，其中每个元素是一个墙面的顶点列表。每个墙面是由三个或更多的三维点（x, y, z）组成的列表。
    例如 walls = [wall1,wall2] 其中，wall1: 第一个墙的坐标点列表，格式为 [[x1, y1, z1], [x2, y2, z2], ...]，wall2: 第二个墙的坐标点列表，格式为 [[x1, y1, z1], [x2, y2, z2], ...]

    返回:
    result: 并集的坐标点数组

    """

    walls = np.array(walls)
    p1, p2, p3 = walls[0][:3]
    normal_vector = calculate_normal(walls[0])
    nx, ny, nz = normal_vector

    # 根据法向量的方向选择坐标轴
    if abs(nx) > abs(ny):
        # 法向量主要指向x轴，选择y和z轴
        coords_plane = (1, 2)
    else:
        # 法向量主要指向y轴，选择x和z轴
        coords_plane = (0, 2)

    result_wall = MultiPolygon([Polygon(wall)
                               for wall in walls[:, :, coords_plane]]).buffer(0)

    # 提取并集或交集的坐标
    if isinstance(result_wall, Polygon):
        # 如果结果是单一多边形
        coords = np.array(result_wall.exterior.coords)
    elif isinstance(result_wall, MultiPolygon):
        # 如果结果是多边形集合，合并它们的坐标
        coords = np.concatenate([np.array(poly.exterior.coords)
                                for poly in result_wall.geoms])
    else:
        return np.array([])
    # 计算平面方程中的常数 d
    d = -np.dot(normal_vector, p1)

    # 根据选择的坐标轴，反推缺失的坐标
    if coords_plane == (1, 2):  # y和z轴，需要反推x坐标
        if nx == 0:
            raise ValueError("平面方程无法解出唯一的x值")  # 无法处理垂直于x轴的平面
        x = -(ny * coords[:, 0] + nz * coords[:, 1] + d) / nx
        result = np.c_[x, coords]

    elif coords_plane == (0, 2):  # x和z轴，需要反推y坐标
        if ny == 0:
            raise ValueError("平面方程无法解出唯一的y值")
        y = -(nx * coords[:, 0] + nz * coords[:, 1] + d) / ny
        result = np.c_[coords[:, 0], y, coords[:, 1]]

    return result

def cal_wall_overlap(wall1, wall2, method='intersection'):
    """
    计算两个墙（平面）的并集或交集。

    参数:
    wall1: 第一个墙的坐标点列表，格式为 [[x1, y1, z1], [x2, y2, z2], ...]
    wall2: 第二个墙的坐标点列表，格式为 [[x1, y1, z1], [x2, y2, z2], ...]
    method: 计算方式，'union' 为并集，'intersection' 为交集，默认为 'union'

    返回:
    result: 并集或交集的坐标点数组，格式与输入格式相同

    思路：
    核心思路是根据两个墙面（平面）的法向量来确定它们主要垂直于哪个坐标轴。然后，选择两个与主轴垂直的坐标轴来表征这些平面。
    例如，如果一个平面主要垂直于 x 轴，那么我们使用 y 和 z 轴。
    基于这些坐标轴，使用 Shapely 库创建多边形来代表每个墙面。
    接下来，计算这两个多边形在xz或yz平面的并集或交集。
    最后，根据先前选择的坐标轴，使用平面方程反推缺失的坐标值，以获取完整的三维坐标点集。
    这样就能够处理那些垂直于不同坐标轴的墙面，并计算它们的重叠部分。
    """

    # 计算法向量
    plane = wall1
    p1, p2, p3 = plane[:3]

    normal_vector = calculate_normal(plane)
    nx, ny, nz = normal_vector

    # 根据法向量的方向选择坐标轴
    if abs(nx) > abs(ny):
        # 法向量主要指向x轴，选择y和z轴
        coords_plane = (1, 2)
    else:
        # 法向量主要指向y轴，选择x和z轴
        coords_plane = (0, 2)

    # 将墙的坐标转换为多边形
    poly1 = Polygon(np.array(wall1)[:, coords_plane])
    if not poly1.is_valid:
        poly1 = poly1.buffer(0)
    poly2 = Polygon(np.array(wall2)[:, coords_plane])
    if not poly2.is_valid:
        poly2 = poly2.buffer(0)

    # 根据方法计算并集或交集
    if method == 'union':
        result_wall = poly1.union(poly2)
    elif method == 'intersection':
        result_wall = poly1.intersection(poly2)

    # 提取并集或交集的坐标
    final_result = None
    if isinstance(result_wall, Polygon):
        final_result = result_wall
    elif isinstance(result_wall, GeometryCollection):
        # 如果是几何集合，处理每个元素
        for geom in result_wall.geoms:
            if isinstance(geom, Polygon):
                if final_result is None:
                    final_result = geom
                else:
                    if method == 'union':
                        final_result = final_result.union(geom)
                    elif method == 'intersection':
                        final_result = final_result.intersection(geom)

    if final_result is not None and isinstance(final_result, Polygon):
        # 提取最终结果的坐标
        coords = np.array(final_result.exterior.coords)
    else:
        # 如果没有有效的 Polygon，返回空数组
        return np.array([])
    # 计算平面方程中的常数 d
    d = -np.dot(normal_vector, p1)

    # 根据选择的坐标轴，反推缺失的坐标
    if coords_plane == (1, 2):  # y和z轴，需要反推x坐标
        if nx == 0:
            raise ValueError("平面方程无法解出唯一的x值")  # 无法处理垂直于x轴的平面
        x = -(ny * coords[:, 0] + nz * coords[:, 1] + d) / nx
        result = np.c_[x, coords]

    elif coords_plane == (0, 2):  # x和z轴，需要反推y坐标
        if ny == 0:
            raise ValueError("平面方程无法解出唯一的x值", str(wall1), str(wall2))
            # raise ValueError("平面方程无法解出唯一的y值")  # 无法处理垂直于y轴的平面
            return None

        y = -(nx * coords[:, 0] + nz * coords[:, 1] + d) / ny
        result = np.c_[coords[:, 0], y, coords[:, 1]]

    return result

def calculate_wall_normal_vector(wall):
    """
    计算给定墙面的法向量。

    假设墙面顶点按顺时针方向给出。

    参数:
    wall : list 或 ndarray
        墙面上的点的集合，其中每个点是一个三维坐标 [x, y, z]。

    返回:
    normal_vector : ndarray
        墙面的法向量。
    """
    # 取墙面的前三个点
    p1, p2, p3 = np.array(wall[:3])

    # 计算两个向量，这两个向量在墙面上并且相互垂直
    v1 = p2 - p1
    v2 = p3 - p1

    # 计算法向量，使用叉积
    normal_vector = np.cross(v1, v2)

    # 标准化法向量
    normal_vector = normal_vector / np.linalg.norm(normal_vector)

    return normal_vector

def calculate_wall_plane(wall):
    p1, p2, p3 = np.array(wall[:3])
    v1 = p2 - p1
    v2 = p3 - p1
    normal_vector = np.cross(v1, v2)

    # 计算平面方程 Ax + By + Cz + D = 0 中的 A, B, C, D
    A, B, C = normal_vector
    D = -np.dot(normal_vector, p1)

    return A, B, C, D

def projection_on_wall_single(plane, sun_vec, wall, wall_normal):
    """
    计算单个墙在单个平面上由太阳光照射产生的投影点，并根据夹角判断是否保留投影点。

    输入:
    plane : ndarray
        平面方程的系数[A, B, C, D]。
    sun_vec : list 或 ndarray
        太阳光的方向向量，格式为 [vx, vy, vz]。
    wall : ndarray
        墙面上的点的集合，格式为 4*3。
    wall_normal : list 或 ndarray
        被投影墙面的法向量。

    输出:
    intersections : ndarray
        4*3大小的矩阵，平面每个点上由太阳光照射产生的投影点的坐标，不合理的投影点标记为None。
    """
    sun_vec = np.array(sun_vec)
    wall = np.array(wall)
    A, B, C, D = plane

    denominator = np.dot(np.array([A, B, C]), sun_vec)
    t = -(np.dot(wall, np.array([A, B, C])) + D) / denominator
    intersections = wall + np.outer(t, sun_vec)

    # 处理特殊情况，平行或无交点
    intersections[denominator == 0] = np.array([None, None, None])

    # 检查每个投影点是否在墙面法向量的“背面”
    for i in range(len(intersections)):

        if not np.any(np.isnan(intersections[i])):

            # 计算从墙面顶点到投影点的向量
            vector_to_projection = intersections[i] - wall[i]
            if np.linalg.norm(vector_to_projection) > 0:

                # 计算夹角

                angle = np.arccos(np.dot(vector_to_projection, wall_normal) / (
                    np.linalg.norm(vector_to_projection) * np.linalg.norm(wall_normal)))
                angle = np.degrees(angle)

            # 如果夹角小于0，将该投影点标记为None
                if angle < 90:
                    intersections[i] = np.array([None, None, None])
                    return np.array([])

    return intersections


def is_sunlight_reaching_wall(sun_vec, wall_normal):
    # 计算太阳光向量与墙面法线向量之间的夹角
    angle = np.arccos(np.dot(sun_vec, wall_normal) /
                      (np.linalg.norm(sun_vec) * np.linalg.norm(wall_normal)))
    angle = np.degrees(angle)
    return angle > 90


def sun_light_vector(azimuth, altitude):
    # 将角度转换为弧度
    azimuth_rad = -azimuth+np.pi/2
    altitude_rad = altitude

    # 计算球坐标系中的向量分量
    x = np.cos(altitude_rad) * np.cos(azimuth_rad)
    y = np.cos(altitude_rad) * np.sin(azimuth_rad)
    z = np.sin(altitude_rad)

    # 太阳光的方向是从太阳指向地球，因此需要反转向量
    return np.array([x, y, -z])

def convert_shadows_to_lonlat(all_shadows_coords, center_lon, center_lat):

    a = pd.DataFrame(all_shadows_coords).reset_index()

    b = a[a[0].apply(len) > 0].explode(0).reset_index(drop=True)
    b[0] = list(aeqd2lonlat_3d(np.array([list(b[0])]), center_lon, center_lat)[0])

    c = a[a[0].apply(len) == 0]

    b = b.groupby('index').apply(lambda x: list(x[0])).reset_index()
    a = pd.concat([b, c]).sort_values('index').reset_index(drop=True)
    return list(a[0])

def projections_from_wall_to_wall(merged_data):

    walls_target_shadow = merged_data[merged_data['face'] == False]

    walls_target_shadow = walls_target_shadow[[
        'building_id_left', 'target_wall_id', 'target_wall', 'date']]
    walls_target_shadow['shadow_projections'] = walls_target_shadow['target_wall']

    # walls_date_shadow = pd.concat([walls_date_shadow, walls_target_shadow])

    merged_data = merged_data[merged_data['face']]

    def calculate_projection(row):

        return projection_on_wall_single(
            row['target_wall_plane'],
            row['sun_vector'],
            row['shadow_wall'],
            row['target_wall_vector']
        )


# 应用修改后的函数计算投影
    merged_data['shadow_projections'] = merged_data.apply(
        calculate_projection, axis=1)
    merged_data = merged_data.dropna(subset=['shadow_projections'])

# 或者，如果空的 shadow_projections 以空列表或其他形式存在，您可以这样做：
    merged_data = merged_data[merged_data['shadow_projections'].apply(
        lambda x: x is not None and len(x) > 0)]

    condition = merged_data.apply(lambda row:
                                  (max([point[0] for point in row['target_wall']]) > min([point[0] for point in row['shadow_projections']])) and
                                  (max([point[2] for point in row['target_wall']]) > min(
                                      [point[2] for point in row['shadow_projections']])),
                                  axis=1)

    merged_data = merged_data[condition]
    merged_data = merged_data[[
        'building_id_left', 'target_wall', 'target_wall_id', 'date', 'shadow_projections']]

    merged_data = pd.concat([merged_data, walls_target_shadow])

    def aggregate_shadows(group):
        walls = group['shadow_projections'].tolist()
        aggregated_shadow = cal_multiple_wall_union(walls)
    # 返回一个包含所有必要数据的 DataFrame
        return pd.DataFrame({
            'building_id_left': [group.name[0]],
            'target_wall_id': [group.name[1]],
            'date': [group.name[2]],
            'aggregated_shadows': [aggregated_shadow],
            'target_wall': [group['target_wall'].iloc[0]]  # 假设仅返回第一个目标墙
        })

# 应用 aggregate_shadows 函数
    aggregated_shadows = merged_data.groupby(['building_id_left', 'target_wall_id', 'date']).apply(
        aggregate_shadows).reset_index(drop=True)


# 展开 DataFrame，因为 apply 返回的是 DataFrame 的列表
    if isinstance(aggregated_shadows.columns, pd.MultiIndex):
        aggregated_shadows.columns = [
            '_'.join(col).strip() for col in aggregated_shadows.columns.values]

# 计算交集并处理结果
    def calculate_intersection(row):
        return cal_wall_overlap(row['target_wall'], row['aggregated_shadows'], method='intersection')

    aggregated_shadows['intersection_shadow'] = aggregated_shadows.apply(
        calculate_intersection, axis=1)
    aggregated_shadows = aggregated_shadows.dropna(
        subset=['intersection_shadow'])

# 删除不需要的列
    result_gdf = aggregated_shadows.drop(
        ['aggregated_shadows', 'target_wall'], axis=1)

    result_gdf = result_gdf.dropna(subset=['intersection_shadow'])

# 或者，如果空的 shadow_projections 以空列表或其他形式存在，您可以这样做：
    result_gdf = result_gdf[result_gdf['intersection_shadow'].apply(
        lambda x: x is not None and len(x) > 0)]

    return result_gdf


def calculate_buildings_shadow_overlap(buildings_gdf, date, precision=3600, padding=1800):


    buildings_gdf['geometry'] = buildings_gdf['geometry'].apply(make_clockwise)
    original_indices = buildings_gdf.index.copy()

    # 确保建筑物数据使用正确的CRS
    center_lon, center_lat = buildings_gdf.unary_union.centroid.x, buildings_gdf.unary_union.centroid.y
    date_times = get_timetable(center_lon, center_lat, dates=[
                               date], precision=precision, padding=padding)

    # 转换建筑物坐标为 AEQD 坐标

    buildings_aeqd_gdf = buildings_gdf.copy()
    buildings_gdf_overlap = buildings_gdf[[
        'building_id', 'geometry', 'height']]

    for idx, row in buildings_gdf.iterrows():
        if isinstance(row.geometry, Polygon):
            lonlat_coords = np.array(
                row.geometry.exterior.coords).reshape(1, -1, 2)
        elif isinstance(row.geometry, MultiPolygon):
            lonlat_coords = np.concatenate([np.array(poly.exterior.coords).reshape(
                1, -1, 2) for poly in row.geometry.geoms], axis=1)
        else:
            continue

        aeqd_coords = lonlat2aeqd(lonlat_coords, center_lon, center_lat)
        buildings_aeqd_gdf.at[idx, 'geometry'] = Polygon(
            np.squeeze(aeqd_coords))
    buildings_aeqd_gdf_walls = get_walls(buildings_aeqd_gdf)
    buildings_aeqd_gdf_walls = buildings_aeqd_gdf_walls[[
        'building_id', 'geometry', 'height', 'wall_id']]
    walls_shadow = buildings_aeqd_gdf_walls.copy()

    walls_shadow.columns = ['building_id_right',
                            'shadow_wall', 'height', 'shadow_wall_id']

    walls_target = buildings_aeqd_gdf_walls.copy()

    walls_target.columns = ['building_id_left',
                            'target_wall', 'height', 'target_wall_id']

    def polygon_to_points(polygon):
        # 提取 Polygon 对象的外部轮廓坐标
        return list(polygon.exterior.coords)

# 应用转换函数
    walls_target['target_wall'] = walls_target['target_wall'].apply(
        polygon_to_points)

    walls_shadow['shadow_wall'] = walls_shadow['shadow_wall'].apply(
        polygon_to_points)
    walls_target['target_wall_vector'] = walls_target['target_wall'].apply(
        calculate_wall_normal_vector)
    walls_target['target_wall_plane'] = walls_target['target_wall'].apply(
        calculate_wall_plane)

    date_times['date'] = pd.to_datetime(date_times['date'])
    merged_data = pd.DataFrame()

    for date_time in date_times['date']:

        sun_position = suncalc.get_position(date_time, center_lon, center_lat)
        sun_azimuth = sun_position['azimuth']
        sun_altitude = sun_position['altitude']

        # 计算所有建筑物的阴影
        shadows_gdf = bdshadow_sunlight(buildings_gdf, date_time)
        shadows_gdf.index = original_indices

        # 确保阴影数据也使用相同的CRS
        if shadows_gdf.crs is None:
            shadows_gdf.set_crs(buildings_gdf.crs, inplace=True)
        shadows_gdf = shadows_gdf[['building_id', 'geometry']]

        overlapping = gpd.sjoin(buildings_gdf_overlap,
                                shadows_gdf, how='left', op='intersects')

        sun_vec = sun_light_vector(sun_azimuth, sun_altitude)
        walls_target['sun_vector'] = [sun_vec] * len(walls_target)

        def have_sun(row):

            return is_sunlight_reaching_wall(
                row['sun_vector'],
                row['target_wall_vector']
            )

        walls_target['face'] = walls_target.apply(have_sun, axis=1)

        walls_target['date'] = date_time
        overlapping = pd.merge(
            overlapping,  walls_target, on='building_id_left')

        overlapping = pd.merge(overlapping, walls_shadow,
                               on='building_id_right')

        overlapping = overlapping[-((overlapping['building_id_left'] == overlapping['building_id_right']) &
                                    (overlapping['target_wall_id'] == overlapping['shadow_wall_id']))]

        merged_data = pd.concat([merged_data, overlapping])
        # walls_target = walls_target.drop(['date','face','sun_vector'],axis=1)

    final_merged_data = projections_from_wall_to_wall(merged_data)

    final_merged_data['intersection_shadow_lonlat'] = convert_shadows_to_lonlat(
        final_merged_data['intersection_shadow'].tolist(), center_lon, center_lat)
    final_merged_data = final_merged_data.dropna(
        subset=['intersection_shadow_lonlat'])

    def create_polygon_from_coords(coords):
        # 仅当坐标列表不为空时创建 Polygon
        # if coords is not None and len(coords) > 2:
        return Polygon(coords)
        # return None

# 将 intersection_shadow 转换为 Polygon 对象
    final_merged_data['intersection_shadow_polygon'] = final_merged_data['intersection_shadow_lonlat'].apply(
        create_polygon_from_coords)
    # final_merged_data['target_wall'] = final_merged_data['target_wall'].apply(create_polygon_from_coords)
    final_merged_data = final_merged_data.rename(
        columns={'building_id_left': 'building_index'})
    # final_merged_data = final_merged_data.dropna(subset=['intersection_shadow_polygon'])
    # all_shadows_gdf = pd.concat([all_shadows_gdf, final_merged_data])

    final_merged_data = final_merged_data.drop(
        ['intersection_shadow', 'intersection_shadow_lonlat'], axis=1)

    return final_merged_data

def cal_sunshine_facade(buildings_gdf, day, precision=3600, padding=1800):

    # 计算阴影重叠情况
    final_shadow = calculate_buildings_shadow_overlap(
        buildings_gdf, day, precision=precision, padding=padding)

    final_shadow['building_id'] = final_shadow['building_index']

    # 求最大光照时长
    lon, lat = buildings_gdf['geometry'].iloc[0].bounds[:2]
    date = pd.to_datetime(day+' 12:45:33.959797119')
    times = get_times(date, lon, lat)
    date_sunrise = times['sunrise']
    data_sunset = times['sunset']
    timestamp_sunrise = pd.Series(date_sunrise).astype('int')
    timestamp_sunset = pd.Series(data_sunset).astype('int')
    sunlighthour = (
        timestamp_sunset.iloc[0]-timestamp_sunrise.iloc[0])/(1000000000*3600)

    # 从阴影重叠情况计算光照时长
    final_shadows_oneday = final_shadow.copy()
    buildings_walls = get_walls(buildings_gdf)
    buildings_walls = buildings_walls.rename(
        columns={'wall_id': 'target_wall_id'})
    buildings_walls = buildings_walls[[
        'building_id', 'target_wall_id', 'geometry']]
    final_shadows_oneday = final_shadows_oneday.rename(
        columns={'intersection_shadow_polygon': 'geometry'})
    final_shadows_oneday = pd.concat([final_shadows_oneday, buildings_walls])
    final_shadows_oneday = final_shadows_oneday[final_shadows_oneday['geometry'].apply(
        lambda x: has_normal(x.exterior.coords))]
    final_shadows_sunshinetime = final_shadows_oneday.groupby(
        ['building_id', 'target_wall_id']).apply(cal_multiple_wall_overlap_count)

    final_shadows_sunshinetime = final_shadows_sunshinetime.reset_index()

    final_shadows_sunshinetime['time'] = (
        final_shadows_sunshinetime['count']-1)*precision
    final_shadows_sunshinetime['Hour'] = sunlighthour - \
        final_shadows_sunshinetime['time']/3600
    final_shadows_sunshinetime.loc[final_shadows_sunshinetime['Hour']
                                   <= 0, 'Hour'] = 0
    return final_shadows_sunshinetime


def get_walls(buildings_gdf):
    # 把建筑物的墙面拆分成单独的面
    def get_wall(r):
        wall_coords = list(r['geometry'].exterior.coords)
        walls = []
        for i in range(len(wall_coords)-1):
            walls.append([Polygon([list(wall_coords[i])+[0],
                                   list(wall_coords[i+1])+[0],
                                   list(wall_coords[i+1])+[r['height']],
                                   list(wall_coords[i])+[r['height']],
                                   ]), i])
        return walls
    buildings_gdf['walls'] = buildings_gdf.apply(get_wall, axis=1)

    buildings_walls = buildings_gdf.explode('walls')
    buildings_walls['wall_id'] = buildings_walls['walls'].apply(lambda x: x[1])
    buildings_walls['geometry'] = buildings_walls['walls'].apply(
        lambda x: x[0])
    return buildings_walls.drop('walls', axis=1)
