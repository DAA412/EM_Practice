from sqlalchemy import Column, Integer, String, Numeric, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TradingResult(Base):
    __tablename__ = 'trading_results'

    id = Column(Integer, primary_key=True)
    exchange_product_id = Column(String(20))
    exchange_product_name = Column(String(255))
    oil_id = Column(String(10))
    delivery_basis_id = Column(String(10))
    delivery_basis_name = Column(String(255))
    delivery_type_id = Column(String(10))
    volume = Column(Numeric(20, 2))
    total = Column(Numeric(20, 2))
    count = Column(Integer)
    trade_date = Column(Date)

    def to_dict(self):
        return {
            "trade_date": self.trade_date,
            "oil_id": self.oil_id,
            "delivery_type_id": self.delivery_type_id,
            "delivery_basis_id": self.delivery_basis_id,
            "volume": float(self.volume) if self.volume else None,
            "total": float(self.total) if self.total else None,
            "count": self.count
        }
