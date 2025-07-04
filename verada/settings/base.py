import os
from pathlib import Path
import environ
from datetime import timedelta

# Initialize environment variables
env = environ.Env(
    DEBUG=(bool, False)
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment from .env file
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = ['.vercel.app']
# ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'corsheaders',
    'drf_spectacular',

    #APPs
    'apps.users',
    'apps.common',
    'apps.agreements',
    'apps.core',
    'apps.waste_collectors',
    'apps.waste_generators',
    'apps.audits',
    'apps.waste_source_group',
    'apps.commodities',
    'storages',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# Storage

ROOT_URLCONF = 'verada.urls' 	

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.users.context_processors.user_logo',
                'apps.core.context_processors.sidebar_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'verada.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

#DATABASES = {
 #   'default': {
  #      'ENGINE': 'django.db.backends.sqlite3',
   #     'NAME': BASE_DIR / 'db.sqlite3',
    #}
#}

# Vercel 
DATABASES = {
    'postgres': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('DB_Name'),
        'USER': env('DB_user'),
        'PASSWORD': env('DB_password'),
        'HOST': env('DB_host'),
        'PORT': '5432',
    },
    'sqlite': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(BASE_DIR / "db.sqlite3"),
    },
}

# Local 
# DATABASES = {
#     'postgres': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'verada1',
#         'USER': 'postgres',
#         'PASSWORD': 'admin',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     },
#     'sqlite': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': str(BASE_DIR / "db.sqlite3"),
#     },
# }

 
DATABASES['default'] = DATABASES['postgres']


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# Static files
# STATIC_URL = '/static/'
# STATICFILES_DIRS = [BASE_DIR / 'static']
# STATIC_ROOT = os.path.join(BASE_DIR, '/static/')


STATIC_URL = '/staticfiles/'
#STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
#STATIC_ROOT = os.path.join(BASE_DIR, '/static/')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')    # Where collectstatic


# Media files
#MEDIA_URL = '/media/'
# MEDIA_URL = f"https://django-011.s3.us-east-1.amazonaws.com/"
# MEDIA_ROOT = BASE_DIR / 'media'
#MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'  # app_name.model_name

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'WasteFlow API',
    'DESCRIPTION': 'API documentation for Waste Recovery Compliance system',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

LOGIN_URL = '/login/'               # Where to redirect if not logged in
LOGIN_REDIRECT_URL = '/dashboard' # Where to go after login
LOGOUT_REDIRECT_URL = '/login/'    # After logout

DEFAULT_FROM_EMAIL = env('EMAIL_HOST_USER')
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.dreamhost.com'
EMAIL_PORT = 587  # or 465 for SSL
EMAIL_USE_TLS = True  # or EMAIL_USE_SSL = True if using 465
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')


# AWS S3 

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = 'us-east-1'  # e.g. 'ap-south-1'
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_QUERYSTRING_AUTH = False
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None

# Media files
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"
# MEDIA_ROOT = BASE_DIR / 'media'

