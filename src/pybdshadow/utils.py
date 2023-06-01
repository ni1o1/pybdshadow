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

def lonlat2aeqd(lonlat):
    '''
    Convert longitude and latitude to azimuthal equidistant projection coordinates.

    Parameters
    ----------
    lonlat : numpy.ndarray
        Longitude and latitude in degrees. The shape of the array is (n,m,2), where n and m are the number of pixels in the first and second dimension, respectively. The last dimension is for longitude and latitude.

    Returns
    -------
    proj_coords : numpy.ndarray
        Azimuthal equidistant projection coordinates. The shape of the array is (n,m,2), where n and m are the number of pixels in the first and second dimension, respectively. The last dimension is for x and y coordinates.

    example
    -----------------
    >>> import numpy as np
    >>> from pybdshadow import utils
    >>> lonlat = np.array([[[120,30],[121,31]],[[120,30],[121,31]]])
    >>> proj_coords = utils.lonlat2aeqd(lonlat)
    >>> proj_coords
    array([[[-48243.5939812 , -55322.02388971],
            [ 47752.57582735,  55538.86412435]],
           [[-48243.5939812 , -55322.02388971],
            [ 47752.57582735,  55538.86412435]]])
    '''
    meanlon = lonlat[:,:,0].mean()
    meanlat = lonlat[:,:,1].mean()
    from pyproj import CRS
    epsg = CRS.from_proj4("+proj=aeqd +lat_0="+str(meanlat)+" +lon_0="+str(meanlon)+" +datum=WGS84")
    from pyproj import Transformer
    transformer = Transformer.from_crs("EPSG:4326", epsg,always_xy = True)
    proj_coords = transformer.transform(lonlat[:,:,0], lonlat[:,:,1])
    proj_coords = np.array(proj_coords).transpose([1,2,0])
    return proj_coords


def aeqd2lonlat(proj_coords,meanlon,meanlat):
    '''
    Convert azimuthal equidistant projection coordinates to longitude and latitude.

    Parameters
    ----------
    proj_coords : numpy.ndarray
        Azimuthal equidistant projection coordinates. The shape of the array is (n,m,2), where n and m are the number of pixels in the first and second dimension, respectively. The last dimension is for x and y coordinates.
    meanlon : float
        Longitude of the center of the azimuthal equidistant projection in degrees.
    meanlat : float
        Latitude of the center of the azimuthal equidistant projection in degrees.

    Returns
    -------
    lonlat : numpy.ndarray
        Longitude and latitude in degrees. The shape of the array is (n,m,2), where n and m are the number of pixels in the first and second dimension, respectively. The last dimension is for longitude and latitude.

    Example
    -----------------
    >>> import numpy as np
    >>> from pybdshadow import utils
    >>> proj_coords = proj_coords = np.array(
        [[[-48243.5939812 , -55322.02388971],
          [ 47752.57582735,  55538.86412435]],
         [[-48243.5939812 , -55322.02388971],
          [ 47752.57582735,  55538.86412435]]])
    >>> lonlat = utils.aeqd2lonlat(proj_coords,120.5,30.5)
    >>> lonlat
    array([[[120.,  30.],
            [121.,  31.]],
           [[120.,  30.],
            [121.,  31.]]])
    '''
    from pyproj import CRS
    epsg = CRS.from_proj4("+proj=aeqd +lat_0="+str(meanlat)+" +lon_0="+str(meanlon)+" +datum=WGS84")
    from pyproj import Transformer
    transformer = Transformer.from_crs( epsg,"EPSG:4326",always_xy = True)
    lonlat = transformer.transform(proj_coords[:,:,0], proj_coords[:,:,1])
    lonlat = np.array(lonlat).transpose([1,2,0])
    return lonlat

