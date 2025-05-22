import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime
import json

from practice_6.main import app
from practice_6.models import TradingResult
from practice_6.database import get_db


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_db_session():
    session = AsyncMock(spec=AsyncSession)
    session.execute.return_value = MagicMock()
    return session


@pytest.fixture
def mock_redis():
    with patch('redis.Redis') as mock:
        yield mock


@pytest.fixture
def override_get_db(mock_db_session):
    async def _override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def sample_trading_results():
    return [
        TradingResult(
            id=1,
            trade_date=date(2023, 1, 1),
            oil_id="OIL1",
            delivery_type_id="DT1",
            delivery_basis_id="DB1",
            volume=100.50,
            total=5000.25,
            count=10
        ),
        TradingResult(
            id=2,
            trade_date=date(2023, 1, 2),
            oil_id="OIL2",
            delivery_type_id="DT2",
            delivery_basis_id="DB2",
            volume=200.75,
            total=10000.50,
            count=20
        )
    ]


@pytest.fixture
def sample_trading_dates():
    return [date(2023, 1, 1), date(2023, 1, 2)]