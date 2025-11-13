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
