..
    This file is part of Brazil Data Cube Sentinel-2 Angle Bands.
    Copyright (C) 2022 INPE.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.


Usage
=====


Python Usage
------------

see:

`Calculate Sentinel 2 angle bands <examples/example.py>`_


Docker Usage
------------

run a docker container mounting an input-dir and provide the file name, e.g. S2A_MSIL1C_20201013T144731_N0209_R139_T19MGV_20201013T164036.SAFE.
The ouput will be generated in the same folder for .zip files or within GRANULE for .SAFE

.. code-block:: console

    docker run --rm -v /path/to/my/S2_file/:/mnt/input-dir s2angs S2A_MSIL1C_20201013T144731_N0209_R139_T19MGV_20201013T164036.SAFE

You can also provide an output folder to specify where the angles should be exported.

.. code-block:: console

    docker run --rm -v /path/to/my/S2_file/:/mnt/input-dir -v /path/to/my/output/:/mnt/output-dir s2angs S2A_MSIL1C_20201013T144731_N0209_R139_T19MGV_20201013T164036.SAFE
