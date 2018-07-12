import logging
from .common import *  # noqa

# Settings for Docker Development
# TODO: Use environment to override, not settings picker

ATTACHMENT_HOST = config('ATTACHMENT_HOST',
                         default='mdn-local.mozillademos.org')

INTERNAL_IPS = ('127.0.0.1', '192.168.10.1', '172.18.0.1')

# Default DEBUG to True, and recompute derived settings
DEBUG = config('DEBUG', default=True, cast=bool)
DEBUG_TOOLBAR = config('DEBUG_TOOLBAR', default=False, cast=bool)
DEBUG_PROPAGATE_EXCEPTIONS = DEBUG
PIPELINE['PIPELINE_ENABLED'] = config('PIPELINE_ENABLED', not DEBUG, cast=bool)
PIPELINE['PIPELINE_COLLECTOR_ENABLED'] = config('PIPELINE_COLLECTOR_ENABLED',
                                                not DEBUG, cast=bool)
TEMPLATES[1]['OPTIONS']['debug'] = DEBUG

LOG_LEVEL = logging.ERROR
PROTOCOL = config('PROTOCOL', default='https://')
DOMAIN = config('DOMAIN', default='developer-local.allizom.org')
SITE_URL = config('SITE_URL', default=PROTOCOL + DOMAIN)

# Elasticsearch related settings.
ES_DEFAULT_NUM_REPLICAS = 0
ES_DEFAULT_NUM_SHARDS = 1
ES_LIVE_INDEX = config('ES_LIVE_INDEX', default=True, cast=bool)

# Don't cache non-versioned static files in DEBUG mode
if DEBUG:
    WHITENOISE_MAX_AGE = 0
    if DEBUG_TOOLBAR:
        INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar',)
        MIDDLEWARE = list(MIDDLEWARE)
        common_index = MIDDLEWARE.index(
            'django.middleware.common.CommonMiddleware')
        MIDDLEWARE.insert(
            common_index + 1,
            'debug_toolbar.middleware.DebugToolbarMiddleware')
        DEBUG_TOOLBAR_INSTALLED = 1
