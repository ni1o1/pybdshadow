import pybdshadow
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon


class Testpointlightshadow:
    def test_bdshadow_pointlight(self):

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

        buildings = pybdshadow.bd_preprocess(buildings)

        pointlon,pointlat,pointheight = [139.69799, 35.534175,100]
        #Calculate building shadow for point light
        shadows = pybdshadow.bdshadow_pointlight(buildings,pointlon,pointlat,pointheight)
        result = list(shadows['geometry'].iloc[0].exterior.coords)
        truth = [(139.698311, 35.533642),
        (139.698311, 35.533796),
        (139.698888, 35.533794),
        (139.698891, 35.53417),
        (139.699079, 35.53417),
        (139.69986758620692, 35.53416637931035),
        (139.69986068965517, 35.533247413793106),
        (139.69854344827584, 35.53325603448276),
        (139.698311, 35.533642)]
        assert np.allclose(result,truth)