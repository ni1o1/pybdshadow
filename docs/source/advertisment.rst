.. _advertisment:


********************************************
Advertisment billboard visual area
********************************************

Advertisment parameters
--------------------------------------

To analyze billboard visual area, the parameter `ad_params` for the billboard should be defined. It has two forms::

    #1. Given the coordinates of the two border points and height
    ad_params = {'point1': [139.711861, 35.552040],
                'point2': [139.713319, 35.553646],#1861,3646
                'height': 50,
                }
    #2. Given the coordinates of brandCenter, orientation and height
    ad_params = {'orientation': 1.2806657381630058,
                'height': 10,
                'brandCenter': [139.71259, 35.552842999999996]} 

You can use `ad_to_gdf` to generate the GeoDataFrame for the billboard in order to visualize it.

.. function:: pybdshadow.ad_to_gdf(ad_params,billboard_height = 10)

Generate a GeoDataFrame from ad_params for visualization.

**Parameters**

ad_params : dict
    Parameters of advertisement.
billboard_height : number
    The height of the billboard

**Return**

ad_gdf : GeoDataFrame
    advertisment GeoDataFrame

Visual area calculation
--------------------------------------

.. function:: pybdshadow.ad_visualArea(ad_params, buildings=gpd.GeoDataFrame(), height='height')

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

Optimize billboard parameters
--------------------------------------

.. function:: pybdshadow.ad_optimize(bounds,buildings,height_range=[0, 100],multiplier=[0.01, 0.001],printlog=True,size_pop=10,max_iter=30,prob_mut=0.001,precision=1e-7)

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
