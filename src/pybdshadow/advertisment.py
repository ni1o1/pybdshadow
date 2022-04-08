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

import geopandas as gpd
from shapely.geometry import Polygon, Point
import math
import numpy as np
from .utils import  (
    lonlat_mercator,
    lonlat_mercator_vector,
    mercator_lonlat,
    mercator_lonlat_vector
    )
from .pybdshadow import bdshadow_pointlight

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
