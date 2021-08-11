..
    This file is part of Python Client Library for Sentinel-2 Angle Bands.
    Copyright (C) 2021 INPE.

    Python Client Library for Sentinel-2 Angle Bands is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.


================================================
Python Client Library for Sentinel-2 Angle Bands
================================================


.. image:: https://img.shields.io/badge/license-MIT-green
        :target: https://github.com//brazil-data-cube/s2-angs/blob/master/LICENSE
        :alt: Software License


.. image:: https://drone.dpi.inpe.br/api/badges/brazil-data-cube/s2-angs/status.svg
        :target: https://drone.dpi.inpe.br/brazil-data-cube/s2-angs
        :alt: Build Status


.. image:: https://codecov.io/gh/brazil-data-cube/s2-angs/branch/master/graph/badge.svg
        :target: https://codecov.io/gh/brazil-data-cube/s2-angs
        :alt: Code Coverage Test


.. image:: https://readthedocs.org/projects/s2angs/badge/?version=latest
        :target: https://s2angs.readthedocs.io/en/latest/
        :alt: Documentation Status


.. image:: https://img.shields.io/badge/lifecycle-maturing-blue.svg
        :target: https://www.tidyverse.org/lifecycle/#maturing
        :alt: Software Life Cycle


.. image:: https://img.shields.io/github/tag/brazil-data-cube/s2-angs.svg
        :target: https://github.com/brazil-data-cube/s2-angs/releases
        :alt: Release


.. image:: https://img.shields.io/pypi/v/s2angs
        :target: https://pypi.org/project/s2angs/
        :alt: Python Package Index


.. image:: https://img.shields.io/discord/689541907621085198?logo=discord&logoColor=ffffff&color=7389D8
        :target: https://discord.com/channels/689541907621085198#
        :alt: Join us at Discord


About
=====


A library in Python for generating Sentinel-2 Angle Bands.

Sentinel-2 Angle Bands
----------------------

Generate Sentinel-2 Resampled Angle bands (Solar Azimuth, Solar Zenith, View Azimuth, View Zenith).

This script uses Sentinel-2 L1C products as input to generate angle bands (Solar Azimuth, Solar Zenith, View Azimuth and View Zenith). Originally the angles are provided as a 23x23 grid (5000 m resolution) in MTD_TL.xml file (Inside GRANULE folder). This script resample the angles through bilinear function to a 10 m spatial resolution.


Dependencies
------------

- affine
- numpy
- rasterio
- scikit-image

Installing via Git
------------------

```
python3 -m pip install git+https://github.com/brazil-data-cube/s2-angs
```

or

```
git clone https://github.com/brazil-data-cube/s2-angs
cd s2-angs
pip install .
```

Usage
-----

```
import s2_angs

#You can indicate a .zip, .SAFE or a folder containing S2 Data.
s2_angs.gen_s2_ang('/path/to/my/S2_file/S2B_MSIL1C_20191223T131239_N0208_R138_T23KMR_20191223T135458.zip')
```

Docker
------

Build the image from the root of this repository.

```
docker build -t s2angs .
```

run a docker container mounting an input-dir and provide the file name, e.g. S2A_MSIL1C_20201013T144731_N0209_R139_T19MGV_20201013T164036.SAFE.
The ouput will be generated in the same folder for .zip files or within GRANULE for .SAFE
```
docker run --rm -v /path/to/my/S2_file/:/mnt/input-dir s2angs S2A_MSIL1C_20201013T144731_N0209_R139_T19MGV_20201013T164036.SAFE
```

You can also provide an output folder to specify where the angles should be exported.
```
docker run --rm -v /path/to/my/S2_file/:/mnt/input-dir -v /path/to/my/output/:/mnt/output-dir s2angs S2A_MSIL1C_20201013T144731_N0209_R139_T19MGV_20201013T164036.SAFE
```

Results
-------
Intermediary files (matrix 23x23)
+++++++++++++++++++++++++++++++++
Solar_azimuth_23

.. image:: https://github.com/brazil-data-cube/s2-angs/blob/master/imgs/Solar_azimuth_23.png
        :width: 100
        :target: https://github.com/brazil-data-cube/s2-angs/blob/master/doc/imgs/Solar_azimuth_23.png
        :alt: Solar_azimuth_23

Solar_zenith_23

.. image:: https://github.com/brazil-data-cube/s2-angs/blob/master/imgs/Solar_zenith_23.png
        :width: 100
        :target: https://github.com/brazil-data-cube/s2-angs/blob/master/imgs/Solar_zenith_23.png
        :alt: Solar_azimuth_23

View_azimuth_23

.. image:: https://github.com/brazil-data-cube/s2-angs/blob/master/imgs/View_azimuth_23.png
        :width: 100
        :target: https://github.com/brazil-data-cube/s2-angs/blob/master/imgs/View_azimuth_23.png
        :alt: Solar_azimuth_23

View_zenith_23

.. image:: https://github.com/brazil-data-cube/s2-angs/blob/master/imgs/View_zenith_23.png
        :width: 100
        :target: https://github.com/brazil-data-cube/s2-angs/blob/master/imgs/View_zenith_23.png
        :alt: Solar_azimuth_23


Resampled
+++++++++
Solar_azimuth_resampled

.. image:: https://github.com/brazil-data-cube/s2-angs/blob/master/imgs/Solar_azimuth_resampled.png
        :width: 100
        :target: https://github.com/brazil-data-cube/s2-angs/blob/master/imgs/Solar_azimuth_resampled.png
        :alt: Solar_azimuth_23

Solar_zenith_resample

.. image:: https://github.com/brazil-data-cube/s2-angs/blob/master/imgs/Solar_zenith_resample.png
        :width: 100
        :target: https://github.com/brazil-data-cube/s2-angs/blob/master/imgs/Solar_zenith_resample.png
        :alt: Solar_azimuth_23

View_azimuth_resample

.. image:: https://github.com/brazil-data-cube/s2-angs/blob/master/imgs/View_zenith_azimuth_resample.png
        :width: 100
        :target: https://github.com/brazil-data-cube/s2-angs/blob/master/imgs/View_zenith_azimuth_resample.png
        :alt: Solar_azimuth_23

View_zenith_resample

.. image:: https://github.com/brazil-data-cube/s2-angs/blob/master/imgs/View_zenith_resample.png
        :width: 100
        :target: https://github.com/brazil-data-cube/s2-angs/blob/master/imgs/View_zenith_resample.png
        :alt: Solar_azimuth_23
