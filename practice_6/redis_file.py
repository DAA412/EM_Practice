from functools import wraps
import json
from datetime import datetime, timedelta, date
import redis
from practice_6.config import REDIS_URL

redis_client = redis.Redis.from_url(REDIS_URL)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)


def async_cache_response(expire_at_14_11=True):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            now = datetime.now()
            if expire_at_14_11:
                today_14_11 = datetime(now.year, now.month, now.day, 14, 11)
                if now < today_14_11:
                    expire_seconds = (today_14_11 - now).total_seconds()
                else:
                    tomorrow_14_11 = today_14_11 + timedelta(days=1)
                    expire_seconds = (tomorrow_14_11 - now).total_seconds()
                cached_data = redis_client.get(cache_key)
                if cached_data:
                    return json.loads(cached_data)
                result = await func(*args, **kwargs)
                redis_client.setex(
                    cache_key,
                    int(expire_seconds),
                    json.dumps(result, cls=DateTimeEncoder)
                )
                return result
            else:
                cached_data = redis_client.get(cache_key)
                if cached_data:
                    return json.loads(cached_data)
                result = await func(*args, **kwargs)
                redis_client.set(
                    cache_key,
                    json.dumps(result, cls=DateTimeEncoder)
                )
                return result

        return wrapper

    return decorator
