from pathlib import Path
from django.contrib.messages import constants as messages

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-lj*+-4$_0h!imqr3&mi88mu&voq4lnb9f&hy^nj5^g0h7u_++m'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000', 'http://localhost:8000']
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'administrador',
    'database',
    'login',
    'citas',
    'horarios',
    'medico',
    'paciente',
]

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "Integrador" / "static",
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',             # respaldo por username/email si lo usas
]

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'          # ajusta a tu vista
LOGOUT_REDIRECT_URL = 'login'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'Integrador.middleware.SessionLoginRequiredMiddleware',
]

ROOT_URLCONF = 'Integrador.urls'

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

WSGI_APPLICATION = 'Integrador.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


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

TIME_ZONE = 'America/Lima'

USE_I18N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / "templates",
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',       # ← OBLIGATORIO
                'django.contrib.auth.context_processors.auth',      # ← OBLIGATORIO
                'django.contrib.messages.context_processors.messages', # ← OBLIGATORIO
            ],
        },
    },
]

MESSAGE_TAGS = {
    messages.DEBUG: "secondary",
    messages.INFO: "primary",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "danger",
}

# ============================================================
# CONFIGURACIÓN TWILIO (RF12: Notificaciones SMS)
# ============================================================
# Obtener desde variables de entorno o .env
import os

# Opción A: Usar credenciales de Twilio reales
#Reemplazar el segundo '' con las credenciales de tu cuenta, caso contrario usa esas de mi cuenta.
#Preferible crea tu cuenta xddd

# QUITA EL "#" antes de TWILIO_ACCOUNT...
#TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', 'TU_TOKEN_AQUI')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', 'NUMERO AQUI')

# URL para encuestas de satisfacción (RF16). Cámbiala por tu Google Form o similar.
SURVEY_URL = os.getenv('SURVEY_URL', 'https://forms.gle/jaA3eBTqEZKHLwtV6')

# Opción B: Para testing sin Twilio real, descomenta estas líneas y comenta las de arriba:
# TWILIO_ACCOUNT_SID = 'test_account_sid'
# TWILIO_AUTH_TOKEN = 'test_auth_token'
# TWILIO_PHONE_NUMBER = '+1234567890'
# ============================================================
# CRON – RF10 Recordatorios escalonados
# ============================================================
CRONJOBS = [
    ('*/10 * * * *', 'citas.tasks.procesar_recordatorios'),
]
