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
from shapely.geometry import Polygon, Point
import math
import numpy as np
from .preprocess import merge_shadow


def lonlat_mercator(lonlat):
    mercator = lonlat.copy()
    earthRad = 6378137.0
    mercator[0] = lonlat[0] * math.pi / 180 * earthRad  # 角度转弧度
    a = lonlat[1] * math.pi / 180  # 弧度制纬度
    mercator[1] = earthRad / 2 * \
        math.log((1.0 + math.sin(a)) / (1.0 - math.sin(a)))
    return mercator


def lonlat_mercator_vector(lonlat):
    mercator = np.zeros_like(lonlat)
    earthRad = 6378137.0
    mercator[:, :, 0] = lonlat[:, :, 0] * math.pi / 180 * earthRad  # 角度转弧度
    a = lonlat[:, :, 1] * math.pi / 180  # 弧度制纬度
    mercator[:, :, 1] = earthRad / 2 * \
        np.log((1.0 + np.sin(a)) / (1.0 - np.sin(a)))
    return mercator


def mercator_lonlat(mercator):
    lonlat = mercator.copy()
    lonlat[0] = mercator[0]/20037508.34*180
    temp = mercator[1]/20037508.34*180
    lonlat[1] = 180/math.pi * \
        (2*math.atan(math.exp(temp*math.pi/180)) - math.pi/2)  # 纬度的长度
    return lonlat


def mercator_lonlat_vector(mercator):
    lonlat = np.zeros_like(mercator)
    lonlat[:, :, 0] = mercator[:, :, 0]/20037508.34*180
    lonlat[:, :, 1] = mercator[:, :, 1]/20037508.34*180
    lonlat[:, :, 1] = 180/math.pi * \
        (2*np.arctan(np.exp(lonlat[:, :, 1]*math.pi/180)) - math.pi/2)

    return lonlat


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

# def mLonlat():


def bdshadow_sunlight(buildings, date, merge=True, height='height', ground=0):
    '''
    Calculate the sunlight shadow of the buildings.

    **Parameters**
    buildings : GeoDataFrame
        Buildings. coordinate system should be WGS84
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

    # calculate position
    lon1, lat1, lon2, lat2 = list(building.bounds.mean())
    lon = (lon1+lon2)/2
    lat = (lat1+lat2)/2

    # 测试坐标转换函数是否可行
    # points = gpd.GeoSeries([geometry.Point(lon,lat)],crs='EPSG:4326') # 指定坐标系为WGS 1984
    # points2 = points.to_crs(epsg=epsg) #用自带的函数计算
    # points1 = lonlat_mercator([lon,lat])#用自定义的函数计算
    # print("zidong",points2,points1)

    # obtain sun position
    sunPosition = get_position(date, lon, lat)
    buildingshadow = building.copy()

    a = buildingshadow['geometry'].apply(lambda r: list(r.exterior.coords))
    buildingshadow['wall'] = a
    buildingshadow = buildingshadow.set_index(['building_id'])
    a = buildingshadow.apply(lambda x: pd.Series(x['wall']), axis=1).unstack()
    walls = a[- a.isnull()].reset_index().sort_values(by=['building_id', 'level_0'])
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

    # calculate shadow for walls
    shadowShape = calSunShadow_vector(
        walls_shape, walls['height'].values, sunPosition)

    walls['geometry'] = list(shadowShape)
    walls['geometry'] = walls['geometry'].apply(lambda r: Polygon(r))
    walls = gpd.GeoDataFrame(walls)
    walls = pd.concat([walls, building])
    if merge:
        walls = merge_shadow(walls)

    return walls


'''
待开发功能:
1. 广告阴影计算
'''
# 用xyz表示，方向


def calPointLightShadow(shape, shapeHeight, pointLight):
    # 数据类型：numpy

    pointLightPosition = pointLight['position']
    #pointLightAngle = pointLight['angle']
    if pointLightPosition[2] < shapeHeight:
        pointLightPosition = shapeHeight + 0.001
    # 高度比
    scale = shapeHeight/(pointLightPosition - shapeHeight)

    shadowShape = []  # list
    for i in range(0, 2):
        vertex = shape[i]
        shadowShape.append(vertex)

    for i in range(2, 3):  # 计算建筑物的顶部点投影位置

        vertex = shape[3 - i]  # lon lat
        vertexToLightVector = vertex - pointLightPosition[0:1]

        shadowVertex = vertex + vertexToLightVector*scale
        shadowShape.append(shadowVertex)
    vertex = shadowShape[0]
    shadowShape.append(vertex)

    return shadowShape


# 用xyz表示，方向,numpy格式
def calPointLightShadow_vector(shape, shapeHeight, pointLight):
    # 多维数据类型：numpy
    # 输入的shape是一个矩阵（n*2*2) n个建筑物面，每个建筑有2个点，每个点有三个维度
    # shapeHeight(n) 每一栋建筑的高度都是一样的
    n = np.shape(shape)[0]
    pointLightPosition = pointLight['position']  # [lon,lat,height]

    # 高度比
    #scale[scale<=0] =1000
    diff = pointLightPosition[2] - shapeHeight
    scale = np.zeros(n)
    scale[diff != 0] = shapeHeight[diff != 0]/(diff[diff != 0])
    scale[scale <= 0] = 10  # n
    scale = scale.reshape((n, 1))

    shadowShape = np.zeros((n, 5, 2))

    shadowShape[:, 0:2, :] += shape  # 前两个点不变
    vertexToLightVector = shape - pointLightPosition[0:2]  # n,2,2

    shadowShape[:, 2, :] = shape[:, 1, :] + vertexToLightVector[:,
                                                                1, :]*scale  # [n,2,2] = [n,2,2]+[n,2,2]*n
    shadowShape[:, 3, :] = shape[:, 0, :] + vertexToLightVector[:, 0, :]*scale

    shadowShape[:, 4, :] = shadowShape[:, 0, :]

    return shadowShape


def bdshadow_pointlight(buildings, pointlon, pointlat, pointheight, merge=True, height='height', ground=0):
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

    # building to walls
    buildingshadow = building.copy()
    a = buildingshadow['geometry'].apply(lambda r: list(r.exterior.coords))
    buildingshadow['wall'] = a
    buildingshadow = buildingshadow.set_index(['building_id'])
    a = buildingshadow.apply(lambda x: pd.Series(x['wall']), axis=1).unstack()
    walls = a[- a.isnull()].reset_index().sort_values(by=['building_id', 'level_0'])
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

    # 在这里创建点光源
    pointLightPosition = {'position': [pointlon, pointlat, pointheight]}
    # calculate shadow for walls
    shadowShape = calPointLightShadow_vector(
        walls_shape, walls['height'].values, pointLightPosition)

    walls['geometry'] = list(shadowShape)
    walls['geometry'] = walls['geometry'].apply(lambda r: Polygon(r))
    walls = gpd.GeoDataFrame(walls)
    walls = pd.concat([walls, building])
    if merge:
        walls = merge_shadow(walls)

    return walls


def calOrientation(p1, p2):
    p1 = lonlat_mercator(p1)
    p2 = lonlat_mercator(p2)

    if p2[0] != p1[0]:
        k = (p2[1] - p1[1])/(p2[0] - p1[0])
        # print('k',k)
        if k == 0:
            k = 0.0000001
        k = -1/k
    else:
        k = 0
    # print('k',k)
    orientation = math.atan(k)
    if orientation < 0:
        orientation += math.pi
    return orientation


def initialVisualRange(brandCenter, orientation, xResolution=0.01, isAngle=True, eyeResolution=3, direction=1):
    # direction：广告牌的朝向，有1和-1两个枚举类型

    # 广告牌的位置，面向的角度，
    # print(orientation)
    brandCenterM = lonlat_mercator(brandCenter)
    # print(brandCenter,brandCenterM)

    if isAngle == True:
        eyeResolution = (eyeResolution / 60) / 60
        eyeResolution = (eyeResolution * math.pi) / 180  # 人眼分辨率，弧度

    D = xResolution / eyeResolution
    # 半径
    visualR = D / 2  # 单位m
    if visualR > brandCenter[2]:
        visualGroundR = math.sqrt(
            (math.pow(D, 2)) / 4 - (math.pow(brandCenterM[2], 2)))  # 地面上的可视化半径
    else:
        visualGroundR = 0

    visualCenter = [brandCenterM[0] - visualR * math.cos(orientation)*direction,
                    brandCenterM[1] - visualR * math.sin(orientation)*direction]

    # 生成可视区域面，原理就是对中心点取buffer构成圆
    visualArea_circle = Point(visualCenter).buffer(visualGroundR)
    # 再转为经纬度坐标系
    visualArea_circle = Polygon(mercator_lonlat_vector(
        np.array([visualArea_circle.exterior.coords]))[0])

    visualCenter = mercator_lonlat(visualCenter)

    visualArea = {
        'brandCenter': brandCenter,
        # 'visualR': visualR,
        'visualGroundR': visualGroundR,
        'visualCenter': visualCenter,
    }
    return visualArea, visualArea_circle


def ad_visualArea(ad_params, buildings=gpd.GeoDataFrame(), height='height'):
    '''
    Calculate visual area for advertisement.

    **Parameters**
    ad_params : dict
        Parameters of advertisement.
    buildings : GeoDataFrame
        Buildings. coordinate system should be WGS84
    height : string
        Column name of building height

    **Return**
    visualArea : GeoDataFrame
        Visual Area of the advertisement
    shadows : GeoDataFrame
        Building shadows
    '''
    if len(buildings) == 0:
        buildings['geometry'] = []
        buildings[height] = []

    if 'orientation' not in ad_params:
        ad_params['orientation'] = calOrientation(
            ad_params['point1']+[ad_params['height']], ad_params['point2']+[ad_params['height']])
    if 'brandCenter' not in ad_params:
        ad_params['brandCenter'] = list(
            (np.array(ad_params['point1'])+np.array(ad_params['point2']))/2)

    # calculate initial visualRange
    brandCenter = ad_params['brandCenter']
    _, visualArea_circle = initialVisualRange(
        ad_params['brandCenter']+[ad_params['height']], ad_params['orientation'])
    visualArea_circle = gpd.GeoDataFrame({'geometry': [visualArea_circle]})
    visualArea_circle.crs = buildings.crs

    # filter buildings inside visualRange
    ad_buildings = gpd.sjoin(buildings, visualArea_circle)

    # calculate building shadow
    shadows = bdshadow_pointlight(
        ad_buildings, brandCenter[0], brandCenter[1], ad_params['height'])

    # calculate visual area
    shadows.crs = visualArea_circle.crs
    visualArea = visualArea_circle.difference(
        gpd.clip(visualArea_circle, shadows))
    visualArea = gpd.GeoDataFrame(visualArea, columns=['geometry'])
    return visualArea, shadows
