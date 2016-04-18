from .production import *

import os

get_env = os.environ.get


DEBUG = bool(get_env('DEBUG', False))

if 'MYSQL_DATABASE' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': get_env('MYSQL_DATABASE'),
            'USER': get_env('MYSQL_USER'),
            'PASSWORD': get_env('MYSQL_USER_PASSWORD'),
        }
    }


STATIC_ROOT = get_env('STATIC_ROOT', STATIC_ROOT)
