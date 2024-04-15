from .base import *
import dj_database_url

DEBUG = False

ALLOWED_HOSTS = ["*"]

db_from_env = dj_database_url.config(conn_max_age=600)

# Update DATABASES['default'] with the contents of db_from_env
DATABASES['default'].update(db_from_env)


WHITENOISE_ROOT = os.path.join(BASE_DIR, 'static_cdn', 'root')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST_USER = "samuel@gmail.com"