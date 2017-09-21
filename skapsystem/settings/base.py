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
VARIABLE_ROOT = os.environ.get("VARIABLE_ROOT", PROJECT_ROOT)

STATIC_ROOT = os.path.join(VARIABLE_ROOT, 'static_collected')
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
    'locker',
    'dbbackup',  # http://django-dbbackup.readthedocs.org/
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
            'filename': os.path.join(LOG_FOLDER, 'info.log'),
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

TEST_RUNNER = 'django.test.runner.DiscoverRunner'
LOGIN_URL = "/admin/login"
