# Connect to Redis
from redis import Redis

# Class to handle Redis connection and global access to the database
class RedisConnection:
    # Redis connection
    redis = None

    @staticmethod
    def get_redis():
        if RedisConnection.redis is None:
            RedisConnection.redis = Redis(host='redis', port=6379)
        return RedisConnection.redis

    @staticmethod
    def close():
        if RedisConnection.redis is not None:
            RedisConnection.redis.close()
            RedisConnection.redis = None

    
