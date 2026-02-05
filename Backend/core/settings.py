from pathlib import Path
import os
from dotenv import load_dotenv
from datetime import timedelta 
import dj_database_url

load_dotenv() 

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback')

DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['*']  

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',  
    'corsheaders',
    'accounts',
    'drf_spectacular',  
    'django_filters',  
    'games',
]



MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',        
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
     
    
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',    
    'django.middleware.clickjacking.XFrameOptionsMiddleware', 
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# Default: local SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
if os.environ.get("DATABASE_URL"):
    DATABASES['default'] = dj_database_url.parse(os.environ.get("DATABASE_URL"))
# If DATABASE_URL is present (e.g. Render), use it for production
database_url = os.getenv("DATABASE_URL")
if database_url:
    DATABASES['default'] = dj_database_url.config(
        default=database_url,
        conn_max_age=600,
        ssl_require=True
    )


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

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny', 
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication', 
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',

    # --- RATE LIMITING ---
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '5/minute',
        'user': '60/minute'
    }
}

CORS_ALLOW_ALL_ORIGINS = True

AUTH_USER_MODEL = 'accounts.CustomUser'

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60), # O "crachá" dura 60 minutos
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),    # A renovação dura 1 dia
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
}

CSRF_TRUSTED_ORIGINS = [
    'https://*.ngrok-free.app',
]

# --- LOGGING CONFIGURATION (Segurança / LGPD) ---
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'mask_sensitive_data': {
            '()': 'core.logging_filters.SensitiveDataFilter', # Aponta para o arquivo que criamos
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'filters': ['mask_sensitive_data'], # Aplica a máscara no terminal
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO', # Em produção, mudamos para 'WARNING'
    },
}

SKALEPAY_SECRET_KEY = os.getenv('SKALEPAY_SECRET_KEY', '')
SKALEPAY_PUBLIC_KEY = os.getenv('SKALEPAY_PUBLIC_KEY', '')
SKALEPAY_BASE_URL = os.getenv('SKALEPAY_BASE_URL', 'https://api.conta.skalepay.com.br/v1')
WEBHOOK_URL_BASE = os.getenv('RENDER_EXTERNAL_URL', 'https://projeto-web-izeu.onrender.com')
SPECTACULAR_SETTINGS = {
    'TITLE': 'PixLegal API',
    'DESCRIPTION': 'API de Gestão de Apostas e Financeiro',
    'VERSION': '1.0.0',
    'COMPONENT_SPLIT_REQUEST': True,
}


# --- CONFIGURAÇÕES DE ARQUIVOS ESTÁTICOS (ADICIONAR NO FINAL) ---
import os  # Garante que o os está disponível aqui

# URL usada pelo navegador para acessar os arquivos
STATIC_URL = '/static/'

# Pasta onde o Django vai reunir todos os arquivos (Obrigatório para o comando funcionar)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Configuração do WhiteNoise para comprimir e servir os arquivos em produção
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- SKALEPAY / FINANCEIRO (integração) ---
SKALEPAY_SECRET_KEY = os.getenv('SKALEPAY_SECRET_KEY', SKALEPAY_SECRET_KEY if 'SKALEPAY_SECRET_KEY' in globals() else '')
SKALEPAY_WEBHOOK_URL = os.getenv('SKALEPAY_WEBHOOK_URL', f"{WEBHOOK_URL_BASE}/api/accounts/webhook/skalepay/")

# Logging adicional para auditoria financeira
LOGGING.setdefault('formatters', {})
LOGGING['formatters'].setdefault('verbose', {
    'format': '{levelname} {asctime} {module} {message}',
    'style': '{',
})

LOGGING.setdefault('handlers', {})
LOGGING['handlers'].setdefault('file', {
    'level': 'INFO',
    'class': 'logging.FileHandler',
    'filename': os.path.join(BASE_DIR, 'financeiro.log'),
    'formatter': 'verbose',
})

LOGGING.setdefault('loggers', {})
LOGGING['loggers'].setdefault('skalepay_integration', {
    'handlers': ['console', 'file'],
    'level': 'INFO',
    'propagate': True,
})
