"""
Production settings – Heroku Postgres, Google Cloud Storage, Whitenoise.
"""
from .base import *  # noqa: F401,F403
import dj_database_url
from decouple import config

DEBUG = False

# ---------------------------------------------------------------------------
# Database – Heroku connection string
# ---------------------------------------------------------------------------
DATABASES = {
    "default": dj_database_url.config(conn_max_age=600, ssl_require=True)
}

# ---------------------------------------------------------------------------
# Allowed hosts & security flags
# ---------------------------------------------------------------------------
ALLOWED_HOSTS = ["test-rebt-5c0ba7e6b65b.herokuapp.com"]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://rebt-frontend.vercel.app",
]

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "https://rebt-frontend.vercel.app",
]

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24  # 1 day
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# ---------------------------------------------------------------------------
# Whitenoise for static files
# ---------------------------------------------------------------------------
MIDDLEWARE = ["whitenoise.middleware.WhiteNoiseMiddleware"] + MIDDLEWARE  # noqa
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ---------------------------------------------------------------------------
# Google Cloud Storage buckets
# ---------------------------------------------------------------------------
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.gcloud.GoogleCloudStorage",
        "OPTIONS": {
            "project_id": config("GCS_PROJECT_ID"),
            "bucket_name": config("GCS_MEDIA_BUCKET"),
            "credentials": GS_CREDENTIALS,  # noqa
        },
    },
    "staticfiles": {
        "BACKEND": "storages.backends.gcloud.GoogleCloudStorage",
        "OPTIONS": {
            "project_id": config("GCS_PROJECT_ID"),
            "bucket_name": config("GCS_STATIC_BUCKET"),
            "credentials": GS_CREDENTIALS,  # noqa
        },
    },
}

# ---------------------------------------------------------------------------
# Logging to file for errors
# ---------------------------------------------------------------------------
LOGGING["handlers"]["file"] = {  # type: ignore
    "class": "logging.FileHandler",
    "level": "ERROR",
    "filename": BASE_DIR / "error.log",  # noqa: F405
}
LOGGING["root"]["handlers"] += ["file"]  # type: ignore

# ---------------------------------------------------------------------------
# Email backend – console for prod
# ---------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"