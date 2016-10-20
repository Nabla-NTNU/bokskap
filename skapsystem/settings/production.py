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
        'NAME': 'bokskap_nabla_no',
        'USER': 'bokskap_nabla_no',
        'PASSWORD': '',
    }
}
