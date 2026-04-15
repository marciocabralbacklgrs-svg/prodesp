"""
Trecho para adicionar ao settings.py do projeto Django.

Instale: pip install python-decouple
"""

from decouple import config

# ─── Salesforce ───────────────────────────────────────────────────────────────
SF_INSTANCE_URL  = config("SF_INSTANCE_URL")
SF_CLIENT_ID     = config("SF_CLIENT_ID")
SF_CLIENT_SECRET = config("SF_CLIENT_SECRET")

# ─── Orquestrador ─────────────────────────────────────────────────────────────
ORQUESTRADOR_API_URL       = config("ORQUESTRADOR_API_URL")
ORQUESTRADOR_CLIENT_ID     = config("ORQUESTRADOR_CLIENT_ID")
ORQUESTRADOR_CLIENT_SECRET = config("ORQUESTRADOR_CLIENT_SECRET")

# ─── App instalado ────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    # ... apps existentes ...
    "buscador",
]

# ─── Static files ─────────────────────────────────────────────────────────────
# Adicione o diretório onde buscador.django.js será copiado:
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
# Estrutura esperada: static/buscador/buscador.django.js

# ─── Templates ────────────────────────────────────────────────────────────────
# O app usa templates próprios; certifique-se de que APP_DIRS está True:
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,   # <-- obrigatório para carregar templates do app
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
