"""
Development settings – local DB, local file storage, DEBUG=True.
"""
from .base import *  # noqa: F401,F403
from decouple import config

DEBUG = True

ALLOWED_HOSTS+=["127.0.0.1"]

# ---------------------------------------------------------------------------
# Database (local Postgres)
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME":     config("DB_NAME", "rebt"),
        "USER":     config("DB_USER", "postgres"),
        "PASSWORD": config("DB_PASSWORD", "postgres"),
        "HOST":     config("DB_HOST", "localhost"),
        "PORT":     config("DB_PORT", "5432"),
    }
}

# ---------------------------------------------------------------------------
# File storage – local filesystem
# ---------------------------------------------------------------------------
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# ---------------------------------------------------------------------------
# Verbose logging
# ---------------------------------------------------------------------------
LOGGING["root"]["level"] = "DEBUG"  # type: ignore

# ---------------------------------------------------------------------------
# Email backend – console for dev
# ---------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"