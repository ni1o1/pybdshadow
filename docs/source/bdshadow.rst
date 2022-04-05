.. _bdshadow:


*********************
Building shadow
*********************


Shadow from sunlight
=============================

.. function:: pybdshadow.bdshadow_sunlight(buildings, date, height='height', ground=0, epsg=3857)

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

.. function:: pybdshadow.singlebdshadow_sunlight(building, height, sunPosition)

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

