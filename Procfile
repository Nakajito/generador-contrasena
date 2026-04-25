release: python manage.py collectstatic --noinput && python manage.py migrate --noinput
web: gunicorn settings.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --access-logfile - --error-logfile -
