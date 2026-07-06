"""Development settings — DO NOT use in production."""

from .base import *  # noqa: F403
from .base import env

DEBUG = True
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="<V?q2X<+T[ehWEiSB}rqfw~=={qexm7nN6BK^]/#a+uR/P1_3Wm_AE1O+4m}9Qu(Qyt}1=zn7W<",
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
