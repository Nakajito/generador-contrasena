#!/bin/sh
# Entrypoint for the production container.
set -eu

# Belt-and-suspenders: regenerate static manifest if absent (e.g. buildpack skipped it).
if [ ! -f "${STATIC_ROOT:-/app/staticfiles}/staticfiles.json" ]; then
    echo "[entrypoint] staticfiles.json missing → running collectstatic"
    python manage.py collectstatic --noinput || true
fi

# Apply migrations (SQLite by default; DATABASE_URL overrides).
python manage.py migrate --noinput

exec "$@"
