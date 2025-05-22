from datetime import datetime, date, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import json
import pytest
from practice_6.redis_file import async_cache_response, DateTimeEncoder, redis_client


class TestDateTimeEncoder:
    def test_encoder_with_date(self):
        result = json.dumps({"date": date(2023, 1, 1)}, cls=DateTimeEncoder)
        assert '"date": "2023-01-01"' in result

    def test_encoder_with_datetime(self):
        result = json.dumps(
            {"datetime": datetime(2023, 1, 1, 12, 30)},
            cls=DateTimeEncoder
        )
        assert '"datetime": "2023-01-01T12:30:00"' in result

    def test_encoder_with_other_types(self):
        data = {
            "str": "test",
            "int": 123,
            "float": 12.34,
            "bool": True,
            "none": None
        }
        result = json.dumps(data, cls=DateTimeEncoder)
        assert '"str": "test"' in result
        assert '"int": 123' in result
        assert '"float": 12.34' in result
        assert '"bool": true' in result
        assert '"none": null' in result


class TestAsyncCacheResponse:
    @pytest.fixture
    def mock_redis(self):
        with patch('practice_6.redis_file.redis_client') as mock:
            yield mock

    @pytest.mark.asyncio
    async def test_cache_miss(self, mock_redis):
        mock_func = AsyncMock()
        mock_func.__name__ = "mock_func"
        mock_func.return_value = {"data": "value"}
        mock_redis.get.return_value = None

        decorated_func = async_cache_response()(mock_func)
        result = await decorated_func("arg1", kwarg="value")

        assert result == {"data": "value"}
        mock_func.assert_called_once_with("arg1", kwarg="value")
        mock_redis.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_cache_hit(self, mock_redis):
        mock_func = AsyncMock()
        mock_func.__name__ = "mock_func"
        cached_data = json.dumps({"data": "cached"}).encode('utf-8')
        mock_redis.get.return_value = cached_data

        decorated_func = async_cache_response()(mock_func)
        result = await decorated_func("arg1", kwarg="value")

        assert result == {"data": "cached"}
        mock_func.assert_not_called()

    @pytest.mark.asyncio
    async def test_cache_expiration_logic(self, mock_redis):
        mock_func = AsyncMock()
        mock_func.__name__ = "mock_func"
        mock_func.return_value = {"data": "value"}
        mock_redis.get.return_value = None
        test_now = datetime(2023, 1, 1, 13, 0)
        with patch('practice_6.redis_file.datetime') as mock_datetime:
            mock_datetime.now.return_value = test_now
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            decorated_func = async_cache_response()(mock_func)
            await decorated_func("arg1")
            args, _ = mock_redis.setex.call_args
            assert len(args) >= 2
            expected_ttl = 1 * 3600 + 11 * 60  # 1 час 11 минут
            assert args[1] == expected_ttl
