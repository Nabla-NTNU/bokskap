# pylint: disable=W0614,wildcard-import
"""
Production settings for skapsystem
"""
from os import environ as env
import pymysql
from .base import *

pymysql.install_as_MySQLdb()

DEBUG = bool(env.get('DEBUG', False))
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

DEBUG = bool(env.get('DEBUG', False))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env.get('MYSQL_DATABASE'),
        'USER': env.get('MYSQL_USER'),
        'PASSWORD': env.get('MYSQL_USER_PASSWORD'),
    }
}
