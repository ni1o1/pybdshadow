import pybdshadow
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon


class Testadvisualarea:
    def test_advisualarea(self):
        buildings = gpd.GeoDataFrame({
            'height': [42],
            'building_id': 1,
            'geometry': [
                Polygon([(139.714612, 35.551441),
                         (139.714616, 35.55144),
                         (139.714705, 35.551412),
                         (139.714712, 35.551427),
                         (139.714878, 35.551375),
                         (139.714913, 35.551447),
                         (139.714755, 35.551497),
                         (139.714763, 35.551514),
                         (139.714757, 35.551516),
                         (139.714662, 35.551546),
                         (139.714612, 35.551441)])]})
        ad_params = {'point1': [139.711861, 35.552040],
                     'point2': [139.713319, 35.553646],
                     'height': 50,
                     }
        # 计算可视面积
        visualArea, shadows = pybdshadow.ad_visualArea(ad_params, buildings)
        result = list(shadows.geometry.iloc[0].exterior.coords)
        truth = [(139.714612, 35.551441),
                 (139.714662, 35.551546),
                 (139.714757, 35.551516),
                 (139.714763, 35.551514),
                 (139.71482917729838, 35.55147352617139),
                 (139.714913, 35.551447),
                 (139.72710874999996, 35.54411800000004),
                 (139.72688999999997, 35.543668000000025),
                 (139.72585249999992, 35.543993),
                 (139.72580875000003, 35.54389925000002),
                 (139.7252525, 35.54407425000002),
                 (139.7252274999999, 35.54408050000001),
                 (139.714612, 35.551441)]
        assert np.allclose(result, truth)

        billboard_gdf = pybdshadow.ad_to_gdf(ad_params, billboard_height=100)
        pybdshadow.show_bdshadow(buildings=buildings,
                                 shadows=shadows,
                                 ad=billboard_gdf,
                                 ad_visualArea=visualArea)

        #Define study area
        bounds = [139.707846,35.543637,139.712567,35.549909]       
        ad_params = pybdshadow.ad_optimize(bounds,
                                   buildings,
                                   height_range=[100,200],
                                   printlog=True,
                                   size_pop=2,
                                   max_iter=1,
                                   prob_mut=0.001,
                                   precision=1e-7)