"""
BSD 3-Clause License

Copyright (c) 2022, Qing Yu
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import numpy as np
import shapely
import geopandas as gpd
import pandas as pd
from pyproj import CRS,Transformer
from shapely.geometry import Polygon,MultiPolygon
import pvlib
from pvlib import location

def extrude_poly(poly,h):
    poly_coords = np.array(poly.exterior.coords)
    poly_coords = np.c_[poly_coords, np.ones(poly_coords.shape[0])*h]
    return Polygon(poly_coords)

def make_clockwise(polygon):
    if polygon.exterior.is_ccw:
        return polygon
    else:
        return Polygon(list(polygon.exterior.coords)[::-1])

def lonlat2aeqd(lonlat, center_lon, center_lat):
    '''
    Convert longitude and latitude to azimuthal equidistant projection coordinates.

    Parameters
    ----------
    lonlat : numpy.ndarray
        Longitude and latitude in degrees. The shape of the array is (n,m,2), where n and m are the number of pixels in the first and second dimension, respectively. The last dimension is for longitude and latitude.

    Returns
    -------
    proj_coords : numpy.ndarray
        Azimuthal equidistant projection coordinates. The shape of the array is (n,m,2), where n and m are the number of pixels in the first and second dimension, respectively. The last dimension is for x and y coordinates.

    example
    -----------------
    >>> import numpy as np
    >>> from pybdshadow import utils
    >>> lonlat = np.array([[[120,30],[121,31]],[[120,30],[121,31]]])
    >>> proj_coords = utils.lonlat2aeqd(lonlat)
    >>> proj_coords
    array([[[-48243.5939812 , -55322.02388971],
            [ 47752.57582735,  55538.86412435]],
           [[-48243.5939812 , -55322.02388971],
            [ 47752.57582735,  55538.86412435]]])
    '''
    epsg = CRS.from_proj4("+proj=aeqd +lat_0="+str(center_lat) +
                          " +lon_0="+str(center_lon)+" +datum=WGS84")
    transformer = Transformer.from_crs("EPSG:4326", epsg, always_xy=True)
    proj_coords = transformer.transform(lonlat[:, :, 0], lonlat[:, :, 1])
    proj_coords = np.array(proj_coords).transpose([1, 2, 0])
    return proj_coords

def aeqd2lonlat_3d(proj_coords, meanlon, meanlat):

    # 提取 xy 坐标和 z 坐标
    xy_coords = proj_coords[:, :, :2]
    z_coords = proj_coords[:, :, 2] if proj_coords.shape[2] > 2 else np.zeros(
        xy_coords.shape[:2])

    # 定义转换器
    epsg = CRS.from_proj4("+proj=aeqd +lat_0=" + str(meanlat) +
                          " +lon_0=" + str(meanlon) + " +datum=WGS84")
    transformer = Transformer.from_crs(epsg, "EPSG:4326", always_xy=True)

    # 转换 xy 坐标
    lon, lat = transformer.transform(xy_coords[:, :, 0], xy_coords[:, :, 1])

    # 将转换后的坐标和原始 z 坐标组合
    lonlat = np.dstack([lon, lat, z_coords])
    return lonlat

def aeqd2lonlat(proj_coords,meanlon,meanlat):
    '''
    Convert azimuthal equidistant projection coordinates to longitude and latitude.

    Parameters
    ----------
    proj_coords : numpy.ndarray
        Azimuthal equidistant projection coordinates. The shape of the array is (n,m,2), where n and m are the number of pixels in the first and second dimension, respectively. The last dimension is for x and y coordinates.
    meanlon : float
        Longitude of the center of the azimuthal equidistant projection in degrees.
    meanlat : float
        Latitude of the center of the azimuthal equidistant projection in degrees.

    Returns
    -------
    lonlat : numpy.ndarray
        Longitude and latitude in degrees. The shape of the array is (n,m,2), where n and m are the number of pixels in the first and second dimension, respectively. The last dimension is for longitude and latitude.

    Example
    -----------------
    >>> import numpy as np
    >>> from pybdshadow import utils
    >>> proj_coords = proj_coords = np.array(
        [[[-48243.5939812 , -55322.02388971],
          [ 47752.57582735,  55538.86412435]],
         [[-48243.5939812 , -55322.02388971],
          [ 47752.57582735,  55538.86412435]]])
    >>> lonlat = utils.aeqd2lonlat(proj_coords,120.5,30.5)
    >>> lonlat
    array([[[120.,  30.],
            [121.,  31.]],
           [[120.,  30.],
            [121.,  31.]]])
    '''

    epsg = CRS.from_proj4("+proj=aeqd +lat_0="+str(meanlat)+" +lon_0="+str(meanlon)+" +datum=WGS84")
    transformer = Transformer.from_crs( epsg,"EPSG:4326",always_xy = True)
    lonlat = transformer.transform(proj_coords[:,:,0], proj_coords[:,:,1])
    lonlat = np.array(lonlat).transpose([1,2,0])
    return lonlat

def calculate_normal(points):
    points = np.array(points)
    if points.shape[0] < 3:
        raise ValueError("墙至少需要三个点。")

    for i in range(points.shape[0]):
        for j in range(i + 1, points.shape[0]):
            for k in range(j + 1, points.shape[0]):
                vector1 = points[j] - points[i]
                vector2 = points[k] - points[i]
                normal = np.cross(vector1, vector2)
                if np.linalg.norm(normal) != 0:
                    return normal / np.linalg.norm(normal)

    raise ValueError("该墙所有点共线，无法计算法向量。")

def has_normal(points):
    # 将点列表转换为NumPy数组以便处理
    points = np.array(points)

    # 需要至少三个点来形成一个平面
    if points.shape[0] < 3:
        return False

    # 寻找不共线的三个点
    for i in range(points.shape[0]):
        for j in range(i+1, points.shape[0]):
            for k in range(j+1, points.shape[0]):
                # 计算两个向量
                vector1 = points[j] - points[i]
                vector2 = points[k] - points[i]

                # 计算叉乘
                normal = np.cross(vector1, vector2)

                # 检查法向量是否非零（即点不共线）
                if np.linalg.norm(normal) != 0:
                    # 返回归一化的法向量
                    return True
    return False

def count_overlapping_features(gdf,buffer = True):
    # 计算多边形的重叠次数
    if buffer:
        bounds = gdf.geometry.buffer(1e-9).exterior.unary_union
    else:
        bounds = gdf.geometry.exterior.unary_union

    new_polys = list(shapely.ops.polygonize(bounds))
    new_gdf = gpd.GeoDataFrame(geometry=new_polys)
    new_gdf['id'] = range(len(new_gdf))
    new_gdf_centroid = new_gdf.copy()
    new_gdf_centroid['geometry'] = new_gdf.geometry.representative_point()
    overlapcount = gpd.sjoin(new_gdf_centroid, gdf)
    overlapcount = overlapcount.groupby(
        ['id'])['index_right'].count().rename('count').reset_index()
    out_gdf = pd.merge(new_gdf, overlapcount)
    return out_gdf

def calculate_irradiance(row, lat, lon):
    """
    Calculate the solar irradiance for a given row with datetime.
    """
    site = location.Location(lat, lon)
    time = pd.DatetimeIndex([row['datetime']])  # 将单个时间点转换为DatetimeIndex

    # 计算太阳位置
    solar_position = site.get_solarposition(time)

    # 获取清晰天空模型的辐射
    clearsky = site.get_clearsky(time)
    

    return clearsky['ghi'].iloc[0]  # 返回全球水平辐照度(ghi)

def calculate_irradiance_gdf(gdf, lat, lon):
    """
    Calculate the solar irradiance for each row in a GeoDataFrame with a datetime.
    Assumes the GeoDataFrame has a column named 'datetime'.
    
    Parameters:
    gdf : GeoDataFrame
        The GeoDataFrame with a 'datetime' column.
    lat : float
        Latitude for the location.
    lon : float
        Longitude for the location.

    Returns:
    GeoDataFrame
        The input GeoDataFrame with added columns for solar position and clear sky data.
    """
    site = location.Location(lat, lon)

    # Convert the datetime column to a DatetimeIndex
    times = pd.DatetimeIndex(gdf['date'])

    # Calculate the solar position for all times
    solar_position = site.get_solarposition(times)

    # Get clear sky model irradiance for all times
    clearsky = site.get_clearsky(times)

    # Add the solar position and clear sky data to the GeoDataFrame
    for col in solar_position.columns:
        gdf['solar_' + col] = solar_position[col].values

    for col in clearsky.columns:
        gdf['clearsky_' + col] = clearsky[col].values

    return gdf

def calculate_3d_area_pro(arr):
    # 计算法线
    plane_norm = calculate_normal(arr)

    # 计算xz平面和yz平面的面积
    xz_poly = Polygon(arr[:, [0, 2]])
    xz_poly_area = xz_poly.area

    yz_poly = Polygon(arr[:, [1, 2]])
    yz_poly_area = yz_poly.area

    if xz_poly_area < yz_poly_area:
        # 选择yz平面
        yz_poly_area = yz_poly.area
        # x轴向量
        x_axis = np.array([1, 0, 0])
        # 计算法线与Z轴的夹角
        angle_with_y = np.arccos(np.clip(np.dot(plane_norm, x_axis) / np.linalg.norm(plane_norm), -1.0, 1.0))
        # 调整投影面积以得到三维空间中的实际面积
        area_3d = abs(yz_poly_area / np.cos(angle_with_y))
    else:
        # 选择xz平面
        xz_poly_area = xz_poly.area
        # x轴向量
        y_axis = np.array([0, 1, 0])
        # 计算法线与Z轴的夹角
        angle_with_y = np.arccos(np.clip(np.dot(plane_norm, y_axis) / np.linalg.norm(plane_norm), -1.0, 1.0))
        # 调整投影面积以得到三维空间中的实际面积
        area_3d = abs(xz_poly_area / np.cos(angle_with_y))
    return area_3d

def convert_buildings_to_aeqd(buildings_gdf, center_lon, center_lat):

    def convert_geometry_to_aeqd(geometry, transformer):
        if isinstance(geometry, Polygon):
            lonlat_coords = np.array(geometry.exterior.coords).reshape(1, -1, 2)
        elif isinstance(geometry, MultiPolygon):
            lonlat_coords = np.concatenate([np.array(poly.exterior.coords).reshape(1, -1, 2) for poly in geometry.geoms], axis=1)
        else:
            return geometry
    
        proj_coords = transformer.transform(lonlat_coords[:, :, 0], lonlat_coords[:, :, 1])
        proj_coords = np.array(proj_coords).transpose([1, 2, 0])
        return Polygon(np.squeeze(proj_coords))
    epsg = CRS.from_proj4("+proj=aeqd +lat_0=" + str(center_lat) + " +lon_0=" + str(center_lon) + " +datum=WGS84")
    transformer = Transformer.from_crs("EPSG:4326", epsg, always_xy=True)

    buildings_aeqd_gdf = buildings_gdf.copy()
    buildings_aeqd_gdf['geometry'] = buildings_gdf['geometry'].apply(lambda geom: convert_geometry_to_aeqd(geom, transformer))
    return buildings_aeqd_gdf