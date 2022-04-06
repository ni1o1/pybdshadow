import pybdshadow
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon


class Testpybdshadow:
    def test_bdshadow_sunlight(self):
        buildings = gpd.GeoDataFrame({
            'height': [42],
            'geometry': [
                Polygon([(139.698311, 35.533796),
                         (139.698311,
                          35.533642),
                         (139.699075,
                          35.533637),
                         (139.699079,
                          35.53417),
                         (139.698891,
                          35.53417),
                         (139.698888,
                          35.533794),
                         (139.698311, 35.533796)])]})
        date = pd.to_datetime('2015-01-01 02:45:33.959797119')

        buildings = pybdshadow.bd_preprocess(buildings)

        buildingshadow = pybdshadow.bdshadow_sunlight(
            buildings, date, merge = True, epsg=3857)

        area = buildingshadow['geometry'].iloc[0]
        area = np.array(area.exterior.coords)
        truth = np.array([[139.698311  ,  35.533642  ],
                        [139.698311  ,  35.533796  ],
                        [139.69831237,  35.53429879],
                        [139.69888937,  35.53429679],
                        [139.69889237,  35.53467278],
                        [139.69908037,  35.53467278],
                        [139.699079  ,  35.53417   ],
                        [139.699075  ,  35.533637  ],
                        [139.698311  ,  35.533642  ]])
        assert np.allclose(area, truth)

        pybdshadow.show_bdshadow(buildings=buildings,
                                 shadows=buildingshadow)
