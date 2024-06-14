from .base import *
import dj_database_url

DEBUG = True

ALLOWED_HOSTS = ["*"]

DATABASES = {
    'default': {
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

db_from_env = dj_database_url.config(conn_max_age=600)

# Update DATABASES['default'] with the contents of db_from_env
DATABASES['default'].update(db_from_env)


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST_USER = "benmore@gmail.com"
