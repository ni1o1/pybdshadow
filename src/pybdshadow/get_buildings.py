import requests
from vt2geojson.tools import vt_bytes_to_geojson
import pandas as pd
import geopandas as gpd
import transbigdata as tbd
from .preprocess import bd_preprocess
from tqdm import tqdm
import math
from retrying import retry
from requests.exceptions import RequestException

def deg2num(lat_deg, lon_deg, zoom):
    '''
    Calculate xy tiles from coordinates

    Parameters
    -------
    lon_deg : number
        Longitude
    lat_deg : number
        Latitude
    zoom : Int
        Zoom level of the map
    '''
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) +
                (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return (xtile, ytile)



def is_request_exception(e):
    return issubclass(type(e),RequestException)

@retry(retry_on_exception=is_request_exception,wrap_exception=False, stop_max_attempt_number=300)
def safe_request(url, **kwargs):
    return requests.get(url, **kwargs)

def getbd(x,y,z,MAPBOX_ACCESS_TOKEN):
    '''
    Get buildings from mapbox vector tiles

    Parameters
    -------
    x : Int
        x tile number
    y : Int
        y tile number
    z : Int
        zoom level of the map
    MAPBOX_ACCESS_TOKEN : str
        Mapbox access token

    Return
    ----------
    building : GeoDataFrame
        buildings in the tile
    '''
    try:
        url = f"https://api.mapbox.com/v4/mapbox.mapbox-streets-v8,mapbox.mapbox-terrain-v2,mapbox.mapbox-bathymetry-v2/{z}/{x}/{y}.vector.pbf?sku=101vMyxQx9v3Q&access_token={MAPBOX_ACCESS_TOKEN}"
        
        r = safe_request(url, timeout=10)
        assert r.status_code == 200, r.content
        vt_content = r.content
        features = vt_bytes_to_geojson(vt_content, x, y, z)
        gdf = gpd.GeoDataFrame.from_features(features)
        building = gdf[gdf['height']>0][['geometry', 'height','type']]
    except:
        building = pd.DataFrame()
    return building


def get_tiles_by_lonlat(lon1,lat1,lon2,lat2,z):
    '''
    Get tiles by lonlat

    Parameters
    -------
    lon1 : number
        Longitude of the first point
    lat1 : number
        Latitude of the first point
    lon2 : number
        Longitude of the second point
    lat2 : number
        Latitude of the second point
    z : Int
        Zoom level of the map

    Return
    ----------
    tiles : DataFrame
        Tiles in the area
    '''
    x1,y1 = deg2num(lat1, lon1, z)
    x2,y2 = deg2num(lat2, lon2, z)
    x_min = min(x1,x2)
    x_max = max(x1,x2)
    y_min = min(y1,y2)
    y_max = max(y1,y2)
    tiles = pd.DataFrame(range(x_min,x_max+1), columns=['x']).assign(foo=1).merge(pd.DataFrame(range(y_min,y_max+1), columns=['y']).assign(foo=1)).drop('foo', axis=1).assign(z=z)
    return tiles

def get_tiles_by_polygon(polygon,z):
    '''
    Get tiles by polygon
    
    Parameters
    -------
    polygon : GeoDataFrame of Polygon or MultiPolygon
        Polygon of the area
    z : Int
        Zoom level of the map

    Return
    ----------
    tiles : DataFrame
        Tiles in the area
    '''
    grid,params = tbd.area_to_grid(polygon,accuracy=400)
    grid['lon'] = grid.centroid.x
    grid['lat'] = grid.centroid.y
    a = grid.apply(lambda x: deg2num(x.lat, x.lon, z), axis=1)
    grid['x'] = a.apply(lambda a:a[0])
    grid['y'] = a.apply(lambda a:a[1])
    grid['z'] = z
    tiles = grid[['x','y','z']].drop_duplicates()
    return tiles

def get_buildings_threading(tiles,MAPBOX_ACCESS_TOKEN,merge=False,num_threads=100):
    '''
    Get buildings by threading

    Parameters
    -------
    tiles : DataFrame
        Tiles in the area
    MAPBOX_ACCESS_TOKEN : str
        Mapbox access token
    merge : bool
        whether to merge buildings in the same grid
    num_threads : Int
        number of threads

    Return
    ----------
    building : GeoDataFrame
        buildings in the area
    '''
    def merge_building(building):
        building = building.groupby(['height','type']).apply(lambda r:r.unary_union).reset_index()
        building.columns = ['height','type','geometry']
        building = gpd.GeoDataFrame(building,geometry = 'geometry')
        building = bd_preprocess(building)
        return building
    
    # 这是修改后的 getbd_tojson 函数
    def getbd_tojson(data, MAPBOX_ACCESS_TOKEN, pbar, results):
        for j in range(len(data)):
            r = data.iloc[j]
            x, y, z = r['x'], r['y'], r['z']
            try:
                url = f"https://api.mapbox.com/v4/mapbox.mapbox-streets-v8,mapbox.mapbox-terrain-v2,mapbox.mapbox-bathymetry-v2/{z}/{x}/{y}.vector.pbf?sku=101vMyxQx9v3Q&access_token={MAPBOX_ACCESS_TOKEN}"
                r = safe_request(url, timeout=10)
                assert r.status_code == 200, r.content
                vt_content = r.content
                features = vt_bytes_to_geojson(vt_content, x, y, z)
                gdf = gpd.GeoDataFrame.from_features(features)
                building = gdf[gdf['height'] > 0][['geometry', 'height', 'type']]
                results.append(building)  # 将结果添加到全局列表
            except:
                pass
            finally:
                pbar.update()
                
    # 主程序
    import threading
    import os
    # 主程序
    # 分割数据
    grid = tiles.copy()
    bins = num_threads

    grid['tmpid'] = range(len(grid))
    grid['group_num'] = pd.cut(grid['tmpid'], bins, precision=2, labels=range(bins))

    # 创建进度条
    pbar = tqdm(total=len(grid), desc='Downloading Buildings: ')

    # 存储结果的全局列表
    results = []

    # 划分线程
    threads = []
    for i in range(bins):
        data = grid[grid['group_num'] == i]
        threads.append(threading.Thread(target=getbd_tojson, args=(data, MAPBOX_ACCESS_TOKEN, pbar, results)))

    # 线程开始
    for t in threads:
        t.setDaemon(True)
        t.start()
    for t in threads:
        t.join()

    # 关闭进度条
    pbar.close()
    threads.clear()

    # 合并数据
    building = pd.concat(results)

    if merge:
        #再做一次聚合，分栅格聚合建筑
        building['x'] = building.centroid.x
        building['y'] = building.centroid.y
        params = tbd.area_to_params(building['geometry'].iloc[0].bounds)
        building['LONCOL'],building['LATCOL'] = tbd.GPS_to_grid(building['x'],building['y'],params)
        building['tile'] = building['LONCOL'].astype(str)+'_'+building['LATCOL'].astype(str)
        building = building.groupby(['tile','type']).apply(merge_building).reset_index(drop=True)
        
    building = building[['geometry','height','type']]
    building['building_id'] = range(len(building))

    return building

def get_buildings_by_bounds(lon1,lat1,lon2,lat2,MAPBOX_ACCESS_TOKEN,merge=False):
    '''
    Get buildings by bounds

    Parameters
    -------
    lon1 : number
        Longitude of the first point
    lat1 : number
        Latitude of the first point
    lon2 : number
        Longitude of the second point
    lat2 : number
        Latitude of the second point
    MAPBOX_ACCESS_TOKEN : str
        Mapbox access token
    merge : bool
        whether to merge buildings in the same grid

    Return
    ----------
    building : GeoDataFrame
        buildings in the area 
    '''
    tiles = get_tiles_by_lonlat(lon1,lat1,lon2,lat2,16)
    building = get_buildings_threading(tiles,MAPBOX_ACCESS_TOKEN,merge)
    building = bd_preprocess(building)
    return building

def get_buildings_by_polygon(polygon,MAPBOX_ACCESS_TOKEN,merge=False):
    '''
    Get buildings by polygon

    Parameters
    -------
    polygon : GeoDataFrame of Polygon or MultiPolygon
        Polygon of the area
    MAPBOX_ACCESS_TOKEN : str
        Mapbox access token
    merge : bool
        whether to merge buildings in the same grid

    Return
    ----------
    building : GeoDataFrame
        buildings in the area
    '''
    tiles = get_tiles_by_polygon(polygon,16)
    building = get_buildings_threading(tiles,MAPBOX_ACCESS_TOKEN,merge)
    building = bd_preprocess(building)
    return building