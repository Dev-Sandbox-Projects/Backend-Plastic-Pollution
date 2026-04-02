import redis
from config import settings

redis_options = {
    "decode_responses": True,
}

if settings.REDIS_URL.startswith("rediss://"):
    redis_options["ssl_cert_reqs"] = "none"
r = redis.from_url(settings.REDIS_URL, **redis_options)