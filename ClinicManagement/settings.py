from pathlib import Path
from datetime import timedelta
import os


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-71-l=n95)01g*_w96muslvj10mo^v)=7fyz#s741qn6d3wv&5m'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

WEBSITE_NAME = "localhost"
ALLOWED_HOSTS = ['*']

LOGIN_REDIRECT_URL = 'home'
APPEND_SLASH=True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'home',
    'cities_light',
    # 'rest_framework',
    # 'rest_framework_swagger',
    # 'drf_spectacular',
    # 'rest_framework.authtoken',
    # 'rest_auth',
    # 'rest_authtoken',
    # 'rest_framework_simplejwt',
    #'rest_framework_simplejwt.token_blacklist',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',    #APPEND_SLASH=True
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'home.middleware.BlockUserMiddleware',
]

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
            ],
        },
    },
]

WSGI_APPLICATION = 'ClinicManagement.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',    #postgres
    }
}
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

#CITIES_LIGHT_TRANSLATION_LANGUAGES = ['en', 'es']
CITIES_LIGHT_INCLUDE_COUNTRIES = ['IN',]
# populate data in model 
# python manage.py cities_light

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'home', 'static')]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



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
# }

# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': [
#         'rest_framework_simplejwt.authentication.JWTAuthentication',
#     ],
# }

# SIMPLE_JWT = {
#     'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
#     'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
#     'ROTATE_REFRESH_TOKENS': True,
#     'BLACKLIST_AFTER_ROTATION': True,
#     # 'AUTH_HEADER_TYPES': ('Bearer',),  # Token type prefix in headers
# }


# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'   #'mail.justapay.in'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'govinda@singhsoft.com'
EMAIL_HOST_PASSWORD = 'igvjublvmjrlupkj'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Store sessions in DB
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