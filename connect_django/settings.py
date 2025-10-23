from pathlib import Path
from datetime import timedelta
import environ
import dj_database_url

# Environment Setup
env = environ.Env(
    DEBUG=(bool, False)
)
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(BASE_DIR / '.env')

# Basic Config
DEBUG = env('DEBUG')
SECRET_KEY = env('SECRET_KEY')
ALLOWED_HOSTS = ['*']
APPEND_SLASH = False

# Installed Apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'daphne',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'storages',
    'user',
    'post',
    'matches',
    'spotify',
    'azureservice',
    'channels',
    'messaging',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'connect_django.urls'
ASGI_APPLICATION = 'connect_django.asgi.application'
WSGI_APPLICATION = 'connect_django.wsgi.application'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'Templates'],
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

# Databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('LOCAL_DB_NAME'),
        'USER': env('LOCAL_DB_USER'),
        'PASSWORD': env('LOCAL_DB_PASSWORD'),
        'HOST': env('LOCAL_DB_HOST'),
        'PORT': env('LOCAL_DB_PORT'),
    },
    'aws': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'Connect',
        'USER': 'Walker',
        'PASSWORD': env('AWS_DB_PASSWORD'),
        'HOST': '43.204.170.91',
        'PORT': '5432',
        'OPTIONS' :{
            'sslmode' : 'require'
        }
    },
}

# Channel Layers
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ]
}

# Static & Media
STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

GOOGLE_CLIENT_ID = "722853174837-v2deis0cugj96kkehvoegef7ldkqd3oo.apps.googleusercontent.com"

STORAGES = {
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# CORS
CORS_ALLOW_ALL_ORIGINS = True

# Timezone and Language
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'loggers': {'django': {'handlers': ['console'], 'level': 'INFO'}},
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=21),
    'ROTATE_REFRESH_TOKEN': True,
    'BLACKLIST_AFTER_ROTATION':True
}