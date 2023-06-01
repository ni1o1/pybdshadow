import pybdshadow
import geopandas as gpd
from shapely.geometry import Polygon


class Testanalysis:
    def test_analysis(self):
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
        #分析
        date = '2022-01-01'
        shadows = pybdshadow.cal_sunshadows(buildings,dates = [date],precision=3600)
        bdgrids = pybdshadow.cal_shadowcoverage(shadows,buildings,precision = 3600,accuracy=2)
        assert len(bdgrids)==1185
        
        grids = pybdshadow.cal_sunshine(buildings)
        assert len(grids)==1882
                                 
        sunshine = pybdshadow.cal_sunshine(buildings,accuracy='vector')
        sunshine = pybdshadow.cal_sunshine(buildings,accuracy='vector',roof = True)