# -*- coding: utf-8 -*-
# Django settings for skapsystem project.

import os

DEBUG = True


ALLOWED_HOSTS = []
TIME_ZONE = 'Europe/Oslo'
LANGUAGE_CODE = 'nb'
SITE_ID = 1

USE_I18N = True
USE_L10N = True
USE_TZ = True

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static_collected')
STATIC_URL = '/static/'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

ADMIN_MEDIA_PREFIX = '/static/admin/'

SECRET_KEY = 'kw+&u!11%q6kfqofukwx^()ka943b=4ee9cb@urn^w$$9(brcn'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'skapsystem.urls'

WSGI_APPLICATION = 'skapsystem.wsgi.application'


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'bootstrap3',
    'grappelli',
    'locker',
    'dbbackup', # http://django-dbbackup.readthedocs.org/
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

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
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

TEST_RUNNER = 'django.test.runner.DiscoverRunner'
LOGIN_URL = "/admin/login"
