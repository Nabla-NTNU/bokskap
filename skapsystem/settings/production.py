import pymysql
pymysql.install_as_MySQLdb()

from .base import *

import os
get_env = os.environ.get

DEBUG = bool(get_env('DEBUG', False))
ALLOWED_HOSTS = ['bokskap.nabla.no']

ADMINS = (
    ('Øystein Hiåsen', 'hiasen@stud.ntnu.no'),
)
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bokskap',
        'USER': 'bokskap',
        'PASSWORD': '',
    }
}

DEBUG = bool(get_env('DEBUG', False))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': get_env('MYSQL_DATABASE'),
        'USER': get_env('MYSQL_USER'),
        'PASSWORD': get_env('MYSQL_USER_PASSWORD'),
    }
}
