import pytest
from fastapi import status
from datetime import date


class TestRootEndpoint:
    def test_read_root(self, client):
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]
        assert "<title>" in response.text


class TestLastTradingDatesEndpoint:
    def test_get_last_trading_dates_success(
            self, client, mock_db_session, sample_trading_dates, override_get_db
    ):
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = sample_trading_dates

        response = client.get("/last-trading-dates/?limit=2")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == ["2023-01-01", "2023-01-02"]

    @pytest.mark.parametrize("limit,expected_status", [
        (0, status.HTTP_422_UNPROCESSABLE_ENTITY),
        (71, status.HTTP_422_UNPROCESSABLE_ENTITY),
        (5, status.HTTP_200_OK),
        (70, status.HTTP_200_OK)
    ])
    def test_get_last_trading_dates_validation(
            self, client, limit, expected_status, override_get_db
    ):
        response = client.get(f"/last-trading-dates/?limit={limit}")
        assert response.status_code == expected_status


class TestDynamicsEndpoint:
    def test_get_dynamics_success(
            self, client, mock_db_session, sample_trading_results, override_get_db
    ):
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = sample_trading_results

        response = client.get(
            "/dynamics/?start_date=2023-01-01&end_date=2023-01-02"
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 2

    def test_get_dynamics_with_filters(
            self, client, mock_db_session, sample_trading_results, override_get_db
    ):
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = [
            sample_trading_results[0]
        ]

        response = client.get(
            "/dynamics/?start_date=2023-01-01&end_date=2023-01-02"
            "&oil_id=OIL1&delivery_type_id=DT1&delivery_basis_id=DB1"
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1

    def test_get_dynamics_invalid_date_range(self, client, override_get_db):
        response = client.get(
            "/dynamics/?start_date=2023-01-02&end_date=2023-01-01"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Дата начала должна быть раньше даты конца" in response.text


class TestTradingResultsEndpoint:
    def test_get_trading_results_success(
            self, client, mock_db_session, sample_trading_results, override_get_db
    ):
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = sample_trading_results

        response = client.get("/trading-results/?limit=2")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 2

    def test_get_trading_results_with_filters(
            self, client, mock_db_session, sample_trading_results, override_get_db
    ):
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = [
            sample_trading_results[0]
        ]

        response = client.get(
            "/trading-results/?oil_id=OIL1&delivery_type_id=DT1&delivery_basis_id=DB1&limit=1"
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1

    @pytest.mark.parametrize("limit,expected_status", [
        (0, status.HTTP_422_UNPROCESSABLE_ENTITY),
        (101, status.HTTP_422_UNPROCESSABLE_ENTITY),
        (1, status.HTTP_200_OK),
        (100, status.HTTP_200_OK)
    ])
    def test_get_trading_results_validation(
            self, client, limit, expected_status, override_get_db
    ):
        response = client.get(f"/trading-results/?limit={limit}")
        assert response.status_code == expected_status
