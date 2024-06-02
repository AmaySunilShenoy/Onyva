# Connect to Redis
from redis import Redis

def connect_to_redis():
    redis = Redis(host="redis", port=6379, decode_responses=True)
    return redis

