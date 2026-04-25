"""Development settings — DO NOT use in production."""

from .base import *  # noqa: F403
from .base import env

DEBUG = True
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="django-insecure-dev-only-change-in-prod",
)
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]  # noqa: S104

# Plain static storage in dev: no hashing, no manifest, runserver-friendly.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Relaxed CSP for dev: allow DevTools / hot reload if any.
INTERNAL_IPS = ["127.0.0.1"]
