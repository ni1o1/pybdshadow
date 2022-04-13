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

import math
import numpy as np


def lonlat_mercator(lonlat):
    mercator = lonlat.copy()
    earthRad = 6378137.0
    mercator[0] = lonlat[0] * math.pi / 180 * earthRad  # 角度转弧度
    a = lonlat[1] * math.pi / 180  # 弧度制纬度
    mercator[1] = earthRad / 2 * \
        math.log((1.0 + math.sin(a)) / (1.0 - math.sin(a)))
    return mercator


def lonlat_mercator_vector(lonlat):
    mercator = np.zeros_like(lonlat)
    earthRad = 6378137.0
    mercator[:, :, 0] = lonlat[:, :, 0] * math.pi / 180 * earthRad  # 角度转弧度
    a = lonlat[:, :, 1] * math.pi / 180  # 弧度制纬度
    mercator[:, :, 1] = earthRad / 2 * \
        np.log((1.0 + np.sin(a)) / (1.0 - np.sin(a)))
    return mercator


def mercator_lonlat(mercator):
    lonlat = mercator.copy()
    lonlat[0] = mercator[0]/20037508.34*180
    temp = mercator[1]/20037508.34*180
    lonlat[1] = 180/math.pi * \
        (2*math.atan(math.exp(temp*math.pi/180)) - math.pi/2)  # 纬度的长度
    return lonlat


def mercator_lonlat_vector(mercator):
    lonlat = np.zeros_like(mercator)
    lonlat[:, :, 0] = mercator[:, :, 0]/20037508.34*180
    lonlat[:, :, 1] = mercator[:, :, 1]/20037508.34*180
    lonlat[:, :, 1] = 180/math.pi * \
        (2*np.arctan(np.exp(lonlat[:, :, 1]*math.pi/180)) - math.pi/2)

    return lonlat
