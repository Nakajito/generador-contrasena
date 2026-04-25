#!/bin/sh
# Entrypoint for the production container.
set -eu

# Apply migrations (SQLite by default; DATABASE_URL overrides).
python manage.py migrate --noinput

exec "$@"
