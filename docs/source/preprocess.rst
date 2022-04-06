.. _preprocess:


*********************
Preprocess
*********************

Building preprocess
=============================

.. function:: pybdshadow.bd_preprocess(buildings)

Preprocess building data, so that we can perform shadow calculation.
Remove empty polygons and convert multipolygons into polygons.

**Parameters**

buildings : GeoDataFrame
    Buildings. 

**Return**

allbds : GeoDataFrame
    Polygon buildings

.. function:: pybdshadow.merge_shadow(data, col = 'building_id')

The input is the GeoDataFrame of polygon geometry, and the col
name. This function will merge the polygon based on the category
in the mentioned column

**Parameters**

data : GeoDataFrame
    The polygon geometry
col : str
    The column name for indicating category

**Return**

data1 : GeoDataFrame
    The merged polygon
