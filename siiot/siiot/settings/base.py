"""
Django settings for pepup project.

Generated by 'django-admin startproject' using Django 3.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import sys, os
from os.path import abspath, basename, dirname, join, normpath
from siiot.loader import load_credential

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)

# Application definition

########## PATH CONFIGURATION
# Absolute filesystem path to the Django project directory:
DJANGO_ROOT = dirname(dirname(abspath(__file__)))

# Absolute filesystem path to the top-level project folder:
SITE_ROOT = dirname(DJANGO_ROOT)

# Site name:
SITE_NAME = basename(DJANGO_ROOT)

# Add our project to our pythonpath, this way we don't need to type our project
# name in our dotted import paths:
sys.path.append(DJANGO_ROOT)
########## END PATH CONFIGURATION


########## MEDIA CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
MEDIA_ROOT = normpath(join(SITE_ROOT, 'media'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
MEDIA_URL = '/media/'
########## END MEDIA CONFIGURATION


########## STATIC FILE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = normpath(join(SITE_ROOT, 'collected_static'))
# See: https://docs.
# djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (
    normpath(join(SITE_ROOT, 'statics')),
)

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'djangobower.finders.BowerFinder',
]

# See: http://django-compressor.readthedocs.io/en/latest/
# COMPRESS_ENABLED = False
# COMPRESS_URL = STATIC_URL
########## END STATIC FILE CONFIGURATION



INSTALLED_APPS = [
    # Default Django apps
    # third party admin before admin
    # 'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# apps
SECONDS_APPS = [
    # 'payment',
    'accounts',
    'custom_manage',
    'products.category',
    'products.shopping_mall',
    'products.supplymentary',
    'products.reply',
    'products',
    'crawler',
    'mypage',
    'payment',
    # 'api',
    # 'notice',
    # 'landing',
    'chats',
    # 'user_activity',
    # 'test'
]

# package
THIRD_APPS = [
    'rest_framework',
    'rest_framework.authtoken',

    # allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rest_auth.registration',

    'allauth.socialaccount.providers.instagram',
    'allauth.socialaccount.providers.kakao',
    'allauth.socialaccount.providers.google',
    # 'drf_yasg',

    'storages',

    'corsheaders',
    
    # 'toolbar'
    'debug_toolbar',

    # 'ckeditor'
    'ckeditor',
    'ckeditor_uploader',

    # django-imagekit
    'imagekit',
    'ajax_select',

    # selenium
    'selenium'
]

INSTALLED_APPS += SECONDS_APPS + THIRD_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'siiot.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates/'],
        # 'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                'core.template_loader.AppLoader',
            ],
        },
    },
]

WSGI_APPLICATION = 'siiot.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Default user model
AUTH_USER_MODEL = 'accounts.User'

# allauth settings
AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)

# router
DATABASE_ROUTERS = [
    'siiot.router.SiiotDataRouter'
]

SITE_ID = 1

# drf 토큰인증처
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',  # temp for web chats test
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'core.pagination.SiiotPagination',
    'PAGE_SIZE': 51
}


AWS_S3_HOST = 's3.ap-northeast-2.amazonaws.com'
STATIC_LOCATION = 'statics'
STATIC_URL = "https://%s/%s/" % (AWS_S3_HOST, STATIC_LOCATION)
# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'djangobower.finders.BowerFinder',
]


########## CKEDITOR CONFIGURATION
CKEDITOR_UPLOAD_PATH = "uploads/"

CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_JQUERY_URL = 'https://ajax.googleapis.com/ajax/libs/jquery/2.2.4/jquery.min.js'


CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline', 'Source', '-', 'Image'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink'],
            ['RemoveFormat', 'Source']
        ]
    }
}
########## END CKEDITOR CONFIGURATION


########## FCM DJANGO CONFIGURATION
FCM_DJANGO_SETTINGS = {
        "APP_VERBOSE_NAME": "siiot",
         # default: _('FCM Django')
        "FCM_SERVER_KEY": load_credential("FCM_SERVER_KEY", ""),
         # true if you want to have only one active device per registered user at a time
         # default: False
        "ONE_DEVICE_PER_USER": False,
         # devices to which notifications cannot be sent,
         # are deleted upon receiving error response from FCM
         # default: False
        "DELETE_INACTIVE_DEVICES": True,
}
########## FCM DJANGO CONFIGURATION

APPEND_SLASH = False

# toolbar
INTERNAL_IPS = ('127.0.0.1',)

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": ['redis://0.0.0.0:6379'],
        },
    },
}

# Celery
CELERY_BROKER_URL = 'redis://0.0.0.0:6379'
CELERY_RESULT_BACKEND = 'redis://0.0.0.0:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TAST_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Seoul'


MESSAGES_TO_LOAD = 15
