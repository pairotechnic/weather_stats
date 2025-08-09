web:  python manage.py collectstatic --noinput && python manage.py migrate && gunicorn weather_stats.wsgi --bind 0.0.0.0:$PORT
worker: celery -A weather_stats worker --loglevel=info
beat: celery -A weather_stats beat --loglevel=info