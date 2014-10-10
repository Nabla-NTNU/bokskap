from .base import *

DEBUG = False
TEMPLATE_DEBUG = False

ADMINS = (
    ('Øystein Hiåsen', 'hiasen@stud.ntnu.no'),
)
MANAGERS = ADMINS

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemCachedCache',
        'LOCATION': '127.0.0.1:11211',
        'KEY_PREFIX': 'bokskap',
    }
}
