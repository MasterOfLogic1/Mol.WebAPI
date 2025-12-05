from pathlib import Path
from datetime import timedelta
from decouple import config
import dj_database_url
import os
from corsheaders.defaults import default_headers

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')
SMTP_SEND_MAIL_URL = config('SMTP_SEND_MAIL_URL')
SMTP_API_KEY = config('SMTP_API_KEY')
PORTAL_WEB_APP_URL = config('PORTAL_WEB_APP_URL')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

DEBUG = config('DEBUG', default=False, cast=bool)

# Get the database URL from environment variable
DATABASE_URL = config('DATABASE_URL')  # Ensure DATABASE_URL is set in .env or environment

DATABASES = {
    'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600, ssl_require=True)
}

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',  # Added for DRF
    'rest_framework_simplejwt',  # Added for JWT authentication
    'apps.account', 
    'apps.user_profile',
    'apps.course',
    'apps.blog',
    'apps.team',
    'apps.admin_panel',
    'drf_spectacular',
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = 'MolWebAPI.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # You can add template directories here
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

WSGI_APPLICATION = 'MolWebAPI.wsgi.application'



SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=200),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

# Use a custom user model for the accounts app
AUTH_USER_MODEL = 'account.User'

# Password validation
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

# REST framework configuration for JWT
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'MolWebAPI.utils.custom_exception_handler',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'MolWebAPI',
    'DESCRIPTION': 'API for Mol Web Application. Complete API documentation for Authentication, Courses, Blog, Team, and User Profile endpoints.',
    'VERSION': '1.0.0',
    
    # Add a URL to be displayed on Swagger
    'SERVERS': [
        {'url': 'http://127.0.0.1:8000/', 'description': 'Local Development Server'},
        {'url': 'https://web-production-6a37.up.railway.app/', 'description': 'Production Server'}  
    ],

    # Contact Information
    'CONTACT': {
        'name': 'Mol Support',
    },

    # License Information
    'LICENSE': {
        'name': 'MIT License',
        'url': 'https://opensource.org/licenses/MIT'
    },

    # Documentation customization options
    'COMPONENT_SPLIT_REQUEST': True,
    
    # Make schema publicly accessible
    'SERVE_PERMISSIONS': ['rest_framework.permissions.AllowAny'],
    'SERVE_AUTHENTICATION': None,
}

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


CORS_ALLOW_HEADERS = list(default_headers)

