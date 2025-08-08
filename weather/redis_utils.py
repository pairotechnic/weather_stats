import redis
from django.conf import settings

# Initialize Redis connection pool
redis_pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True
)

def get_redis_client():
    '''
    Retrieves a Redis client from the connection pool
    '''
    return redis.Redis(connection_pool=redis_pool)