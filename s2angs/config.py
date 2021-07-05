#
# This file is part of Python Client Library for Sentinel-2 Angle Bands.
# Copyright (C) 2021 INPE.
#
# Python Client Library for Sentinel-2 Angle Bands is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Configuration options for Python Client Library for Sentinel-2 Angle Bands."""

import os

_BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def get_settings(env):
    """Get the given enviroment configuration."""
    return CONFIG.get(env)

class Config:
    """Base Configuration."""

    DEBUG = False
    TESTING = False

    SECRET_KEY = 'secret-key'

    S2ANGS_BASE_PATH_TEMPLATES = os.getenv('S2ANGS_BASE_PATH_TEMPLATES', 'templates')

    S2ANGS_SMTP_PORT = os.getenv('S2ANGS_SMTP_PORT', 587)
    S2ANGS_SMTP_HOST = os.getenv('S2ANGS_SMTP_HOST', None)

    S2ANGS_EMAIL_ADDRESS = os.getenv('S2ANGS_EMAIL_ADDRESS', None)
    S2ANGS_EMAIL_PASSWORD = os.getenv('S2ANGS_EMAIL_PASSWORD', None)

    S2ANGS_APM_APP_NAME = os.environ.get('BDC_AUTH_APM_APP_NAME', None)
    S2ANGS_APM_HOST = os.environ.get('BDC_AUTH_APM_HOST', None)
    S2ANGS_APM_SECRET_TOKEN = os.environ.get('BDC_AUTH_APM_SECRET_TOKEN', None)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'postgresql://postgres:postgres@localhost:5432/s2angs')

    OAUTH2_REFRESH_TOKEN_GENERATOR = True

    # Default OAuth 2.0 client app for Brazil Data Cube
    S2ANGS_DEFAULT_APP = 'bdc-auth'

    # Base path used in production (with proxy)
    APPLICATION_ROOT = os.getenv('S2ANGS_PREFIX', '/')
    SESSION_COOKIE_PATH = os.getenv('SESSION_COOKIE_PATH', '/')

    # Logstash configuration
    BDC_LOGSTASH_URL = os.getenv('BDC_LOGSTASH_URL', 'localhost')
    BDC_LOGSTASH_PORT = os.getenv('BDC_LOGSTASH_PORT', 5044)


class ProductionConfig(Config):
    """Production Mode."""


class DevelopmentConfig(Config):
    """Development Mode."""

    DEVELOPMENT = True


class TestingConfig(Config):
    """Testing Mode (Continous Integration)."""

    TESTING = True
    DEBUG = True


CONFIG = {
    "DevelopmentConfig": DevelopmentConfig(),
    "ProductionConfig": ProductionConfig(),
    "TestingConfig": TestingConfig()
}