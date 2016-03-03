import pymysql
pymysql.install_as_MySQLdb()

from .base import *

DEBUG = False

ADMINS = (
    ('Øystein Hiåsen', 'hiasen@stud.ntnu.no'),
)
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bokskap_nabla_no',
        'USER': 'bokskap_nabla_no',
        'PASSWORD': '',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'KEY_PREFIX': 'bokskap',
    }
}
