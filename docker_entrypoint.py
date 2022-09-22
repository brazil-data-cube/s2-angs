#
# This file is part of Brazil Data Cube Sentinel-2 Angle Bands.
# Copyright (C) 2022 INPE.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.
#

import sys
from pathlib import Path

# 3rdparty
import s2angs

if len(sys.argv) < 2:
    print('missing args, use .SAFE, .zip or folder containing S2 Data')
    sys.exit()

ang_source = sys.argv[1]
ang_input = Path(f'/mnt/input-dir/{ang_source}')
if Path('/mnt/output-dir/').exists():
    s2angs.gen_s2_ang(str(ang_input), '/mnt/output-dir/')
else:
    s2angs.gen_s2_ang(str(ang_input), '/mnt/input-dir/')