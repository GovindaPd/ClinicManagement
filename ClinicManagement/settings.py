from pathlib import Path
from datetime import timedelta
import os
import environ
from django.core.exceptions import ImproperlyConfigured


BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False)
)
# In production if file does not exist it will pass and do nothing 
env.read_env(str(BASE_DIR / ".env.local"))

SECRET_KEY = env('SECRET_KEY', default='django-insecure-secret-key-5489112gdfasd54732641876@!#')

DEBUG = env('DEBUG')

try:
    DJANGO_ADMIN_URL = env('DJANGO_ADMIN_URL')
except ImproperlyConfigured:
    DJANGO_ADMIN_URL = 'admin'

WEBSITE_NAME = env('WEBSITE_NAME', default='My Clinic Store')

# when your app is behind Nginx / Load Balancer / Cloudflare / AWS ALB.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")   # env('ALLOWED_HOSTS').split(',')

INTERNAL_IPS = env.list('INTERNAL_IPS')

CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS')

USE_X_FORWARDED_HOST = True

APPEND_SLASH = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'home',
    'bahikhata',
    'cities_light',
    # 'django_ckeditor_5',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',   # for serving static files in production without using nginx or apache it usage cache to improve performance it must be above any other middleware and below security middleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

ROOT_URLCONF = 'ClinicManagement.urls'

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
                'home.context_processors.notification_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'ClinicManagement.wsgi.application'

# DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.sqlite3',
#             'NAME': BASE_DIR / 'db.sqlite3',
#         }
#     }

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': env("DB_ENGINE"),
            'NAME': env("DB_NAME"),
            'USER': env("DB_USER"),
            'PASSWORD': env("DB_PASSWORD"),
            'HOST': env("DB_HOST"),
            'PORT': env("DB_PORT"),
        }
    }

#in memory cache
# CACHES = {
#     "default": {
#         "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
#         "LOCATION": "unique-snowflake",
#     }
# }

#redis cache
# CACHES = {
#       "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": "redis://127.0.0.1:6379/1",
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",  #this is default client class for django-redis, you can use other client classes if needed
#             "PASSWORD": env('REDIS_PASSWORD', default=''),  # if your redis server requires password, set it in .env file and it will be used here, else it will be empty
#             "IGNORE_EXCEPTIONS": True,
#         }
#     }
# }

#for docker setup use service name in host(postgresql) or location(redis)
# db → PostgreSQL service name in database setting above for docker ("HOST": "db",)
# redis → Redis service name

LOGIN_REDIRECT_URL = 'index'
AUTH_USER_MODEL = 'home.User'

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

#pip install django-cities-light
CITIES_LIGHT_TRANSLATION_LANGUAGES = ['en',]
CITIES_LIGHT_INCLUDE_COUNTRIES = ['IN',]

# populate data in model if not using fixture then use this command to populate data for cities and countries
# python manage.py cities_light # on linux
# python manage.py cities_light_data # on windows


LANGUAGE_CODE = 'en-us'
TIME_ZONE = env('TIME_ZONE', default='Asia/Kolkata')
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')  # folder where collectstatic will copy everything

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'home', 'static')]   # tells Django where to look for source static files.

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER =  env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


SESSION_ENGINE = env('SESSION_ENGINE', default='django.contrib.sessions.backends.db')
SESSION_COOKIE_AGE = 3600 * 24 * 7  # 7 days (time until cookie expires)
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

SESSION_COOKIE_SECURE = True  # Set to True for HTTPS
CSRF_COOKIE_SECURE = True  # Enable for secure CSRF cookies


# ----------------------------------------------- #
# INSTALLED_APPS = ['django_ratelimit',]
# MIDDLEWARE = ["ratelimit.middleware.RatelimitMiddleware",]

# CACHES = {
#     "default": {
#         "BACKEND": "django.core.cache.backends.db.DatabaseCache",
#         "LOCATION": "ratelimit_cache",  # table name
#     }
# }

# RATELIMIT_USE_CACHE = "ratelimit"
# create cache table
# python manage.py createcachetable ratelimit_cache

# from django_ratelimit.decorators import ratelimit
# @ratelimit(key='post:email', rate='3/10m', block=True)
# @ratelimit(key='ip', rate='2/m', block=True)


#CELERY SETTINGS
# CELERY_BROKER_URL = 'redis://localhost:6379/0'
# CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
# -------------------------------------------------- #


# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': [
#         'rest_framework.authentication.SessionAuthentication',
#         'rest_framework.authentication.TokenAuthentication',
#         'rest_framework.authentication.BasicAuthentication',
#         # 'rest_authtoken.auth.AuthTokenAuthentication'
#         # 'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
#         'rest_framework_simplejwt.authentication.JWTAuthentication',
#     ],
#     'DEFAULT_PERMISSION_CLASSES': [
#         'rest_framework.permissions.IsAuthenticated',
#         'rest_framework.permissions.IsAdminUser',   #AllowAny
#     ],
#     'DEFAULT_RENDERER_CLASSES': [
#         'rest_framework.renderers.JSONRenderer',
#         'rest_framework.renderers.BrowsableAPIRenderer',
#     ]
# }


# REST_FRAMEWORK = {
#     'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
# 
#     'DEFAULT_AUTHENTICATION_CLASSES': [
#         'rest_framework_simplejwt.authentication.JWTAuthentication',
#     ],
# 
#     'DEFAULT_PERMISSION_CLASSES': [
#         'rest_framework.permissions.IsAuthenticated',
#     ],
# }

# SIMPLE_JWT = {
#     'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
#     'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
#     'ROTATE_REFRESH_TOKENS': True,
#     'BLACKLIST_AFTER_ROTATION': True,
#     # 'AUTH_HEADER_TYPES': ('Bearer',),
# }