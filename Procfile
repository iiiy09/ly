web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn news_system.wsgi:application --bind 0.0.0.0:$PORT --workers 2
