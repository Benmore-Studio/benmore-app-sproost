from .base import *
import dj_database_url

DEBUG = False

ALLOWED_HOSTS = ["*"]



WHITENOISE_ROOT = os.path.join(BASE_DIR, 'static_cdn', 'root')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST_USER = "samuel@gmail.com"