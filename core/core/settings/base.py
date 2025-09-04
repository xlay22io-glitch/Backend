"""
Base settings shared by both dev and prod environments.
DO NOT put DEBUG, DATABASES, Whitenoise or any environment-specific
configuration here.
"""
from pathlib import Path
from datetime import timedelta
import os
import json
import base64
import logging

from decouple import config
from google.oauth2 import service_account

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:8000"
]

# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # repo root

# -----------------------------------------------------------------------------
# Core
# -----------------------------------------------------------------------------
SECRET_KEY = config("DJANGO_SECRET_KEY")
DEBUG = False  # overridden in dev.py

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

ROOT_URLCONF = "core.urls"
WSGI_APPLICATION = "core.wsgi.application"

# -----------------------------------------------------------------------------
# Applications
# -----------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "storages",
    'django_crontab',
]
LOCAL_APPS = [
    "authentication",
    "accounts"
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# -----------------------------------------------------------------------------
# Middleware
# -----------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# -----------------------------------------------------------------------------
# Templates
# -----------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
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

# -----------------------------------------------------------------------------
# Static & media
# -----------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / 'media'

# -----------------------------------------------------------------------------
# REST Framework & JWT
# -----------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "BLACKLIST_APP": "authentication",
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# -----------------------------------------------------------------------------
# Google Cloud Storage credentials helper
# -----------------------------------------------------------------------------


def _load_gcs_credentials():
    path = config("GCS_CREDENTIALS_PATH", default=None)
    b64 = config("GOOGLE_CREDENTIALS_BASE64", default=None)
    try:
        if path:
            with open(path, "r", encoding="utf-8") as fh:
                info = json.load(fh)
        elif b64:
            info = json.loads(base64.b64decode(b64).decode("utf-8"))
        else:
            return None
        return service_account.Credentials.from_service_account_info(info)
    except Exception as exc:  # pragma: no cover
        logging.error("Failed to load GCS credentials: %s", exc)
        return None


GS_CREDENTIALS = _load_gcs_credentials()
DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

# -----------------------------------------------------------------------------
# Logging – console by default (prod adds file handler)
# -----------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
# ---------------------------------------------------------------------------
# Email backend – configuration for email support
# ---------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

AUTH_USER_MODEL = 'authentication.CustomUser'

CRONJOBS = [
    # Run every Monday at 00:01
    ('1 0 * * 1', 'accounts.cron.reset_weekly_bonuses')
]


# CRONJOBS = [
#     # Every minute
#     ('* * * * *', 'accounts.cron.reset_weekly_bonuses',
#      '>> /tmp/weekly_bonus.log 2>&1')
# ]
