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
def mock_asset_ticker():
    mock_at = Mock(spec=AssetTicker)
    mock_at.get_current_price.return_value = 100.0
    mock_at.get_long_name.return_value = "iShares Core MSCI World UCITS ETF USD (Acc)"
    return mock_at


@pytest.fixture
def mock_shares_detail():
    mock_sd = Mock(spec=SharesDetail)
    mock_sd.purchased_date.strftime.return_value = "01/11/2024"
    mock_sd.get_total_cost.return_value = 10.0
    mock_sd.get_unrealized_gain_loss.return_value = 90.0
    mock_sd.get_deemed_disposal_date.return_value = "01/11/2032"
    mock_sd.deemed_disposal_triggered_status = False
    mock_sd.get_deemed_disposal_price.return_value = None
    mock_sd.get_deemed_disposal_gain_loss.return_value = 0
    mock_sd.get_realized_gain_loss.return_value = 0
    mock_sd.formatted_deemed_disposal_date.return_value = "01/11/2032"
    mock_sd.get_sale_date.return_value = None
    mock_sd.get_quantity_sold.return_value = 0
    return mock_sd


def test_data_loader_init(mock_investments_sample):
    data_loader = DataLoader(mock_investments_sample)
    assert data_loader.investments == mock_investments_sample
    assert data_loader.investment_data == []
