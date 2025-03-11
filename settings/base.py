import os 
from pathlib import Path
from django.urls import reverse_lazy

import cloudinary
import cloudinary.uploader
import cloudinary.api	


from decouple import config
from datetime import timedelta



SECRET = config('SECRET')
CLIENT_ID = config('CLIENT_ID')

# print(SECRET)
from django.core.management.utils import get_random_secret_key

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")


# SECURITY WARNING: don't run with debug turned on in production!

# Application definition

INSTALLED_APPS = [
    "daphne",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # user defined apps
    'main',
    'accounts',
    'quotes',
    'utils',
    'profiles',
    'admins',
    'property',
    'chat',
    
    'address',
    'mail_templated',
    'sslserver',
    
    'corsheaders',

    "phonenumber_field",
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'cloudinary_storage',
    'cloudinary',

    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt.token_blacklist',
    'dj_rest_auth',
    "dj_rest_auth.registration",

    'drf_spectacular',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "allauth.account.middleware.AccountMiddleware",
    # 'accounts.middleware.GoogleOAuthCallbackMiddleware',

]

ROOT_URLCONF = 'SproostApp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
                BASE_DIR / "templates",
            ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'SproostApp.wsgi.application'

ASGI_APPLICATION = 'SproostApp.asgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'static_cdn')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media_cdn/')


WHITENOISE_ROOT = os.path.join(BASE_DIR, 'static_cdn', 'root') 

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder'
)


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SITE_ID = 2

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)


ACCOUNT_ADAPTER = 'accounts.adapters.CustomAccountAdapter'
ACCOUNT_LOGOUT_ON_GET = True
SOCIALACCOUNT_LOGIN_ON_GET = False
SOCIALACCOUNT_ADAPTER = 'accounts.adapters.MySocialAccountAdapter'

# ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = True



ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_CHANGE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_SESSION_REMEMBER = True
SOCIALACCOUNT_QUERY_EMAIL = True

ACCOUNT_LOGOUT_REDIRECT_URL = reverse_lazy('account_login')
LOGIN_REDIRECT_URL = reverse_lazy('main:home')
ACCOUNT_SIGNUP_REDIRECT_URL = reverse_lazy('main:home')
# ACCOUNT_FORMS = {'signup': 'accounts.forms.CustomSignupForm'}

SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Use database-backed sessions
SESSION_COOKIE_AGE = 1209600  # Two weeks in seconds
SESSION_SAVE_EVERY_REQUEST = True  # Save the session to the database on every request



 
 
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "apikey"  # Use "apikey" as the username
EMAIL_HOST_PASSWORD = config('SENDGRID_API_KEY')
DEFAULT_FROM_EMAIL = config('FROM_EMAIL')



# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',

    'EXCEPTION_HANDLER': 'settings.utils.custom_exception_handler', 

}

print("BASE_DR")
print(BASE_DIR)

SPECTACULAR_SETTINGS = {
    'TITLE': 'My API',
    'DESCRIPTION': 'A sample API',
    'VERSION': '1.0.0',
}


SOCIALACCOUNT_PROVIDERS = {
    "google": {
        # For each OAuth based provider, either add a ``SocialApp``
        # (``socialaccount`` app) containing the required client
        # credentials, or list them here:
        'SCOPE': ['profile', 'email'],
        "APPS": [
            {
                "client_id":CLIENT_ID,
                "secret":SECRET,
                "key": ''
            },
        ],
        
        "AUTH_PARAMS": {
            "access_type": "online",
        },
    }
}

AUTH_USER_MODEL = 'accounts.User'

GOOGLE_API_KEY = config('GOOGLE_API_KEY')

CSRF_TRUSTED_ORIGINS = ['https://fdb9-105-113-33-126.ngrok-free.app']

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config("CLOUD_NAME"),
    'API_KEY': config("API_KEY"),
    'API_SECRET': config("API_SECRET")
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',  # This can be any unique identifier
    }
}

CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = [
    'https://44a8b72b893325a51bc6403f5837d712.serveo.net',
]

CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS',
]

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  # Customize token lifetime
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),    # Customize refresh token lifetime
    'ROTATE_REFRESH_TOKENS': True,                  # Rotate refresh tokens
    'BLACKLIST_AFTER_ROTATION': True,               # Blacklist old refresh tokens
    'AUTH_HEADER_TYPES': ('Bearer',),               # Header prefix for JWT tokens
    'BLACKLIST_AFTER_ROTATION': True, 
}

# CHANNEL_LAYERS = {
#     "default": {
#         "BACKEND": "channels_redis.core.RedisChannelLayer",
#         "CONFIG": {
#             "hosts": [("127.0.0.1", 6379)],  # Local Redis
#         },
#     },
# }

DOMAIN_NAME=config('DOMAIN_NAME', default='http://localhost:8000')
