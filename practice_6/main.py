from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.future import select
from sqlalchemy import and_
from datetime import date
from typing import List, Optional
from pydantic import BaseModel, field_serializer, ConfigDict
from practice_6.models import *
from practice_6.database import *
from practice_6.redis_file import async_cache_response


# FastAPI app
app = FastAPI(title="Результаты торгов Spimex")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class TradingResultResponse(BaseModel):
    trade_date: date
    oil_id: str
    delivery_type_id: str
    delivery_basis_id: str
    volume: Optional[float]
    total: Optional[float]
    count: int

    @field_serializer('trade_date')
    def serialize_trade_date(self, trade_date: date, _info):
        return trade_date.isoformat() if trade_date else None

    model_config = ConfigDict(from_attributes=True)


@asynccontextmanager
async def lifespan(app: app):
    async with async_engine.begin() as conn:
        pass
    yield


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse(request, "index.html")


# API Endpoints
@app.get("/last-trading-dates/", response_model=List[str])
@async_cache_response()
async def get_last_trading_dates(
        limit: int = Query(5, description="Количество предыдущих дат торгов", gt=0, le=70),
        db: AsyncSession = Depends(get_db)
):
    """
    Возвращает количество предыдущих дат торгов.

    Parameters:
    - limit: Количество дат торгов (default: 5, max: 70)
    """
    stmt = select(TradingResult.trade_date).distinct().order_by(TradingResult.trade_date.desc()).limit(limit)
    result = await db.execute(stmt)
    dates = result.scalars().all()
    return [date.isoformat() for date in dates]


@app.get("/dynamics/", response_model=List[TradingResultResponse])
@async_cache_response()
async def get_dynamics(
        start_date: date = Query(..., description="Начальная дата"),
        end_date: date = Query(..., description="Конечная дата"),
        oil_id: Optional[str] = Query(None, description="Фильтрация по oil ID"),
        delivery_type_id: Optional[str] = Query(None, description="Фильтрация по delivery type ID"),
        delivery_basis_id: Optional[str] = Query(None, description="Фильтрация по delivery basis ID"),
        db: AsyncSession = Depends(get_db)
):
    """
    Возвращает отфильтрованный список торгов за период.

    Parameters:
    - start_date: Начальная дата торгов (required)
    - end_date: Конечная дата торгов (required)
    - oil_id: Фильтрация по oil ID (optional)
    - delivery_type_id: Фильтрация по delivery type ID (optional)
    - delivery_basis_id: Фильтрация по delivery basis ID (optional)
    """
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Дата начала должна быть раньше даты конца")

    filters = [
        TradingResult.trade_date >= start_date,
        TradingResult.trade_date <= end_date
    ]

    if oil_id:
        filters.append(TradingResult.oil_id == oil_id)
    if delivery_type_id:
        filters.append(TradingResult.delivery_type_id == delivery_type_id)
    if delivery_basis_id:
        filters.append(TradingResult.delivery_basis_id == delivery_basis_id)

    stmt = select(TradingResult).where(and_(*filters)).order_by(TradingResult.trade_date.desc())
    result = await db.execute(stmt)
    trading_results = result.scalars().all()
    return [tr.to_dict() for tr in trading_results]


@app.get("/trading-results/", response_model=List[TradingResultResponse])
@async_cache_response()
async def get_trading_results(
        oil_id: Optional[str] = Query(None, description="Фильтрация по oil ID"),
        delivery_type_id: Optional[str] = Query(None, description="Фильтрация по delivery type ID"),
        delivery_basis_id: Optional[str] = Query(None, description="Фильтрация по delivery basis ID"),
        limit: int = Query(10, description="Количество возвращаемых значений", gt=0, le=100),
        db: AsyncSession = Depends(get_db)
):
    """
    Возвращает отфильтрованный список последних торгов.

    Parameters:
    - oil_id: Фильтрация по oil ID (optional)
    - delivery_type_id: Фильтрация по delivery type ID (optional)
    - delivery_basis_id: Фильтрация по delivery basis ID (optional)
    - limit: Количество возвращаемых значений (default: 10, max: 100)
    """
    filters = []

    if oil_id:
        filters.append(TradingResult.oil_id == oil_id)
    if delivery_type_id:
        filters.append(TradingResult.delivery_type_id == delivery_type_id)
    if delivery_basis_id:
        filters.append(TradingResult.delivery_basis_id == delivery_basis_id)

    stmt = select(TradingResult)
    if filters:
        stmt = stmt.where(and_(*filters))
    stmt = stmt.order_by(TradingResult.trade_date.desc()).limit(limit)

    result = await db.execute(stmt)
    trading_results = result.scalars().all()
    return [tr.to_dict() for tr in trading_results]
