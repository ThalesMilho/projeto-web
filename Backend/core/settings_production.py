"""
Production-Ready Django Settings
Secure configuration using python-decouple for environment variable management.
"""

from pathlib import Path
import os
from decouple import config, Csv
from datetime import timedelta
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ==================== SECURITY CONFIGURATION ====================

# Secret Key (REQUIRED for production)
SECRET_KEY = config('SECRET_KEY', cast=str)

# Debug Mode (MUST be False in production)
DEBUG = config('DEBUG', default=False, cast=bool)

# Allowed Hosts (configure from environment)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='', cast=Csv()).split(',')

# Custom Admin URL (prevent brute-force attacks)
ADMIN_URL = config('ADMIN_URL', default='admin/')

# ==================== DATABASE CONFIGURATION ====================

# SECURITY: PostgreSQL ONLY - No fallback to SQLite
DATABASE_URL = config('DATABASE_URL')

# CRITICAL: Fail fast if PostgreSQL is not configured
if not DATABASE_URL:
    raise ImproperlyConfigured(
        "DATABASE_URL environment variable is required. "
        "This application requires PostgreSQL - SQLite fallback is disabled for security."
    )

# Parse and configure PostgreSQL with production settings
DATABASES = {
    'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
}

# ==================== APPLICATION CONFIGURATION ====================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    'django_filters',
    'whitenoise',
    
    # Local apps
    'accounts',
    'games',
]

# ==================== MIDDLEWARE CONFIGURATION ====================

MIDDLEWARE = [
    # Security middleware should be first
    'django.middleware.security.SecurityMiddleware',
    
    # CORS handling
    'corsheaders.middleware.CorsMiddleware',
    
    # Static file serving
    'whitenoise.middleware.WhiteNoiseMiddleware',
    
    # Django core middleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ==================== URL CONFIGURATION ====================

ROOT_URLCONF = 'core.urls'

# ==================== TEMPLATE CONFIGURATION ====================

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

WSGI_APPLICATION = 'core.wsgi.application'

# ==================== AUTHENTICATION CONFIGURATION ====================

AUTH_USER_MODEL = 'accounts.CustomUser'

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

# ==================== INTERNATIONALIZATION ====================

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# ==================== STATIC FILES CONFIGURATION ====================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Production static file storage
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==================== REST FRAMEWORK CONFIGURATION ====================

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    
    # Rate limiting
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '5/minute',
        'user': '60/minute',
    },
}

# ==================== CORS CONFIGURATION ====================

# Configure CORS origins from environment
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='', cast=Csv()).split(',')
CORS_ALLOW_CREDENTIALS = config('CORS_ALLOW_CREDENTIALS', default=False, cast=bool)

# ==================== JWT CONFIGURATION ====================

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,  # Use same secret key
}

# ==================== CSRF CONFIGURATION ====================

CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='', cast=Csv()).split(',')

# ==================== API INTEGRATION CONFIGURATION ====================

# SkalePay integration
SKALEPAY_SECRET_KEY = config('SKALEPAY_SECRET_KEY', cast=str)
SKALEPAY_PUBLIC_KEY = config('SKALEPAY_PUBLIC_KEY', cast=str)
SKALEPAY_BASE_URL = config('SKALEPAY_BASE_URL', 
                           default='https://api.conta.skalepay.com.br/v1', cast=str)

# Webhook configuration
WEBHOOK_URL_BASE = config('RENDER_EXTERNAL_URL', cast=str)
SKALEPAY_WEBHOOK_URL = f"{WEBHOOK_URL_BASE}/api/accounts/webhook/skalepay/"

# ==================== LOGGING CONFIGURATION ====================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'mask_sensitive_data': {
            '()': 'core.logging_filters.SensitiveDataFilter',
        },
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'production': {
            'format': '{asctime} {levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'filters': ['mask_sensitive_data'],
            'formatter': 'production' if not DEBUG else 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'production',
            'filters': ['mask_sensitive_data'],
        },
    },
    'root': {
        'handlers': ['console', 'file'] if not DEBUG else ['console'],
        'level': 'WARNING' if not DEBUG else 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'] if not DEBUG else ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'skalepay_integration': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# ==================== API DOCUMENTATION ====================

SPECTACULAR_SETTINGS = {
    'TITLE': 'PixLegal API',
    'DESCRIPTION': 'API de Gestão de Apostas e Financeiro',
    'VERSION': '1.0.0',
    'COMPONENT_SPLIT_REQUEST': True,
}

# ==================== SECURITY HEADERS ====================

if not DEBUG:
    # Production security headers
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = config('HSTS_SECONDS', default=31536000, cast=int)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = config('HSTS_INCLUDE_SUBDOMAINS', 
                                           default=True, cast=bool)
    SECURE_HSTS_PRELOAD = config('HSTS_PRELOAD', default=True, cast=bool)
    
    # SSL settings
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ['HTTP_X_FORWARDED_PROTO']

# ==================== EMAIL CONFIGURATION ====================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='localhost', cast=str)
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='', cast=str)
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='', cast=str)
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', 
                            default='noreply@pixlegal.com', cast=str)

# ==================== MONITORING ====================

# Sentry configuration (optional)
SENTRY_DSN = config('SENTRY_DSN', default='', cast=str)
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=config('SENTRY_TRACES_SAMPLE_RATE', default=0.1, cast=float),
    )
