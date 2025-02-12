from .base import *
import dj_database_url
from decouple import config


DEBUG = True

ALLOWED_HOSTS = ["*"]


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
    }
}
# DATABASE_URL= config('DATABASE_URL')
# DATABASES = {'default':dj_database_url.parse(DATABASE_URL, conn_max_age=600)}

# print(DATABASE_URL)

# Update DATABASES['default'] with the contents of db_from_env
db_from_env = dj_database_url.config(conn_max_age=600)
DATABASES['default'].update(db_from_env)


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST_USER = "benmore@gmail.com"
