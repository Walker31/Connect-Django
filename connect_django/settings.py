from pathlib import Path
import environ
import os
import dj_database_url

# Environment Variables Setup
env = environ.Env(
    DEBUG=(bool, False)
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

APPEND_SLASH = False
# Load .env file
environ.Env.read_env(BASE_DIR / '.env')

# Security
DEBUG = env("DEBUG")
ALLOWED_HOSTS = ['*']

# Rest Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ]   
}

# Media Configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

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
    'corsheaders',
    'storages',
    'user',
    'post',
    'matches',
    'spotify',
    'azureservice',
    'channels',
    'messaging'
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

# URLs and Templates
ROOT_URLCONF = 'connect_django.urls'

ASGI_APPLICATION = 'connect_django.asgi.application'

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

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}


WSGI_APPLICATION = 'connect_django.wsgi.application'

# Database
DATABASES = {
    'render' : 
        dj_database_url.config(default='postgresql://walker:kHoq4Gi8ulJVliKoZoeOmgCrmbqDhS7u@dpg-d06sumili9vc73en1j70-a.oregon-postgres.render.com/connect_n2h4')
    ,
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'Connect',
        'USER': 'postgres',
        'PASSWORD': 'aditya',
        'HOST': 'localhost',
        'PORT': '5432',
    },
    'azure': {
        'ENGINE': 'mssql',
        'NAME': 'Connect',
        'USER': 'Walker',
        'PASSWORD': env("AZURE_DB_PASSWORD"),
        'HOST': 'connect2.database.windows.net',
        'PORT': '1433',
        'OPTIONS':{
            'driver': 'ODBC Driver 17 for SQL Server'
        },
    },
}

# Password Validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static Files
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Azure Storage
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.azure_storage.AzureStorage",
        "OPTIONS": {
            "account_name": env("AZURE_ACCOUNT_NAME"),
            "account_key": env("AZURE_ACCOUNT_KEY"),
        }
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
AZURE_CONTAINER = env("AZURE_CONTAINER")
AZURE_CONNECTION_STRING = env('AZURE_CONNECTION_STRING')

SECRET_KEY = env('SECRET_KEY')


# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',  # You can change this to 'DEBUG' for more verbosity
        },
    },
}

