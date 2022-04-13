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
from shapely.geometry import Polygon, Point
import math
import numpy as np
from .utils import (
    lonlat_mercator,
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


def initialVisualRange(brandCenter,
                       orientation,
                       xResolution=0.01,
                       isAngle=True,
                       eyeResolution=3,
                       direction=1):
    # direction：广告牌的朝向，有1和-1两个枚举类型

    # 广告牌的位置，面向的角度，
    # print(orientation)
    brandCenterM = lonlat_mercator(brandCenter)
    # print(brandCenter,brandCenterM)

    if isAngle:
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

    visualCenter = [
        brandCenterM[0] - visualR * math.cos(orientation)*direction,
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


def ad_to_gdf(ad_params, billboard_height=10, billboard_witdh=20):
    '''
    Generate a GeoDataFrame from ad_params for visualization.

    **Parameters**
    ad_params : dict
        Parameters of advertisement.
    billboard_height : number
        The height of the billboard.
    billboard_witdh : number
        Default witdh of the billboard.


    **Return**
    ad_gdf : GeoDataFrame
        advertisment GeoDataFrame
    '''
    ad_gdf = []
    width = 0.02
    gap = 0.000001
    if ('point1' in ad_params) & ('point2' in ad_params):
        adp1 = ad_params['point1']
        adp2 = ad_params['point2']
    if 'brandCenter' in ad_params:
        brandCenter = ad_params['brandCenter'][:2]
        orientation = ad_params['orientation']
        adp1 = mercator_lonlat(
            lonlat_mercator(brandCenter) +
            np.array([math.sin(math.pi-orientation),
                      math.cos(math.pi-orientation)])*billboard_witdh)
        adp2 = mercator_lonlat(
            lonlat_mercator(brandCenter) -
            np.array([math.sin(math.pi-orientation),
                      math.cos(math.pi-orientation)])*billboard_witdh)

    billboard_gdf = gpd.GeoDataFrame(
        {'geometry': [
            Polygon(
                [[adp1[0],
                    adp1[1],
                    ad_params['height']],
                    [adp1[0]+gap,
                     adp1[1]+gap,
                     ad_params['height']+billboard_height],
                    [adp2[0]+gap,
                        adp2[1]+gap,
                     ad_params['height']+billboard_height],
                    [adp2[0],
                        adp2[1],
                        ad_params['height']]]),
            Polygon(
                [
                    [(adp1[0] + adp2[0]) / 2 - width/2000 - gap,
                     (adp1[1] + adp2[1]) / 2 - width / 2000 - gap,
                        ad_params['height']],
                    [width/2000 + (adp1[0] + adp2[0]) / 2 - gap,
                     width/2000 + (adp1[1] + adp2[1]) / 2 - gap,
                        ad_params['height']],
                    [width/2000 + (adp1[0] + adp2[0]) / 2,
                        width/2000 + (adp1[1] + adp2[1]) / 2,
                        0],
                    [(adp1[0] + adp2[0]) / 2 - width/2000,
                        (adp1[1] + adp2[1]) / 2 - width / 2000,
                        0],
                ]
            ), ]})
    ad_gdf.append(billboard_gdf)

    ad_gdf = gpd.GeoDataFrame(pd.concat(ad_gdf))
    return ad_gdf


def ad_visualArea(ad_params,
                  buildings=gpd.GeoDataFrame(),
                  height='height',
                  xResolution=0.01,
                  eyeResolution=3):
    '''
    Calculate visual area for advertisement.

    **Parameters**
    ad_params : dict
        Parameters of advertisement.
    buildings : GeoDataFrame
        Buildings. coordinate system should be WGS84
    height : string
        Column name of building height
    xResolution, eyeResolution : number
        Resolution of advertisement and eye

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
            ad_params['point1']+[ad_params['height']],
            ad_params['point2']+[ad_params['height']])
    if 'brandCenter' not in ad_params:
        ad_params['brandCenter'] = list(
            (np.array(ad_params['point1'])+np.array(ad_params['point2']))/2)

    # calculate initial visualRange
    brandCenter = ad_params['brandCenter']
    _, visualArea_circle = initialVisualRange(
        ad_params['brandCenter']+[ad_params['height']],
        ad_params['orientation'],
        xResolution=xResolution,
        eyeResolution=eyeResolution)
    visualArea_circle = gpd.GeoDataFrame({'geometry': [visualArea_circle]})
    visualArea_circle.crs = buildings.crs

    # filter buildings inside visualRange
    ad_buildings = gpd.sjoin(buildings, visualArea_circle)

    # calculate building shadow
    shadows = bdshadow_pointlight(
        ad_buildings, brandCenter[0], brandCenter[1], ad_params['height'])

    if len(shadows) == 0:
        return visualArea_circle, shadows
    # calculate visual area
    shadows.crs = visualArea_circle.crs
    visualArea = visualArea_circle.difference(
        gpd.clip(visualArea_circle, shadows))
    visualArea = gpd.GeoDataFrame(visualArea, columns=['geometry'])
    return visualArea, shadows


'''
广告选址的优化算法
目前优化的参数是方向，高度，经度，纬度，四个参数
两个分辨率参数还没有考虑，这个可能需要再考虑
'''


def ad_optimize(bounds,
                buildings,
                height_range=[0, 100],
                multiplier=[0.01, 0.001],
                printlog=True,
                size_pop=10,
                max_iter=30,
                prob_mut=0.001,
                precision=1e-7):
    '''
    Optimize advertisment parameters using Genetic Algorithm

    **Parameters**

    bounds : list
        Area bounds, should be [lon1,lat1,lon2,lat2]
    buildings : GeoDataFrame
        Buildings. coordinate system should be WGS84
    height_range : list
        Height range of advertisment [minheight,maxheight]
    multiplier : list
        Multiplier for orientation and height
    printlog : bool
        Whether to print the optimization information of Genetic Algorithm
    size_pop,max_iter,prob_mut,precision :
        Parameters of Genetic Algorithm

    **Return**

    ad_params : dict
        Optimized advertisment parameters
    '''

    try:
        from sko.GA import GA
    except ImportError:
        raise ImportError(
            "Please install scikit-opt, run following code "
            "in cmd: pip install scikit-opt")

    # 遗传算法的目标函数，面积最大
    def optimize_func(p):
        ad_params = {'orientation': p[0]/multiplier[0],
                     'height': p[1]/multiplier[1],
                     'brandCenter': [p[2], p[3]]}
        # 计算可视面积
        visualArea, shadows = ad_visualArea(
            ad_params, buildings)  # 两个分辨率参数还没有考虑，这个可能需要再考虑
        if visualArea['geometry'].isnull().iloc[0]:
            return 0
        visualArea.crs = 'epsg:4326'
        area = visualArea.to_crs(epsg=2381)['geometry'].iloc[0].area
        return -area  # 面积作为目标函数，GA求的是目标函数最小值

    import math
    ga = GA(func=optimize_func,
            n_dim=4,  # 方向，高度，经度，纬度，四个参数，引入两个乘子让四个参数尽可能在同一量级上优化
            size_pop=size_pop,
            max_iter=max_iter,
            prob_mut=prob_mut,
            lb=[0,  # 四个参数的下边界
                height_range[0]*multiplier[1],
                bounds[0],
                bounds[1]],
            ub=[2*math.pi*multiplier[0],  # 四个参数的上边界
                height_range[1]*multiplier[1],
                bounds[2],
                bounds[3]],
            precision=precision)
    result = ga.run()
    p = result[0]

    # 重构广告参数
    ad_params = {'orientation': p[0]/multiplier[0],
                 'height': p[1]/multiplier[1],
                 'brandCenter': [p[2], p[3]]}

    # 绘制算法的优化过程
    if printlog:
        import pandas as pd
        import matplotlib.pyplot as plt
        Y_history = pd.DataFrame(ga.all_history_Y)
        _, ax = plt.subplots(2, 1)
        ax[0].plot(Y_history.index, -Y_history.values, '.', color='red')
        (-Y_history.min(axis=1).cummin()).plot(kind='line')
        plt.ylabel('Visual area($m^2$)')
        plt.xlabel('Iters')
        plt.show()

    return ad_params
