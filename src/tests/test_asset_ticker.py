import pytest
import pandas as pd

from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from assets.scripts.asset_ticker import AssetTicker


@pytest.fixture
def mock_yf_ticker(monkeypatch):
    mock_ticker = Mock()
    mock_ticker.history.return_value = pd.DataFrame({"Close": [100.0]})
    mock_ticker.info = {"longName": "Mock Asset"}
    monkeypatch.setattr("yfinance.Ticker", lambda ticker: mock_ticker)
    return mock_ticker


def test_get_current_price(mock_yf_ticker):
    asset = AssetTicker("Mock")
    current_price = asset.get_current_price()
    assert current_price == 100.0


def test_get_long_name(mock_yf_ticker):
    asset = AssetTicker("Mock")
    asset_name = asset.get_long_name()
    assert asset_name == "Mock Asset"


def test_get_previous_price(mock_yf_ticker):
    asset = AssetTicker("Mock")
    test_date = datetime.now() - timedelta(days=5)
    mock_yf_ticker.history.return_value = pd.DataFrame({"Close": [97.0]})
    previous_price = asset.get_previous_price(test_date)
    assert previous_price == 97.0


def test_get_unkown_name():
    with patch("yfinance.Ticker") as MockTicker:
        mock_ticker = MockTicker.return_value
        mock_ticker.info = {}

        asset = AssetTicker("Mock")
        asset_name = asset.get_long_name()
        assert asset_name == "Unknown Asset"


def test_invalid_ticker_type():
    invalid_tickers = [123, 45.67, [], {}, set(), None]

    for invalid_ticker in invalid_tickers:
        with pytest.raises(TypeError) as excinfo:
            AssetTicker(invalid_ticker)

        assert (
            str(excinfo.value)
            == f"Expected a string for ticker, got {type(invalid_ticker).__name__}"
        )
