.. pybdshadow documentation master file, created by
   sphinx-quickstart on Thu Oct 21 14:41:25 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pybdshadow 
========================================

.. image:: _static/logo-wordmark-dark.png


`pybdshadow` is a python package to generate building shadow geometry. 


Installation
---------------------------------


It is recommended to use `Python 3.7, 3.8, 3.9`. 
`pybdshadow` can be installed by using `pip install`. Before installing `pybdshadow`, make sure that 
you have installed the available `geopandas` package: https://geopandas.org/en/stable/getting_started/install.html. 
If you already have geopandas installed, run the following code directly from the command prompt to install `pybdshadow`:

    pip install pybdshadow

Dependency
---------------------------------
`pybdshadow` depends on the following packages

* `numpy`
* `pandas`
* `shapely`
* `rtree`
* `geopandas`
* `matplotlib`
* `suncalc`
* `keplergl` (optional)

Example
---------------------------------

Given a building GeoDataFrame and datetime, `pybdshadow` can calculate the building shadow based on the sun position obtained by `suncalc`

::

   #Given UTC datetime
   date = pd.to_datetime('2015-01-01 02:45:33.959797119')
   #Calculate building shadow
   shadows = pybdshadow.bdshadow_sunlight(buildings,date)


Citation information
---------------------------------

Citation information can be found at https://github.com/ni1o1/pybdshadow/blob/main/CITATION.cff.


Method
=========================

.. toctree::
   :caption: Method
   :maxdepth: 2
   
   preprocess.rst
   bdshadow.rst
   Visualization.rst