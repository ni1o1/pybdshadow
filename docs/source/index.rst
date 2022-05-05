.. pybdshadow documentation master file, created by
   sphinx-quickstart on Thu Oct 21 14:41:25 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pybdshadow 
========================================

.. image:: _static/logo-wordmark-dark.png

Introduction
---------------------------------

| `pybdshadow` is a python package for generating, analyzing and visualizing building shadows from large scale building geographic data. `pybdshadow` support generate building shadows from both sun light and point light. `pybdshadow` provides an efficient and easy-to-use method to generate a new source of geospatial data with great application potential in urban study. 

| The latest stable release of the software can be installed via pip and full documentation can be found [here](https://pybdshadow.readthedocs.io/en/latest/).


Functionality
---------------------------------

Currently, `pybdshadow` mainly provides the following methods:

- **Generating building shadow from sun light**: With given location and time, the function in `pybdshadow` uses the properties of sun position obtained from `suncalc-py` and the building height to generate shadow geometry data.
- **Generating building shadow from point light**: `pybdshadow` can generate the building shadow with given location and height of the point light, which can be potentially useful for visual area analysis in urban environment.
- **Analysis**: `pybdshadow` integrated the analysing method based on the properties of sun movement to track the changing position of shadows within a fixed time interval. Based on the grid processing framework provided by `TransBigData`, `pybdshadow` is capable of calculating sunshine time on the ground and on the roof.
- **Visualization**: Built-in visualization capabilities leverage the visualization package `keplergl` to interactively visualize building and shadow data in Jupyter notebooks with simple code.

The target audience of `pybdshadow` includes data science researchers and data engineers in the field of BIM, GIS, energy, environment, and urban computing.


Example
---------------------------------

Given a building GeoDataFrame and UTC datetime, `pybdshadow` can calculate the building shadow based on the sun position obtained by `suncalc`

::

   import pybdshadow
   #Given UTC datetime
   date = pd.to_datetime('2022-01-01 12:45:33.959797119')\
            .tz_localize('Asia/Shanghai')\
            .tz_convert('UTC')
   #Calculate building shadow
   shadows = pybdshadow.bdshadow_sunlight(buildings,date)

`pybdshadow` also provide visualization method supported by keplergl. 

::

   # visualize buildings and shadows
   pybdshadow.show_bdshadow(buildings = buildings,shadows = shadows)

.. image:: _static/visualize.png


.. toctree::
   :caption: Installation and dependencies
   :maxdepth: 2

   install.rst

.. toctree::
   :caption: Example
   :maxdepth: 2

   example/example.rst

.. toctree::
   :caption: Method
   :maxdepth: 2
   
   preprocess.rst
   bdshadow.rst
   analysis.rst
   Visualization.rst