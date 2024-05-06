from .base import *
import dj_database_url

DEBUG = True

ALLOWED_HOSTS = ["*"]

DATABASES = {
    'default': {
    }
}

db_from_env = dj_database_url.config(conn_max_age=600)

# Update DATABASES['default'] with the contents of db_from_env
DATABASES['default'].update(db_from_env)


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST_USER = "benmore@gmail.com"