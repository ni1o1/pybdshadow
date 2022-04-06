# pybdshadow

![1649074615552.png](https://github.com/ni1o1/pybdshadow/raw/main/image/README/1649074615552.png)

[![Documentation Status](https://readthedocs.org/projects/pybdshadow/badge/?version=latest)](https://pybdshadow.readthedocs.io/en/latest/?badge=latest) [![codecov](https://codecov.io/gh/ni1o1/pybdshadow/branch/main/graph/badge.svg?token=GLAVYYCD9L)](https://codecov.io/gh/ni1o1/pybdshadow) [![Tests](https://github.com/ni1o1/pybdshadow/actions/workflows/tests.yml/badge.svg)](https://github.com/ni1o1/pybdshadow/actions/workflows/tests.yml)

## Introduction

`pybdshadow` is a python package to generate building shadow geometry. The latest stable release of the software can be installed via pip and full documentation can be found [here](https://pybdshadow.readthedocs.io/en/latest/).

## Example

Given a building GeoDataFrame and UTC datetime, `pybdshadow` can calculate the building shadow based on the sun position obtained by `suncalc`

```python
import pybdshadow
#Given UTC datetime
date = pd.to_datetime('2015-01-01 02:45:33.959797119')
#Calculate building shadow
shadows = pybdshadow.bdshadow_sunlight(buildings,date)
```

`pybdshadow` also provide visualization method supported by keplergl.

```python
# visualize buildings and shadows
pybdshadow.show_bdshadow(buildings = buildings,shadows = shadows)
```

![1649161376291.png](https://github.com/ni1o1/pybdshadow/raw/main/image/README/1649161376291.png)

Detail usage can be found in [this example](https://github.com/ni1o1/pybdshadow/blob/main/example/example.ipynb).

## Installation

It is recommended to use `Python 3.7, 3.8, 3.9`

### Using pypi [![PyPI version](https://badge.fury.io/py/pybdshadow.svg)](https://badge.fury.io/py/pybdshadow) 

`pybdshadow` can be installed by using `pip install`. Before installing `pybdshadow`, make sure that you have installed the available [geopandas package](https://geopandas.org/en/stable/getting_started/install.html). If you already have geopandas installed, run the following code directly from the command prompt to install `pybdshadow`:

```python
pip install pybdshadow
```

## Dependency
`pybdshadow` depends on the following packages

* `numpy`
* `pandas`
* `shapely`
* `rtree`
* `geopandas`
* `matplotlib`
* `suncalc`
* `keplergl` (optional)

## Citation information

Citation information can be found at [CITATION.cff](https://github.com/ni1o1/pybdshadow/blob/main/CITATION.cff).
