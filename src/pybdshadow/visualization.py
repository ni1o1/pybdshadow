"""
BSD 3-Clause License

Copyright (c) 2022, Qing Yu
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import numpy as np
import geopandas as gpd


def show_bdshadow(buildings=gpd.GeoDataFrame(),
                  shadows=gpd.GeoDataFrame(),
                  height='height',
                  zoom='auto'):
    '''
    Visualize the building and shadow with keplergl.

    **Parameters**
    buildings : GeoDataFrame
        Buildings. coordinate system should be WGS84
    shadows : GeoDataFrame
        Building shadows. coordinate system should be WGS84
    height : string
        Column name of building height
    zoom : number
        Zoom level of the map

    **Return**
    vmap : keplergl.keplergl.KeplerGl
        Visualizations provided by keplergl
    '''
    displaybuilding = buildings.copy()
    displaybuildingshadow = shadows.copy()
    vmapdata = {}
    layers = []
    if len(displaybuilding) == 0:
        displaybuilding['geometry'] = []
        displaybuilding[height] = []
    else:
        vmapdata['building'] = displaybuilding
        layers.append({
            'id': '4eo0v3',
            'type': 'geojson',
            'config': {
                'dataId': 'building',
                'label': 'building',
                'color': [169, 203, 237],
                'highlightColor': [252, 242, 26, 255],
                'columns': {'geojson': 'geometry'},
                'isVisible': True,
                'visConfig': {
                    'opacity': 0.8,
                    'strokeOpacity': 0.8,
                    'thickness': 0.5,
                    'strokeColor': [221, 178, 124],
                    'colorRange': {
                        'name': 'Global Warming',
                        'type': 'sequential',
                        'category': 'Uber',
                                    'colors': ['#5A1846',
                                               '#900C3F',
                                               '#C70039',
                                               '#E3611C',
                                               '#F1920E',
                                               '#FFC300']},
                    'strokeColorRange': {'name': 'Global Warming',
                                         'type': 'sequential',
                                         'category': 'Uber',
                                                     'colors': ['#5A1846',
                                                                '#900C3F',
                                                                '#C70039',
                                                                '#E3611C',
                                                                '#F1920E',
                                                                '#FFC300']},
                                'radius': 10,
                                'sizeRange': [0, 10],
                                'radiusRange': [0, 50],
                                'heightRange': [0, 500],
                                'elevationScale': 0.1,
                                'enableElevationZoomFactor': True,
                                'stroked': False,
                                'filled': True,
                                'enable3d': True,
                                'wireframe': False},
                'hidden': False,
                'textLabel': [{'field': None,
                               'color': [255, 255, 255],
                               'size': 18,
                               'offset': [0, 0],
                               'anchor': 'start',
                               'alignment': 'center'}]},
            'visualChannels': {'colorField': None,
                               'colorScale': 'quantile',
                               'strokeColorField': None,
                               'strokeColorScale': 'quantile',
                               'sizeField': None,
                               'sizeScale': 'linear',
                               'heightField': {
                                   'name': 'height',
                                   'type': 'integer'},
                               'heightScale': 'linear',
                               'radiusField': None,
                               'radiusScale': 'linear'}})
        bdcentroid = displaybuilding['geometry'].bounds[[
            'minx', 'miny', 'maxx', 'maxy']]
        lon_center, lat_center = bdcentroid['minx'].mean(
        ), bdcentroid['miny'].mean()
        lon_min, lon_max = bdcentroid['minx'].min(), bdcentroid['maxx'].max()
    if len(displaybuildingshadow) == 0:
        displaybuildingshadow['geometry'] = []
    else:
        bdcentroid = displaybuildingshadow['geometry'].bounds[[
            'minx', 'miny', 'maxx', 'maxy']]
        lon_center, lat_center = bdcentroid['minx'].mean(
        ), bdcentroid['miny'].mean()
        lon_min, lon_max = bdcentroid['minx'].min(), bdcentroid['maxx'].max()
        vmapdata['shadow'] = displaybuildingshadow
        layers.append(
            {'id': 'lz48o1',
             'type': 'geojson',
                     'config': {
                         'dataId': 'shadow',
                         'label': 'shadow',
                         'color': [73, 73, 73],
                         'highlightColor': [252, 242, 26, 255],
                         'columns': {'geojson': 'geometry'},
                         'isVisible': True,
                         'visConfig': {
                             'opacity': 0.32,
                             'strokeOpacity': 0.8,
                             'thickness': 0.5,
                             'strokeColor': [255, 153, 31],
                             'colorRange': {'name': 'Global Warming',
                                            'type': 'sequential',
                                            'category': 'Uber',
                                            'colors': ['#5A1846',
                                                       '#900C3F',
                                                       '#C70039',
                                                       '#E3611C',
                                                       '#F1920E',
                                                       '#FFC300']},
                             'strokeColorRange': {'name': 'Global Warming',
                                                  'type': 'sequential',
                                                  'category': 'Uber',
                                                  'colors': ['#5A1846',
                                                             '#900C3F',
                                                             '#C70039',
                                                             '#E3611C',
                                                             '#F1920E',
                                                             '#FFC300']},
                             'radius': 10,
                             'sizeRange': [0, 10],
                             'radiusRange': [0, 50],
                             'heightRange': [0, 500],
                             'elevationScale': 5,
                             'enableElevationZoomFactor': True,
                             'stroked': False,
                             'filled': True,
                             'enable3d': False,
                             'wireframe': False},
                         'hidden': False,
                         'textLabel': [{
                             'field': None,
                                       'color': [255, 255, 255],
                                       'size': 18,
                                       'offset': [0, 0],
                                       'anchor': 'start',
                                       'alignment': 'center'}]},
                     'visualChannels': {
                         'colorField': None,
                         'colorScale': 'quantile',
                         'strokeColorField': None,
                         'strokeColorScale': 'quantile',
                         'sizeField': None,
                         'sizeScale': 'linear',
                         'heightField': None,
                         'heightScale': 'linear',
                                        'radiusField': None,
                                        'radiusScale': 'linear'}})
    try:
        from keplergl import KeplerGl
    except ImportError:
        raise ImportError(
            "Please install keplergl, run "
            "the following code in cmd: pip install keplergl")

    if zoom == 'auto':
        zoom = 8.5-np.log(lon_max-lon_min)/np.log(2)
    vmap = KeplerGl(config={
        'version': 'v1',
        'config': {
            'visState': {
                'filters': [],
                'layers': layers,
                'layerBlending': 'normal',
                'animationConfig': {'currentTime': None, 'speed': 1}},
            'mapState': {'bearing': -3,
                         'dragRotate': True,
                         'latitude': lat_center,
                         'longitude': lon_center,
                         'pitch': 50,
                         'zoom': zoom,
                         'isSplit': False},
            'mapStyle': {'styleType': 'light',
                         'topLayerGroups': {},
                         'visibleLayerGroups': {'label': True,
                                                'road': True,
                                                'border': False,
                                                'building': True,
                                                'water': True,
                                                'land': True},
                         'mapStyles': {}}}}, data=vmapdata, height=500)
    return vmap
