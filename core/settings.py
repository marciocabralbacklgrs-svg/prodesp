from pathlib import Path
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

# ─── Segurança ────────────────────────────────────────────────────────────────
SECRET_KEY    = config('SECRET_KEY')
DEBUG         = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# ─── Salesforce ───────────────────────────────────────────────────────────────
SF_INSTANCE_URL  = config('SF_INSTANCE_URL')
SF_CLIENT_ID     = config('SF_CLIENT_ID')
SF_CLIENT_SECRET = config('SF_CLIENT_SECRET')

# ─── Orquestrador ─────────────────────────────────────────────────────────────
ORQUESTRADOR_API_URL       = config('ORQUESTRADOR_API_URL')
ORQUESTRADOR_CLIENT_ID     = config('ORQUESTRADOR_CLIENT_ID',     default='')
ORQUESTRADOR_CLIENT_SECRET = config('ORQUESTRADOR_CLIENT_SECRET', default='')

# ─── Apps ─────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'buscador',
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'pt-br'
TIME_ZONE     = 'America/Sao_Paulo'
USE_I18N      = True
USE_TZ        = True

# ─── Static ───────────────────────────────────────────────────────────────────
STATIC_URL       = 'static/'
STATIC_ROOT      = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── Funcionalidades opcionais ────────────────────────────────────────────────
ENABLE_VLIBRAS = config('ENABLE_VLIBRAS', default=False, cast=bool)
