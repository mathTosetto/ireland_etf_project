import sys
import pytest
import pandas as pd

from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

src_path = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(src_path))

from src.utils.data_loader import DataLoader

from src.assets.scripts.asset_ticker import AssetTicker
from src.assets.scripts.shares_detail import SharesDetail


@pytest.fixture
def mock_investments_sample():
    return [1, "IWDA.AS", "2024-11-01", 1, 10.0, 1.0, "No", 1, None, 0, 0]


@pytest.fixture
def mock_data_loader(mock_investments_sample):
    return DataLoader(investments=mock_investments_sample)


@pytest.fixture
def mock_yf_ticker(monkeypatch):
    mock_ticker = Mock()
    mock_ticker.history.return_value = pd.DataFrame({"Close": [100.0]})
    mock_ticker.info = {"longName": "Mock Asset"}
    monkeypatch.setattr("yfinance.Ticker", lambda ticker: mock_ticker)
    return mock_ticker


def test_data_loader_init(mock_investments_sample):
    data_loader = DataLoader(mock_investments_sample)
    assert data_loader.investments == mock_investments_sample
    assert data_loader.investment_data == []


def test_process_investment(mock_data_loader, mock_yf_ticker):
    investment = mock_data_loader.investments
    asset = AssetTicker("Mock")

    result = mock_data_loader.process_investment(investment)

    result["Current Price"] = asset.get_current_price()
    result["Unrealized Gain/Loss"] = round(
        (asset.get_current_price() - investment[4]) * investment[3] - investment[5], 2
    )

    expected_result = {
        "ID": 1,
        "Ticker": "IWDA.AS",
        "Asset Name": "Mock Asset",
        "Purchase Date": "01/11/2024",
        "Initial Amount": 1,
        "Initial Unit Price": 10.0,
        "Total Cost": 10.0,
        "Current Price": 100.0,
        "Transaction Fee": 1.0,
        "Unrealized Gain/Loss": 89.0,
        "Is Older Than Eight Years": "No",
        "Deemed Disposal Date": None,
        "Deemed Disposal Price": None,
        "Sold Share Status": "No",
        "Sale Date": None,
        "Quantity Sold": 0,
        "Sale Price": 0,
        "Remaining Shares": 1,
        "Realized Gain/Loss (Deemed Disposal)": 0,
        "Realized Gain/Loss": -0.0,
    }

    assert result == expected_result, f"Expected {expected_result} but got {result}"


@pytest.fixture
def mock_investments():
    return [
        [1, "AAPL", "2023-01-01", 100, 150.0, 10.0, "Partially Sold", 50, "2023-12-01", 50, 160.0],
        [2, "MSFT", "2022-05-01", 200, 250.0, 15.0, "Sold", 0, "2023-07-01", 200, 260.0]
    ]

@pytest.fixture
def expected_df():
    return pd.DataFrame([
        {
            "ID": 1,
            "Ticker": "AAPL",
            "Asset Name": "Apple Inc.",
            "Purchase Date": "01/01/2023",
            "Initial Amount": 100,
            "Initial Unit Price": 150.0,
            "Total Cost": 15100.0,
            "Current Price": 160.0,
            "Transaction Fee": 10.0,
            "Unrealized Gain/Loss": 1000.0,
            "Is Older Than Eight Years": False,
            "Deemed Disposal Date": "01/01/2031",
            "Deemed Disposal Price": 165.0,
            "Sold Share Status": "Partially Sold",
            "Sale Date": "01/12/2023",
            "Quantity Sold": 50,
            "Sale Price": 160.0,
            "Remaining Shares": 50,
            "Realized Gain/Loss (Deemed Disposal)": 1000.0,
            "Realized Gain/Loss": 800.0,
        },
        {
            "ID": 2,
            "Ticker": "MSFT",
            "Asset Name": "Microsoft Corp.",
            "Purchase Date": "01/05/2022",
            "Initial Amount": 200,
            "Initial Unit Price": 250.0,
            "Total Cost": 50200.0,
            "Current Price": 260.0,
            "Transaction Fee": 15.0,
            "Unrealized Gain/Loss": 2000.0,
            "Is Older Than Eight Years": False,
            "Deemed Disposal Date": "01/05/2030",
            "Deemed Disposal Price": 270.0,
            "Sold Share Status": "Sold",
            "Sale Date": "01/07/2023",
            "Quantity Sold": 200,
            "Sale Price": 260.0,
            "Remaining Shares": 0,
            "Realized Gain/Loss (Deemed Disposal)": 2000.0,
            "Realized Gain/Loss": 1500.0,
        }
    ])

@patch('src.utils.data_loader.AssetTicker')
@patch('src.utils.data_loader.SharesDetail')
def test_load_data(mock_shares_detail, mock_asset_ticker, mock_investments, expected_df):
    mock_asset_ticker_instance = Mock()
    mock_asset_ticker.return_value = mock_asset_ticker_instance
    mock_asset_ticker_instance.get_current_price.side_effect = [160.0, 260.0]
    mock_asset_ticker_instance.get_long_name.side_effect = ["Apple Inc.", "Microsoft Corp."]

    mock_shares_detail_instance = Mock()
    mock_shares_detail.return_value = mock_shares_detail_instance
    mock_shares_detail_instance.purchased_date.strftime.side_effect = ["01/01/2023", "01/05/2022"]
    mock_shares_detail_instance.get_total_cost.side_effect = [15100.0, 50200.0]
    mock_shares_detail_instance.get_unrealized_gain_loss.side_effect = [1000.0, 2000.0]
    mock_shares_detail_instance.get_deemed_disposal_date.side_effect = ["01/01/2031", "01/05/2030"]
    mock_shares_detail_instance.deemed_disposal_triggered_status = False
    mock_shares_detail_instance.get_deemed_disposal_price.side_effect = [165.0, 270.0]
    mock_shares_detail_instance.get_deemed_disposal_gain_loss.side_effect = [1000.0, 2000.0]
    mock_shares_detail_instance.get_realized_gain_loss.side_effect = [800.0, 1500.0]
    mock_shares_detail_instance.formatted_deemed_disposal_date.side_effect = ["01/01/2031", "01/05/2030"]
    mock_shares_detail_instance.get_sale_date.side_effect = ["01/12/2023", "01/07/2023"]
    mock_shares_detail_instance.get_quantity_sold.side_effect = [50, 200]

    data_loader = DataLoader(mock_investments)
    result_df = data_loader.load_data()

    pd.testing.assert_frame_equal(result_df, expected_df)
