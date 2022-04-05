.. _preprocess:


*********************
Preprocess
*********************

Building preprocess
=============================

bd_preprocess(buildings):

Preprocess building data, so that we can perform shadow calculation.
Remove empty polygons and convert multipolygons into polygons.

**Parameters**

buildings : GeoDataFrame
    Buildings. 

**Return**

allbds : GeoDataFrame
    Polygon buildings
