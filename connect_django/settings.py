from pathlib import Path
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
    'render': dj_database_url.parse(env('RENDER_DATABASE_URL')),
    'post': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('LOCAL_DB_NAME'),
        'USER': env('LOCAL_DB_USER'),
        'PASSWORD': env('LOCAL_DB_PASSWORD'),
        'HOST': env('LOCAL_DB_HOST'),
        'PORT': env('LOCAL_DB_PORT'),
    },
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'Connect',
        'USER': 'Walker',
        'PASSWORD': env('AZURE_DB_PASSWORD'),
        'HOST': 'connect2.database.windows.net',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 18 for SQL Server',
            'encrypt': True,
            'trust_server_certificate': False,
            'connection_timeout': 30,
        },
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
        'rest_framework.authentication.TokenAuthentication',
    ]
}

# Static & Media
STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
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
AZURE_CONNECTION_STRING = env("AZURE_CONNECTION_STRING")

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
