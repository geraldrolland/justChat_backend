"""
Django settings for justChatBackend project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
from decouple import config
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-fnj208p9@29sgpbw&y(czelpg@+zb(g1f+sjijah4g+x8t#x8w'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["justchat-api.onrender.com", "localhost", "127.0.0.1"]


# Application definition

INSTALLED_APPS = [
    'daphne',
    'channels',
    'celery',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'justChat_api',
    'django_extensions',
    'rest_framework',
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
     "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'justChat_api.customemiddleware.IpLimiterMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]

# GOOGLE AUTHENTICATION CONFIGURATION
BASE_APP_URL = "https://justchat-0hms.onrender.com/home"
BASE_API_URL = "https://justchat-api.onrender.com"


# SMTP GMAIL CONFIGURATION
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465 #587
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")


GOOGLE_OAUTH2_CLIENT_ID = config("GOOGLE_OAUTH2_CLIENT_ID")
GOOGLE_OAUTH2_CLIENT_SECRET = config("GOOGLE_OAUTH2_CLIENT_SECRET")



# CORS CONFIGURATION
CORS_ALLOW_CREDENTIALS = True
AUTH_USER_MODEL = 'justChat_api.CustomUser'
ROOT_URLCONF = 'justChatBackend.urls'
CORS_ALLOWED_ORIGINS = [
"http://localhost:5173",
"https://justchat-0hms.onrender.com",
]


# justChatBackend/settings.py

from kombu import Queue

CELERY_TASK_QUEUES = (
    Queue('high_priority', routing_key='high_priority'),
    Queue('medium_priority', routing_key='medium_priority'),
    Queue('low_priority', routing_key='low_priority'),
)

CELERY_TASK_DEFAULT_QUEUE = 'low_priority'
CELERY_TASK_ROUTES = {
    'justChatBackend.tasks.send_user_otp': {'queue': 'high_priority'},
    'justChatBackend.tasks.medium_priority_task': {'queue': 'medium_priority'},
    'justChatBackend.tasks.low_priority_task': {'queue': 'low_priority'},
}



#Configuration for celery with Redis broker

CELERY_BROKER_URL = 'redis-11216.c277.us-east-1-3.ec2.redns.redis-cloud.com'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

#SESSION_COOKIE_AGE = 3600  # 2 minutes

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'justChatBackend.wsgi.application'
ASGI_APPLICATION = "justChatBackend.asgi.application"

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

import os

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
STATIC_URL = '/django_static/' 
STATIC_ROOT = BASE_DIR / 'django_static'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / "db.sqlite3",
    },
    #'default': {
    #    'ENGINE': 'django.db.backends.mysql',
    #    'NAME': config("DATABASE_NAME"),
    #    'USER': config("DATABASE_USER"),
    #    'PASSWORD': config("DATABASE_PASSWORD"),
    #    'HOSTNAME': 'localhost',
    #    'PORT': '3306',
    #   'OPTIONS': {
    #        'charset': 'utf8',
    #        'use_unicode': True,
    #    },
    #}

}



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


MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
STATIC_URL = '/django_static/' 
STATIC_ROOT = BASE_DIR / "staticfiles"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STORAGES = {
    # ...
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
          'LOCATION': 'redis://default:zzBAlSv81bcsrlalRIzDBwluKFRBdJio@redis-11216.c277.us-east-1-3.ec2.redns.redis-cloud.com:11216', # Adjust the IP and port if necessary
        
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'decode_responses': True,
        }
    }
}



REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        'rest_framework_simplejwt.authentication.JWTAuthentication',       
    ],

    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",

    ]
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# SESSION CONFIGURATIONS
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Default is using database sessions
# If you prefer caching the session, use: 'django.contrib.sessions.backends.cached_db'
SESSION_COOKIE_DOMAIN = None  # Use default if you're not setting a custom domain
SESSION_COOKIE_AGE = 60 * 60 * 24  # Sessions last for 1 day (24 hours)
SESSION_COOKIE_SECURE = False  # Set to True if using HTTPS in production
SESSION_COOKIE_HTTPONLY = True  # Ensures JavaScript can't access the session cookie
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Sessions persist after browser close
SESSION_SAVE_EVERY_REQUEST = True  # Save the session on every request (keeps it active)
#SESSION_COOKIE_SAMESITE = None



CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [('redis-11216.c277.us-east-1-3.ec2.redns.redis-cloud.com', 11216)],
        },
    },
}


from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=5),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,

    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti",

    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),

    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}