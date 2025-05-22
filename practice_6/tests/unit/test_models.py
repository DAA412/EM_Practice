from datetime import date
from practice_6.models import TradingResult


class TestTradingResultModel:
    def test_model_creation(self):
        tr = TradingResult(
            id=1,
            trade_date=date(2023, 1, 1),
            oil_id="OIL1",
            delivery_type_id="DT1",
            delivery_basis_id="DB1",
            volume=100.50,
            total=5000.25,
            count=10
        )

        assert tr.id == 1
        assert tr.oil_id == "OIL1"
        assert tr.volume == 100.50
        assert tr.trade_date == date(2023, 1, 1)

    def test_to_dict_method(self, sample_trading_results):
        tr = sample_trading_results[0]
        result = tr.to_dict()

        expected = {
            "trade_date": date(2023, 1, 1),
            "oil_id": "OIL1",
            "delivery_type_id": "DT1",
            "delivery_basis_id": "DB1",
            "volume": 100.5,
            "total": 5000.25,
            "count": 10
        }

        assert result == expected

    def test_to_dict_with_none_values(self):
        tr = TradingResult(
            trade_date=date(2023, 1, 1),
            oil_id="OIL1",
            delivery_type_id="DT1",
            delivery_basis_id="DB1",
            volume=None,
            total=None,
            count=10
        )

        result = tr.to_dict()
        assert result["volume"] is None
        assert result["total"] is None