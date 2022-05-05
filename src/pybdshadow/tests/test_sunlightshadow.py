import pybdshadow
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon


class Testsunlightshadow:
    def test_bdshadow_sunlight(self):

        buildings = gpd.GeoDataFrame({
            'height': [42, 9],
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
                        (139.698311, 35.533796)]),
                Polygon([(139.69799, 35.534175),
                        (139.697988, 35.53389),
                        (139.698814, 35.533885),
                        (139.698816, 35.534171),
                        (139.69799, 35.534175)])]})
        date = pd.to_datetime('2015-01-01 03:45:33.959797119')

        buildings = pybdshadow.bd_preprocess(buildings)

        buildingshadow = pybdshadow.bdshadow_sunlight(
            buildings, date, roof=True, include_building=False)

        area = buildingshadow['geometry'].iloc[0]
        area = np.array(area.exterior.coords)
        truth = np.array([(139.6983434498457, 35.53388784954066),
                          (139.698343456533, 35.533887872006716),
                          (139.6984440527688, 35.53417277873741),
                          (139.69844406145836, 35.534172800060766),
                          (139.69844408446318, 35.534172801043766),
                          (139.69881597541797, 35.534171000119045),
                          (139.69881599883948, 35.53417099885312),
                          (139.6988159998281, 35.53417097541834),
                          (139.69881400017155, 35.533885024533475),
                          (139.6988139988598, 35.53388500115515),
                          (139.69881397546646, 35.53388500014851),
                          (139.69834347324914, 35.53388784822488),
                          (139.6983434498457, 35.53388784954066)])
        assert np.allclose(area, truth)

        pybdshadow.show_bdshadow(buildings=buildings,
                                 shadows=buildingshadow)
