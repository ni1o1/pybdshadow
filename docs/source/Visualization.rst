.. _Visualization:


*****************************
Building Visualization
*****************************

Visualization
=============================

.. function:: pybdshadow.show_bdshadow(buildings=gpd.GeoDataFrame(),shadows=gpd.GeoDataFrame(),height='height',zoom='auto')

Visualize the building and shadow with keplergl.

**Parameters**

buildings : GeoDataFrame
    Buildings. coordinate system should be WGS84
shadows : GeoDataFrame
    Building shadows. coordinate system should be WGS84
height : string
    Column name of building height
zoom : number
    Zoom level of the map

**Return**

vmap : keplergl.keplergl.KeplerGl
    Visualizations provided by keplergl
