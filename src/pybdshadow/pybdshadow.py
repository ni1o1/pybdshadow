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
from shapely.geometry import Polygon
import math
import numpy as np
# 读取shp格式的文件并保存

# 计算空间直线与平面的交点


def calLinePlaneIntersect(line, plane):
    p1 = line[0], p2 = line[1]
    p1D = plane[0] * p1[0] + plane[1] * p1[1] + plane[2] * p1[2] + plane[3]
    p1D2 = plane[0] * (p2[0] - p1[0]) + plane[1] * \
        (p2[1] - p1[1]) + plane[2] * (p2[2] - p1[2])
    m = abs(p1D / p1D2)

    #p2D = (plane[0] * p2[0] + plane[1] * p2[1] + plane[2] * p2[2] + plane[3])
    x = p1[0] - m * (p2[0] - p1[0])
    y = p1[1] - m * (p2[1] - p1[1])
    z = p1[2] - m * (p2[2] - p1[2])

    # if (isNaN(z)):
    # return null

    return [x, y, z]


def radianToAngle(radian):
    radian = radian*180/math.pi
    # if radian<0:
    #   radian += 360
    return radian


def angleToRadian(angle):
    angle = angle/180*math.pi
    # if radian<0:
    #   radian += 360
    return angle


def lineCrossMultiply(l1, l2, option="lineSegment"):
    if (option == "lineSegment"):
        # 根据两直线计算：前-后
        vectorL1 = [l1[0][0] - l1[1][0], l1[0]
                    [1] - l1[1][1], l1[0][2] - l1[1][2]]
        vectorL2 = [l2[0][0] - l2[1][0], l2[0]
                    [1] - l2[1][1], l2[0][2] - l2[1][2]]

        # 计算叉乘
        A = vectorL1[1] * vectorL2[2] - vectorL2[1] * vectorL1[2]
        B = vectorL2[0] * vectorL1[2] - vectorL1[0] * vectorL2[2]
        C = vectorL1[0] * vectorL2[1] - vectorL2[0] * vectorL1[1]

    elif (option == "vector"):
        A = l1[1] * l2[2] - l2[1] * l1[2]
        B = l2[0] * l1[2] - l1[0] * l2[2]
        C = l1[0] * l2[1] - l2[0] * l1[1]

    return [A, B, C, A + B + C]


def calPlaneByTwoVectors(n1, n2, p):
    n = lineCrossMultiply(n1, n2, "vector")
    n.splice(3, 1)
    D = -n[0] * p[0] - n[1] * p[1] - n[2] * p[2]
    n.push(D)
    return n


# 计算每个面的阴影
# shape的格式：两个平面点组成的列表
def calSunShadow(shape, shapeHeight, sunPosition):
    azimuth = (sunPosition['azimuth'])
    altitude = (sunPosition['altitude'])
    symbol = [1, -1]  # 经度，纬度的符号

    if azimuth < 0:
        azimuth += math.pi
        symbol[0] *= -1

    distance = shapeHeight/math.tan(altitude)

    # 计算投影位置偏移
    lonDistance = symbol[0]*distance*math.sin(azimuth)
    latDistance = symbol[1]*distance*math.cos(azimuth)

    shadowShape = []
    for i in range(0, 2):
        vertex = shape[i]
        # vertex.append(0)
        shadowShape.append(vertex)

    for i in range(2, 4):  # 计算建筑物的顶部点投影位置
        vertex = shape[3-i]
        shadowVertexLon = vertex[0] + lonDistance  # 经度
        shadowVertexLat = vertex[1] + latDistance  # 纬度
        shadowShape.append([shadowVertexLon, shadowVertexLat])
    vertex = shadowShape[0]
    shadowShape.append(vertex)

    return shadowShape


# 多维数据类型：numpy
# 输入的shape是一个矩阵（n*2*2) n个建筑物面，每个建筑有2个点，每个点有三个维度
# shapeHeight(n) 每一栋建筑的高度都是一样的
def calSunShadow1(shape, shapeHeight, sunPosition):
    azimuth = (sunPosition['azimuth'])
    altitude = (sunPosition['altitude'])
    symbol = [1, -1]  # 经度，纬度的符号

    if azimuth < 0:
        azimuth += math.pi
        symbol[0] *= -1

    distance = shapeHeight/math.tan(altitude)

    # 计算投影位置偏移
    lonDistance = symbol[0]*distance*math.sin(azimuth)  # n个偏移量[n]
    latDistance = symbol[1]*distance*math.cos(azimuth)

    n = np.shape(shape)[0]
    shadowShape = np.zeros(n, 5, 2)  # n个建筑物面，每个面都有5个点，每个点都有个维数

    shadowShape[:, 0:1, :] += shape  # 前两个点不变
    shadowShape[:, 2:3, 0] += shape + lonDistance
    shadowShape[:, 2:3, 1] += shape + latDistance
    temp = shadowShape[:, 3, :]
    shadowShape[:, 3, :] = shadowShape[:, 2, :]
    shadowShape[:, 2, :] = temp

    shadowShape[:, 4, :] = shadowShape[:, 0, :]

    return shadowShape[:, 0:1, :]


# 计算广告牌每个面的阴影
def calBdShadow(shape, shapeHeight, bdPosition, visualArea):

    visualGroundR = visualArea['visualGroundR']
    bdHeight = bdPosition[2]
    groundPlane = [0, 0, 1, 0]
    shadowShape = []
    for i in range(0, 2):
        vertex = shape[i]
        # vertex.append(0)
        shadowShape.append(vertex)

    for i in range(2, 3):  # 计算建筑物的顶部点投影位置

        # 如果太阳高度比较高
        if bdHeight < shapeHeight:
            bdHeight = shapeHeight+0.1
        vertex = shape[i]
        vertex.append(shapeHeight)
        shadowVertex = calLinePlaneIntersect(
            [bdHeight, shape[i]], groundPlane)  # 计算投影点
        shadowShape.append(shadowVertex[0:1])
    vertex = shadowShape[0]
    shadowShape.append(vertex)

    return shadowVertex


def singlebdshadow_sunlight(building, height, sunPosition):
    '''
    Calculate the sunlight shadow of a single building. The input data should be in
    projection coordinate system


    **Parameters**
    building : shapely.geometry.Polygon
        Building. coordinate system should be projection coordinate system
    height : string
        Building height
    sunPosition : dict
        Sun position calculated by suncalc

    **Return**
    shadow : shapely.geometry.Polygon
        Building shadow geometry
    '''
    wall = pd.DataFrame(list(building.exterior.coords), columns=['x1', 'y1'])
    wall['x2'] = wall['x1'].shift(-1)
    wall['y2'] = wall['y1'].shift(-1)
    wall['height'] = height
    wall = wall.iloc[:-1]
    wall['geometry'] = wall.apply(lambda r: Polygon(calSunShadow(
        [[r['x1'], r['y1']], [r['x2'], r['y2']]], r['height'], sunPosition)), axis=1)
    shadow = gpd.GeoSeries(list(wall['geometry'])+[building]).unary_union
    return shadow


def bdshadow_sunlight(buildings, date, height='height', ground=0, epsg=3857):
    '''
    Calculate the sunlight shadow of the buildings.

    **Parameters**
    buildings : GeoDataFrame
        Buildings. coordinate system should be WGS84
    date : datetime
        Datetime
    height : string
        Column name of building height
    ground : number
        Height of the ground
    epsg : number
        epsg code of the projection coordinate system

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
    # transform coordinate system
    building.crs = 'epsg:4326'
    building = building.to_crs(epsg=epsg)
    # obtain sun position
    sunPosition = get_position(date, lon, lat)
    buildingshadow = building.copy()
    buildingshadow['geometry'] = building.apply(
        lambda r: singlebdshadow_sunlight(r['geometry'], r[height], sunPosition), axis=1)
    # transform coordinate system back to wgs84
    shadows = buildingshadow.to_crs(epsg=4326)
    return shadows
