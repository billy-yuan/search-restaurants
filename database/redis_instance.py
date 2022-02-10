import redis
from urllib.parse import urlparse
from search_service.s3_helpers import load_env_var

REDIS_URL = load_env_var("REDISCLOUD_URL")
EXPIRE_SECONDS = 1 * 60 * 60


url = urlparse(REDIS_URL)

redis_instance = redis.Redis(
    host=url.hostname, port=url.port, password=url.password)
