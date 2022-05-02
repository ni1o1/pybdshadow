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
from shapely.geometry import Polygon,LineString, MultiPolygon
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
                gpd.GeoDataFrame(building_shadow_height), gpd.GeoDataFrame(building_roof))
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

    a = buildingshadow['geometry'].apply(lambda r: list(r.exterior.coords))  #裸格式的几何
    buildingshadow['wall'] = a  #
    #print(a[0])
    buildingshadow = buildingshadow.set_index(['building_id']) #设置阴影所对应的id
    a = buildingshadow.apply(lambda x: pd.Series(x['wall']), axis=1).unstack()  #压缩为一个数组
    walls = a[- a.isnull()].reset_index().sort_values(
        by=['building_id', 'level_0'])  #重新排序
    walls = pd.merge(walls, buildingshadow['height'].reset_index())#与高度融合
    
    walls['x1'] = walls[0].apply(lambda r: r[0])  #
    walls['y1'] = walls[0].apply(lambda r: r[1])
    walls['x2'] = walls['x1'].shift(-1)  #向量中的序号全部向前提了一个
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

    walls['geometry'] = list(shadowShape)  #阴影存储
    walls['geometry'] = walls['geometry'].apply(lambda r: Polygon(r))  #将numpy转换成polygon形式
    walls = gpd.GeoDataFrame(walls)  #8列 x1 ， y1 ，x2 ， y2 ， building_id ， height ，  wall ，shadow 
    wallsBuilding = pd.concat([walls, building]) #
    #print(wallsBuilding)
    if merge:
        wallsBuilding = wallsBuilding.groupby(['building_id'])['geometry'].apply(
            lambda df: MultiPolygon(list(df)).buffer(0)).reset_index()
        #print(wallsBuilding)

    return [walls,wallsBuilding]
''' 
#=======================================================================================

#Calculate building shadow for point light

#Enter two points to calculate the general equation of the line：Ax+By+C = 0
def calLine(p1, p2): 
    
    A = p2[1] - p1[1]
    B = p1[0] - p2[0]
    C = p2[0] * p1[1] - p1[0] * p2[1] 
    
    return [A, B, C]

#Calculate the point of intersection of straight lines
def calCross2DLine_Geo(l1, l2):
    
    l1A = l1.apply(lambda r: r[0])
    l1B = l1.apply(lambda r: r[1])
    l1C = l1.apply(lambda r: r[2])
    l2A = l2.apply(lambda r: r[0])
    l2B = l2.apply(lambda r: r[1])
    l2C = l2.apply(lambda r: r[2])
    cross = gpd.GeoDataFrame()
    
    #x = (c2 * b1 - c1 * b2) / (a1 * b2 - a2 * b1)S
    cross['lon'] = (l2C * l1B - l1C * l2B) / (l1A * l2B - l2A * l1B)
    #corss['lon'] = corss[- corss.isnull()]
    
    #y = (c1 * a2 - c2 * a1) / (a1 * b2 - a2 * b1)
    cross['lat'] = (l1C * l2A - l2C * l1A) / (l1A * l2B - l2A * l1B)
    cross['lonlat'] = cross.apply(lambda r: [r['lon'], r['lat']], axis=1)
    return cross['lonlat']

#Calculate the point of intersection of straight lines：(numpy)
def calCross2DLine1(l1, l2):
  
    n = np.shape(l1)[0]
    cross = np.zeros((n,2))
    #x = (c2 * b1 - c1 * b2) / (a1 * b2 - a2 * b1)
    cross[:,0] = (l2[:,2] * l1[:,1] - l1[:,2] * l2[:,1]) / (l1[:,0] * l2[:,1] - l2[:,0] * l1[:,1])
    #y = (c1 * a2 - c2 * a1) / (a1 * b2 - a2 * b1)
    cross[:,1] = (l1[:,2] * l2[:,0] - l2[:,2] * l1[:,0]) / (l1[:,0] * l2[:,1] - l2[:,0] * l1[:,1])

    return cross

#Calculate the vector formed by two straight lines
def calVector2(p1,p2):
    return  [p1[0] - p2[0], p1[1] - p2[1]]

def vecDotMultiply(v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1]

def vecDotMultiply_Geo(v1,v2):
    vDot = gpd.GeoDataFrame()
    vDot['v1'] = v1
    vDot['v2'] = v2
    vDot['vDotRes'] = vDot.apply(lambda r : vecDotMultiply(r['v1'],r['v2']),axis=1)   
    return vDot['vDotRes']

def judgeDotSymbol(r,i):
    if r['crossPDot'] < 0:
        return r['beShelterWall'][1-i]
    else:
        return r['crossP']
    
def calDistance(p1,p2):  #输入两个点
    return math.sqrt((p2[0] - p1[0])*(p2[0] - p1[0])+(p2[1] - p1[1])*(p2[1] - p1[1]))

def calWallsShadow(pointLight,wallJoinShadow):
    #算shelterWall在beShelterWall上的投影
    #print(wallJoinShadow)

    shelterWall = wallJoinShadow['wall']
    shelterHeight = wallJoinShadow['height']
    beShelterWall = wallJoinShadow['beShelterWall']
    
    pointLightPosition = pointLight['position']
    
    #计算被遮挡面所在直线
    pBeShelterWall = beShelterWall.apply(lambda r: [r[0],r[1]])
    lBeShelterWall = pBeShelterWall.apply(lambda r: calLine(r[0], r[1]))
    shadow = gpd.GeoDataFrame()
    shadow['beShelterWall'] = beShelterWall
    shadow['beShelterHeight'] = wallJoinShadow['beShelterHeight']
    shadow['beShelterIndex'] = wallJoinShadow['index_right']
        
    for i in range(2):
        #计算中心点与遮挡面上的点构成的直线
        p = shelterWall.apply(lambda r: [r[i],pointLightPosition[0:2]])#exterior.
        l = p.apply(lambda r: calLine(r[0], r[1]))#

        shadowPoint = gpd.GeoDataFrame()
        shadowPoint['shelterWall'] = shelterWall
        shadowPoint['beShelterWall'] = beShelterWall
        shadowPoint['shelterHeight'] = shelterHeight
        
        shadowPoint['crossP'] = calCross2DLine_Geo(l, lBeShelterWall)  #射线与投影面的交点
        ##另一种形式：使用numpy矩阵求交点，结果相同
        #l1Numpy = np.array(list(l1))
        #lBeShelterWallNumpy = np.array(list(lBeShelterWall))
        #cross = calCross2DLine1(l1Numpy, lBeShelterWallNumpy)
    
        #通过向量点乘结果判断相交位置
        v = shelterWall.apply(lambda r: calVector2(r[i],pointLightPosition[0:2]))
        vShadow = shadowPoint['crossP'].apply(lambda r: calVector2(r,pointLightPosition[0:2]))
        shadowPoint['crossPDot'] = vecDotMultiply_Geo(v,vShadow)
        shadowPoint['point'] = shadowPoint.apply(lambda r: judgeDotSymbol(r,i),axis = 1)
        #print(shadowPoint['point'])
        
        #高度的比例
        shadowPoint['height'] = shadowPoint.apply(lambda r: r['shelterHeight']/calDistance(r['shelterWall'][i],pointLightPosition[0:2])
                              *calDistance(r['crossP'],pointLightPosition[0:2]),axis = 1)
        shadow['Point ' + str(i)] = shadowPoint['point']
        shadow['Height ' + str(i)] = shadowPoint['height']
    #print(shadow)                    
    return shadow

def convert3To2(point,originP,directP):
    #X = gpd.GeoDataFrame()
    x = calDistance(point,originP)
    v1 = [directP[0] - originP[0],directP[1] - originP[1]]
    v2 = [point[0] - originP[0],point[1] - originP[1]]
    if (vecDotMultiply(v1, v2)<0):
        x *= -1
    return x         

def getWallShape(shadow):
    shadow['beShelPointX'] =shadow.apply(lambda r:convert3To2(
        r['beShelterWall'][1],r['beShelterWall'][0],r['beShelterWall'][1]),axis = 1)
    shadow['beShelShape2'] = shadow.apply(lambda r:Polygon([[0.0,0.0],
                                                    [r['beShelPointX'],0.0],
                                                    [r['beShelPointX'],r['beShelterHeight']],
                                                    [0.0,r['beShelterHeight']],
                                                    [0.0,0.0]]),axis = 1)

    #print(shadow['beShelShape2']) 
    shadow['shelPointX1'] =shadow.apply(lambda r:convert3To2(
        r['Point 0'],r['beShelterWall'][0],r['beShelterWall'][1]),axis = 1)

    shadow['shelPointX2'] =shadow.apply(lambda r:convert3To2(
        r['Point 1'],r['beShelterWall'][0],r['beShelterWall'][1]),axis = 1)
    temp = shadow[-shadow['shelPointX1'].isnull()].copy()
    shadow = temp[-temp['shelPointX2'].isnull()].copy()
    shadow['shelShape2'] = shadow.apply(lambda r:Polygon([[r['shelPointX1'],0.0],
                                                  [r['shelPointX2'],0.0],
                                                  [r['shelPointX2'],r['Height 1']],
                                                  [r['shelPointX1'],r['Height 0']],
                                                  [r['shelPointX1'],0.0]]),axis = 1)
    #print(shadow['shelShape2'])
    return shadow


def decrease(p1,p2):
    return [p1[0] - p2[0],p1[1] - p2[1],calDistance(p1,p2)]

def calVisibleShape(shadow):    
    #print(shadow)
    beShelShape2 = gpd.GeoSeries(shadow['beShelShape2'])#[-shadow['beShelShape2'].isnull()]
    shelShape2 = gpd.GeoSeries(shadow['shelShape2'])
    shadow['diff'] = beShelShape2.difference(shelShape2, align=False)
    
    #area = shadow[shadow['diff'].area != 0]
    union = shadow.reset_index().sort_values(by=['beShelterIndex'])
    
    unionShapes = []
    beShelShapes = []
    origins = []
    directions = []
    for i in range(len(union)):   
        r = union.iloc[i]  #
        if (i!= 0) and (r['beShelterIndex'] == union.iloc[i-1]['beShelterIndex']):
            unionShapes[-1] = unionShape.union(r['diff'])
        else:
            #创建一个新的union
            unionShape = r['diff']
            unionShapes.append(unionShape)
            #被遮挡的shape
            #beShelShape = r['beShelShape2']
            beShelShapes.append(r['beShelShape2'])
            #原点
            origins.append(r['beShelterWall'][0])
            directions.append(decrease(r['beShelterWall'][1],r['beShelterWall'][0]))
       
        
    unionShapes = gpd.GeoSeries(unionShapes)#GeoSeries

    beShelShapes = gpd.GeoSeries(beShelShapes)
    visibleShapes = gpd.GeoDataFrame()
    visiShapes = beShelShapes.difference(unionShapes)
   
    visibleShapes['visiShapes'] = visiShapes#.apply(lambda r: list(r.exterior.coords))list
    visibleShapes['coordSysOrigins'] = origins 
    visibleShapes['coordSysDir'] = directions 
    #print(visibleShapes)
    
    #visibleShapes = visibleShapes[len(visibleShapes['visiShapes']) != 0]#.area
    visibleShapes = visibleShapes[visibleShapes['visiShapes'].area != 0]
    #print(visibleShapes)
    
    return visibleShapes

def convert2To3(r):
    results = []
    visiList = list(r['visiShapes'].exterior.coords)
    #print(visiList)
    for i in range(len(visiList)):
        x = r['coordSysOrigins'][0] + r['coordSysDir'][0] * (visiList[i][0] / r['coordSysDir'][2])
        y = r['coordSysOrigins'][1] + r['coordSysDir'][1] * (visiList[i][0] / r['coordSysDir'][2])
        results.append([x,y,visiList[i][1]])
    return results  

def calVisibleArea(wall,pointLight):
    
    wallsGeo = gpd.GeoDataFrame()
    wallsGeo['geometry'] = wall['wall'].apply(lambda r: LineString(r))  #几何图形对应的阴影
    wallsGeo['beShelterWall'] = wall['wall']#几何图形对应的地面坐标
    wallsGeo['beShelterHeight'] = wall['height']#几何图形对应的高度

    wallJoinShadow = gpd.sjoin(wall,wallsGeo)  #wall遮挡的墙面,被遮挡的墙面
    
    shadow = calWallsShadow(pointLight,wallJoinShadow)  #计算墙面阴影的地面点
    shadow = getWallShape(shadow)   #组成遮挡阴影以及被遮挡面的shape
    visibleShapes = calVisibleShape(shadow)  #计算可视面积
    visibleShapes['visibleShapes'] = visibleShapes.apply(lambda r: convert2To3(r),axis = 1)
    return visibleShapes['visibleShapes']
 '''