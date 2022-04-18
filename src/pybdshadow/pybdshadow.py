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
import pandas as pd
import geopandas as gpd
from suncalc import get_position
from shapely.geometry import Polygon, MultiPolygon
import math
import numpy as np
from .utils import (
    lonlat_mercator_vector,
    mercator_lonlat_vector
)
from .preprocess import gdf_difference,gdf_intersect


def calSunShadow_vector(shape, shapeHeight, sunPosition):
    # 多维数据类型：numpy
    # 输入的shape是一个矩阵（n*2*2) n个建筑物面，每个建筑有2个点，每个点有三个维度
    # shapeHeight(n) 每一栋建筑的高度都是一样的

    # 坐标系转换transform coordinate system
    shape = lonlat_mercator_vector(shape)
    # print(shape,np.shape(shape))

    azimuth = sunPosition['azimuth']
    altitude = sunPosition['altitude']

    n = np.shape(shape)[0]
    distance = shapeHeight/math.tan(altitude)

    # 计算投影位置偏移
    lonDistance = distance*math.sin(azimuth)  # n个偏移量[n]
    lonDistance = lonDistance.reshape((n, 1))
    latDistance = distance*math.cos(azimuth)
    latDistance = latDistance.reshape((n, 1))

    shadowShape = np.zeros((n, 5, 2))  # n个建筑物面，每个面都有5个点，每个点都有个维数

    shadowShape[:, 0:2, :] += shape  # 前两个点不变
    shadowShape[:, 2:4, 0] = shape[:, :, 0] + lonDistance
    shadowShape[:, 2:4, 1] = shape[:, :, 1] + latDistance

    shadowShape[:, [2, 3], :] = shadowShape[:, [3, 2], :]
    shadowShape[:, 4, :] = shadowShape[:, 0, :]

    shadowShape = mercator_lonlat_vector(shadowShape)
    # print(shadowShape,np.shape(shadowShape))
    return shadowShape


def bdshadow_sunlight(buildings, date,  height='height', roof=False,include_building = True,ground=0):
    '''
    Calculate the sunlight shadow of the buildings.

    **Parameters**

    buildings : GeoDataFrame
        Buildings. coordinate system should be WGS84
    date : datetime
        Datetime
    height : string
        Column name of building height
    roof : bool
        whether to calculate the roof shadows
    include_building : bool
        whether the shadow include building outline
    ground : number
        Height of the ground

    **Return**

    shadows : GeoDataFrame
        Building shadow
    '''

    building = buildings.copy()

    building[height] -= ground
    building = building[building[height] > 0]

    # calculate position
    lon1, lat1, lon2, lat2 = list(building.bounds.mean())
    lon = (lon1+lon2)/2
    lat = (lat1+lat2)/2

    # obtain sun position
    sunPosition = get_position(date, lon, lat)
    buildingshadow = building.copy()

    a = buildingshadow['geometry'].apply(lambda r: list(r.exterior.coords))
    buildingshadow['wall'] = a
    buildingshadow = buildingshadow.set_index(['building_id'])
    a = buildingshadow.apply(lambda x: pd.Series(x['wall']), axis=1).unstack()
    walls = a[- a.isnull()].reset_index().sort_values(
        by=['building_id', 'level_0'])
    walls = pd.merge(walls, buildingshadow['height'].reset_index())
    walls['x1'] = walls[0].apply(lambda r: r[0])
    walls['y1'] = walls[0].apply(lambda r: r[1])
    walls['x2'] = walls['x1'].shift(-1)
    walls['y2'] = walls['y1'].shift(-1)
    walls = walls[walls['building_id'] == walls['building_id'].shift(-1)]
    walls = walls[['x1', 'y1', 'x2', 'y2', 'building_id', 'height']]
    walls['wall'] = walls.apply(lambda r: [[r['x1'], r['y1']],
                                           [r['x2'], r['y2']]], axis=1)

    ground_shadow = walls.copy()
    walls_shape = np.array(list(ground_shadow['wall']))

    # calculate shadow for walls
    shadowShape = calSunShadow_vector(
        walls_shape, ground_shadow['height'].values, sunPosition)

    ground_shadow['geometry'] = list(shadowShape)
    ground_shadow['geometry'] = ground_shadow['geometry'].apply(
        lambda r: Polygon(r))
    ground_shadow = gpd.GeoDataFrame(ground_shadow)



    ground_shadow = pd.concat([ground_shadow, building])
    ground_shadow = ground_shadow.groupby(['building_id'])['geometry'].apply(
        lambda df: MultiPolygon(list(df)).buffer(0)).reset_index()
    
    ground_shadow['height'] = 0
    ground_shadow['type'] = 'ground'

    if not roof:
        if not include_building:
            #从地面阴影裁剪建筑轮廓
            ground_shadow = gdf_difference(ground_shadow,buildings)
        return ground_shadow
    else:
        def calwall_shadow(walldata, building):
            walls = walldata.copy()
            walls_shape = np.array(list(walls['wall']))
            # calculate shadow for walls
            shadowShape = calSunShadow_vector(
                walls_shape, walls['height'].values, sunPosition)
            walls['geometry'] = list(shadowShape)
            walls['geometry'] = walls['geometry'].apply(lambda r: Polygon(r))
            walls = gpd.GeoDataFrame(walls)
            walls = pd.concat([walls, building])

            walls = walls.groupby(['building_id'])['geometry'].apply(
                lambda df: MultiPolygon(list(df)).buffer(0)).reset_index()
            return walls

        # 计算屋顶阴影
        roof_shadows = []
        for roof_height in walls[height].drop_duplicates():
            # 高于给定高度的墙
            walls_high = walls[walls[height] > roof_height].copy()
            if len(walls_high) == 0:
                continue
            walls_high[height] -= roof_height
            # 高于给定高度的建筑
            building_high = building[building[height] > roof_height].copy()
            if len(building_high) == 0:
                continue
            building_high[height] -= roof_height
            # 所有建筑在此高度的阴影
            building_shadow_height = calwall_shadow(walls_high, building_high)
            # 在此高度的建筑屋顶
            building_roof = building[building[height] == roof_height].copy()
            building_shadow_height.crs = building_roof.crs
            # 取有遮挡的阴影
            building_shadow_height = gpd.sjoin(
                building_shadow_height, building_roof)
            if len(building_shadow_height) == 0:
                continue
            # 与屋顶做交集
            building_roof = gdf_intersect(building_roof,building_shadow_height)

            # 再减去这个高度以上的建筑
            building_higher = building[building[height] > roof_height].copy()
            building_roof = gdf_difference(building_roof,building_higher)
            
            #给出高度信息
            building_roof['height'] = roof_height
            building_roof = building_roof[-building_roof['geometry'].is_empty]

            roof_shadows.append(building_roof)
        if len(roof_shadows) == 0:
            roof_shadow = gpd.GeoDataFrame()
        else:
            roof_shadow = pd.concat(roof_shadows)[
                ['height', 'building_id', 'geometry']]
            roof_shadow['type'] = 'roof'

        if not include_building:
            #从地面阴影裁剪建筑轮廓
            ground_shadow = gdf_difference(ground_shadow,buildings)
        
        shadows = pd.concat([roof_shadow, ground_shadow])
        shadows.crs = None
        shadows['geometry'] = shadows.buffer(0.000001).buffer(-0.000001)
        return shadows


def calPointLightShadow_vector(shape, shapeHeight, pointLight):
    # 多维数据类型：numpy
    # 输入的shape是一个矩阵（n*2*2) n个建筑物面，每个建筑有2个点，每个点有三个维度
    # shapeHeight(n) 每一栋建筑的高度都是一样的
    n = np.shape(shape)[0]
    pointLightPosition = pointLight['position']  # [lon,lat,height]

    # 高度比
    diff = pointLightPosition[2] - shapeHeight
    scale = np.zeros(n)
    scale[diff != 0] = shapeHeight[diff != 0]/(diff[diff != 0])
    scale[scale <= 0] = 10  # n
    scale = scale.reshape((n, 1))

    shadowShape = np.zeros((n, 5, 2))

    shadowShape[:, 0:2, :] += shape  # 前两个点不变
    vertexToLightVector = shape - pointLightPosition[0:2]  # n,2,2

    shadowShape[:, 2, :] = shape[:, 1, :] + \
        vertexToLightVector[:, 1, :]*scale  # [n,2,2] = [n,2,2]+[n,2,2]*n
    shadowShape[:, 3, :] = shape[:, 0, :] + \
        vertexToLightVector[:, 0, :]*scale

    shadowShape[:, 4, :] = shadowShape[:, 0, :]

    return shadowShape


def bdshadow_pointlight(buildings,
                        pointlon,
                        pointlat,
                        pointheight,
                        merge=True,
                        height='height',
                        ground=0):
    '''
    Calculate the sunlight shadow of the buildings.

    **Parameters**
    
    buildings : GeoDataFrame
        Buildings. coordinate system should be WGS84
    pointlon,pointlat,pointheight : float
        Point light coordinates and height
    date : datetime
        Datetime
    merge : bool
        whether to merge the wall shadows into the building shadows
    height : string
        Column name of building height
    ground : number
        Height of the ground

    **Return**

    shadows : GeoDataFrame
        Building shadow
    '''

    building = buildings.copy()

    building[height] -= ground
    building = building[building[height] > 0]

    if len(building) == 0:
        walls = gpd.GeoDataFrame()
        walls['geometry'] = []
        walls['building_id'] = []
        return walls
    # building to walls
    buildingshadow = building.copy()

    a = buildingshadow['geometry'].apply(lambda r: list(r.exterior.coords))
    buildingshadow['wall'] = a
    buildingshadow = buildingshadow.set_index(['building_id'])
    a = buildingshadow.apply(lambda x: pd.Series(x['wall']), axis=1).unstack()
    walls = a[- a.isnull()].reset_index().sort_values(
        by=['building_id', 'level_0'])
    walls = pd.merge(walls, buildingshadow['height'].reset_index())
    walls['x1'] = walls[0].apply(lambda r: r[0])
    walls['y1'] = walls[0].apply(lambda r: r[1])
    walls['x2'] = walls['x1'].shift(-1)
    walls['y2'] = walls['y1'].shift(-1)
    walls = walls[walls['building_id'] == walls['building_id'].shift(-1)]
    walls = walls[['x1', 'y1', 'x2', 'y2', 'building_id', 'height']]
    walls['wall'] = walls.apply(lambda r: [[r['x1'], r['y1']],
                                           [r['x2'], r['y2']]], axis=1)
    walls_shape = np.array(list(walls['wall']))

    # Create point light
    pointLightPosition = {'position': [pointlon, pointlat, pointheight]}
    # calculate shadow for walls
    shadowShape = calPointLightShadow_vector(
        walls_shape, walls['height'].values, pointLightPosition)

    walls['geometry'] = list(shadowShape)
    walls['geometry'] = walls['geometry'].apply(lambda r: Polygon(r))
    walls = gpd.GeoDataFrame(walls)
    walls = pd.concat([walls, building])
    if merge:
        walls = walls.groupby(['building_id'])['geometry'].apply(
            lambda df: MultiPolygon(list(df)).buffer(0)).reset_index()

    return walls
