# pylint: disable=W0614,wildcard-import
"""
Production settings for skapsystem
"""
from os import environ as env
import pymysql
from .base import *

pymysql.install_as_MySQLdb()

DEBUG = bool(env.get('DEBUG', False))
ALLOWED_HOSTS = ['bokskap.nabla.no', '127.0.0.1']

SECRET_KEY = env.get("SECRET_KEY")

ADMINS = []
MANAGERS = ADMINS

DEBUG = bool(env.get('DEBUG', False))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env.get('MYSQL_DATABASE', 'bokskap'),
        'USER': env.get('MYSQL_USER', 'bokskap'),
        'PASSWORD': env.get('MYSQL_USER_PASSWORD', ''),
    }
}

LOG_FOLDER = VARIABLE_ROOT

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'file': {
            'level': 'INFO',
            'filters': [],
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': get_env(
                "DJANGO_LOG_PATH", "/var/log/django/bokskap/error.log"
            ),
            'when': 'W0',
            'formatter': 'default',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'locker': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        }
    },
    'formatters': {
        'default': {
            'format': '%(asctime)s %(levelname)s %(name)s: %(message)s',
        },
    },
}
