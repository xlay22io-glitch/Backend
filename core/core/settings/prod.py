"""
Production settings – Heroku Postgres, Google Cloud Storage, Whitenoise.
"""
from .base import *  # noqa: F401,F403
import dj_database_url
from urllib.parse import urlparse
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

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24  # 1 day
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# -----------------------------------------------------------------------------
# CORS / CSRF
# -----------------------------------------------------------------------------
FRONTEND_URL = config("FRONTEND_URL", "http://localhost:5173")
BACKEND_URL = config("BACKEND_URL", "http://127.0.0.1:8000")

def get_origin(url):
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.hostname}" + (f":{parsed.port}" if parsed.port else "")


CORS_ALLOWED_ORIGINS = [
    get_origin(os.environ.get("FRONTEND_URL", "")),
    get_origin(os.environ.get("BACKEND_URL", "")),
    "http://localhost:5173",
    "http://127.0.0.1:8000"
    
]

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    get_origin(FRONTEND_URL),
    get_origin(BACKEND_URL),
    "http://localhost:5173",
    "http://127.0.0.1:8000"
]

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
            "project_id": config("G_CLOUD_PROJECT_ID"),
            "bucket_name": config("G_CLOUD_BUCKET_NAME_MEDIA"),
            "credentials": GS_CREDENTIALS,  # noqa
        },
    },
    "staticfiles": {
        "BACKEND": "storages.backends.gcloud.GoogleCloudStorage",
        "OPTIONS": {
            "project_id": config("G_CLOUD_PROJECT_ID"),
            "bucket_name": config("G_CLOUD_BUCKET_NAME_STATIC"),
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

print(">>> USING PRODUCTION SETTINGS")
