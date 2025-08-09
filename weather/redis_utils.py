import redis
from django.conf import settings

def get_redis_client():
    
    return redis.Redis(
        host = settings.REDIS_CONFIG["HOST"],
        port = settings.REDIS_CONFIG["PORT"],
        db = settings.REDIS_CONFIG["DB"],
        ssl = settings.REDIS_CONFIG["SSL"],
        decode_responses = True,
        socket_connect_timeout = 5
    )
    