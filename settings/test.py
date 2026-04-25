"""Test settings — isolated, fast, deterministic."""

from .base import *  # noqa: F403
from .base import MIDDLEWARE as _BASE_MIDDLEWARE

# WhiteNoise requires STATIC_ROOT to exist on disk; skip it in tests.
MIDDLEWARE = [m for m in _BASE_MIDDLEWARE if "whitenoise" not in m]

DEBUG = False
SECRET_KEY = "test-only-not-a-secret"
ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Speed up password hashing in tests.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Disable throttling by default in unit tests; individual tests can re-enable.
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_THROTTLE_CLASSES": [],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "30/min",
        "generate": "30/min",
    },
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "UNAUTHENTICATED_USER": None,
}
