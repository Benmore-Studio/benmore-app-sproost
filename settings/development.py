from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost',
    '127.0.0.1',
    '44a8b72b893325a51bc6403f5837d712.serveo.net',]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

