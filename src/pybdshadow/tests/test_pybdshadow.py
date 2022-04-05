import pybdshadow
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon

class Testpybdshadow:
    def test_bdshadow_sunlight(self):
        building = gpd.GeoDataFrame({'height':[42],'geometry':[Polygon([(139.698311, 35.533796),
        (139.698311, 35.533642),
        (139.699075, 35.533637),
        (139.699079, 35.53417),
        (139.698891, 35.53417),
        (139.698888, 35.533794),
        (139.698311, 35.533796)])]})
        date = pd.to_datetime('2015-01-01 02:45:33.959797119')

        buildingshadow = pybdshadow.bdshadow_sunlight(building,date,epsg = 3857)
        area = buildingshadow['geometry'].iloc[0].area
        truth = 5.76296081373734e-07
        assert np.allclose(area,truth)

        pybdshadow.show_bdshadow(building=building,
                                shadow=buildingshadow)


