#!/usr/bin/env bash
#
# This file is part of Python Client Library for Sentinel-2 Angle Bands.
# Copyright (C) 2021 INPE.
#
# Python Client Library for Sentinel-2 Angle Bands is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

pydocstyle s2angs examples tests setup.py && \
isort s2angs examples tests setup.py --check-only --diff && \
check-manifest --ignore ".travis.yml,.drone.yml,.readthedocs.yml" && \
sphinx-build -qnW --color -b doctest docs/sphinx/ docs/sphinx/_build/doctest && \
pytest
