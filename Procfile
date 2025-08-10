web: gunicorn weather_stats.wsgi --bind 0.0.0.0:$PORT -- worker 3 --threads 2
worker: celery -A weather_stats worker --loglevel=info --concurrency=2 --without-mingle --without-gossip
beat: celery -A weather_stats beat --loglevel=info