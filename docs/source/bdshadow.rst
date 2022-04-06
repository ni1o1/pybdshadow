.. _bdshadow:


*********************
Building shadow
*********************


Shadow from sunlight
=============================

.. function:: pybdshadow.bdshadow_sunlight(buildings, date, merge=False, height='height', ground=0)

Calculate the sunlight shadow of the buildings.

**Parameters**

buildings : GeoDataFrame
    Buildings. coordinate system should be WGS84
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
