"""Development settings — DO NOT use in production."""

from .base import *  # noqa: F403
from .base import env

DEBUG = True
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="django-insecure-dev-only-change-in-prod",
)
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]  # noqa: S104

# Relaxed CSP for dev: allow DevTools / hot reload if any.
INTERNAL_IPS = ["127.0.0.1"]

# Use non-manifest storage in dev (no collectstatic needed).
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
