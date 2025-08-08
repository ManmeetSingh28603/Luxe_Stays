"""
Optimized Django settings for Luxe Stays India project.
Enhanced with security, performance, and modern best practices.
"""

import os
from pathlib import Path
from decouple import config
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

# Enhanced allowed hosts with better security
ALLOWED_HOSTS = [
    'luxestaysindia.com',
    'www.luxestaysindia.com',
    'luxestays-production.up.railway.app',
    'luxestaysindia.vercel.app',
    'luxestaysindia-git-vercel.vercel.app',
    'luxestaysindia-git-main.vercel.app',
    '127.0.0.1',
    'localhost',
]

# Enhanced CSRF protection
CSRF_TRUSTED_ORIGINS = [
    'https://luxestaysindia.com',
    'https://www.luxestaysindia.com',
    'https://luxestaysindia-production.up.railway.app',
    'https://luxestaysindia.vercel.app',
    'https://luxestaysindia-git-vercel.vercel.app',
    'https://luxestaysindia-git-main.vercel.app',
]

# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'
X_CONTENT_TYPE_OPTIONS = 'nosniff'

# SSL/HTTPS settings (for production)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Enhanced cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'cache'),
        'TIMEOUT': 300,  # 5 minutes default
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
            'CULL_FREQUENCY': 3,  # 1/3 of entries removed when max is reached
        }
    }
}

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',  # SEO
    'django.contrib.humanize',  # Human-readable formatting
    'website',
    'tailwind',
    'theme',
]

# Enhanced middleware stack
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Custom middleware for analytics
    'website.middleware.AnalyticsMiddleware',
]

# Tailwind configuration
TAILWIND_APP_NAME = 'theme'
NPM_BIN_PATH = r"C:\Program Files\nodejs\npm.cmd"
INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]

# Enhanced static files configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

ROOT_URLCONF = 'luxestays_project.urls'

# Enhanced templates configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Custom context processors
                'website.context_processors.site_settings',
                'website.context_processors.analytics',
            ],
        },
    },
]

WSGI_APPLICATION = 'luxestays_project.wsgi.application'

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 20,  # Database timeout
        }
    }
}

# Enhanced password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
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
TIME_ZONE = 'Asia/Kolkata'  # Indian timezone
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static/',
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Enhanced email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtpout.secureserver.net'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_TIMEOUT = 20

# Enhanced logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'website': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Session configuration
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = False

# File upload configuration
FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440  # 2.5MB
FILE_UPLOAD_TEMP_DIR = os.path.join(BASE_DIR, 'temp')
DATA_UPLOAD_MAX_MEMORY_SIZE = 2621440  # 2.5MB

# Security settings
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_HOST = None

# Performance settings
CONN_MAX_AGE = 60  # Database connection pooling
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# Custom settings
SITE_NAME = "Luxe Stays India"
SITE_DESCRIPTION = "Luxury Content Creation & Social Media Marketing for Hospitality"
INSTAGRAM_USERNAME = "luxestaysindia"

# API settings
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "instagram120.p.rapidapi.com")

# Analytics settings
GOOGLE_ANALYTICS_ID = os.getenv("GOOGLE_ANALYTICS_ID")
FACEBOOK_PIXEL_ID = os.getenv("FACEBOOK_PIXEL_ID")

# Maintenance mode
MAINTENANCE_MODE = config('MAINTENANCE_MODE', default=False, cast=bool)
MAINTENANCE_MESSAGE = config('MAINTENANCE_MESSAGE', default="Site is under maintenance. Please check back soon.")

# Cache timeouts
CACHE_TIMEOUTS = {
    'instagram_data': 60 * 60 * 24 * 5,  # 5 days
    'excel_data': 60 * 60 * 24,  # 1 day
    'page_cache': 60 * 15,  # 15 minutes
}

# Rate limiting (if using django-ratelimit)
RATELIMIT_ENABLE = config('RATELIMIT_ENABLE', default=True, cast=bool)
RATELIMIT_USE_CACHE = 'default'

# Error reporting
ADMINS = [
    ('Admin', os.getenv('ADMIN_EMAIL', 'admin@luxestaysindia.com')),
]

# Create logs directory if it doesn't exist
os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'temp'), exist_ok=True) 