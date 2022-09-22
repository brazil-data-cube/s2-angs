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


Installation
============


Development installation
------------------------


Pre-Requirements
++++++++++++++++


The ``Sentinel-2 Angle Bands`` (``s2angs``) depends essentially on:

- affine

- numpy

- rasterio

- scikit-image


Clone the software repository
+++++++++++++++++++++++++++++


Use ``git`` to clone the software repository::

    git clone https://github.com/brazil-data-cube/s2-angs.git


Install s2-angs in Development Mode
+++++++++++++++++++++++++++++++++++++++


Go to the source code folder::

    cd s2-angs


Install in development mode::

    pip3 install -e .[all]


.. note::

    If you want to create a new *Python Virtual Environment*, please, follow this instruction:

    *1.* Create a new virtual environment linked to Python 3.7::

        python3.7 -m venv venv


    **2.** Activate the new environment::

        source venv/bin/activate


    **3.** Update pip and setuptools::

        pip3 install --upgrade pip

        pip3 install --upgrade setuptools


Installing via Git
------------------

.. code-block:: console

    python3 -m pip install git+https://github.com/brazil-data-cube/s2-angs


or

.. code-block:: console

    git clone https://github.com/brazil-data-cube/s2-angs
    cd s2-angs
    pip install .


Building a Docker image
-----------------------

Build the image from the root of this repository.

.. code-block:: console

    docker build -t s2angs .
