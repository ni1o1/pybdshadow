"""
`pybdshadow`: Python package to generate building shadow geometry.

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

__version__ = '0.3.5'
__author__ = 'Qing Yu <qingyu0815@foxmail.com>'

# module level doc-string
__doc__ = """
`pybdshadow` - Python package to generate building shadow geometry.
"""
from .pybdshadow import *
from .get_buildings import (
    get_buildings_by_polygon,
    get_buildings_by_bounds,
)
from .pybdshadow import (
    bdshadow_sunlight,
    bdshadow_pointlight
)
from .preprocess import (
    bd_preprocess
)
from .visualization import (
    show_bdshadow,
    show_sunshine,
)
from .analysis import (
    cal_sunshine,
    cal_sunshadows,
    cal_shadowcoverage,
    get_timetable
)

from .utils import (
    extrude_poly
)

__all__ = ['bdshadow_sunlight',
           'bdshadow_pointlight',
           'bd_preprocess',
           'show_bdshadow',
           'cal_sunshine',
           'cal_sunshadows',
           'cal_shadowcoverage',
           'get_timetable',
           'get_buildings_by_polygon',
           'get_buildings_by_bounds',
           'cal_sunshine_facade',
           'show_sunshine',
           'extrude_poly'
           ]
