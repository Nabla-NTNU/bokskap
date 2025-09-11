# pylint: disable=W0614,wildcard-import
"""
Development settings for skapsystem
"""
from .base import *

DEBUG = True

# Choose Nabla_email_backend for the gmail api, or console to see
#   in the terminal where you run the server
# EMAIL_BACKEND = "lib.nabla_email_backend.Nabla_email_backend"
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


ALLOWED_HOSTS = ["bokskap.nabla.no", "localhost", "127.0.0.1"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'skapsystem.db',
    }
}
