.. _bdshadow:


*********************
Building shadow
*********************


Shadow from sunlight
--------------------------------------

.. function:: pybdshadow.bdshadow_sunlight(buildings, date,  height='height', roof=False,include_building = True,ground=0)

Generate the shadow of the buildings from sunlight.

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

Shadow from pointlight
--------------------------------------

.. function:: pybdshadow.bdshadow_pointlight(buildings, pointlon, pointlat, pointheight, merge=True, height='height', ground=0)

Generate the shadow of the buildings from point light.

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