import pymysql
pymysql.install_as_MySQLdb()

from .base import *

DEBUG = False
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

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/bokskap/debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
