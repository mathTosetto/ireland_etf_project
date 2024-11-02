import sys
import pytest

from pathlib import Path

from unittest.mock import Mock, patch
from datetime import datetime, timedelta

src_path = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(src_path))

from assets.scripts.asset_ticker import AssetTicker
from assets.scripts.shares_detail import SharesDetail


@pytest.fixture
def mock_shares_detail():
    return SharesDetail(
        purchased_date="2024-11-01",
        initial_amount=10,
        initial_unit_price=10.0,
        transaction_fee=1.0,
        current_price=20.0,
        sold_share_status="No",
        remaining_shares=10,
        sale_date=None,
        quantity_sold=0,
        sale_price=0,
    )


@pytest.fixture
def mock_asset_ticker():
    return Mock(spec=AssetTicker)


def test_asset_transaction_initialization(mock_shares_detail):
    assert mock_shares_detail.purchased_date == datetime(2024, 11, 1).date()
    assert mock_shares_detail.initial_amount == 10
    assert mock_shares_detail.initial_unit_price == 10.0
    assert mock_shares_detail.transaction_fee == 1.0
    assert mock_shares_detail.current_price == 20.0
    assert mock_shares_detail.deemed_disposal_realized_gain_loss == 0
    assert mock_shares_detail.deemed_disposal_price is None
    assert mock_shares_detail.sold_share_status == "No"
    assert mock_shares_detail.remaining_shares == 10
    assert mock_shares_detail.sale_date is None
    assert mock_shares_detail.quantity_sold == 0
    assert mock_shares_detail.sale_price == 0


def test_get_total_cost(mock_shares_detail):
    result = 10 * 10
    assert mock_shares_detail.get_total_cost() == result


def test_get_unrealized_gain_loss(mock_shares_detail):
    result = round((20 - 10) * 10 - 1, 2)
    assert mock_shares_detail.get_unrealized_gain_loss() == result


def test_get_deemed_disposal_date(mock_shares_detail):
    result = datetime(2024, 11, 1).date() + timedelta(days=365.25 * 8)
    assert mock_shares_detail.get_deemed_disposal_date() == result


def test_is_deemed_disposal_triggered_past_date(mock_shares_detail):
    mock_shares_detail.purchased_date = datetime.strptime(
        "2024-11-01", "%Y-%m-%d"
    ).date()
    with patch("datetime.datetime") as mock_datetime:
        mock_datetime.now.return_value = (
            mock_shares_detail.is_deemed_disposal_triggered()
        )
        assert mock_shares_detail.is_deemed_disposal_triggered() == False


def test_is_deemed_disposal_triggered_future_date(mock_shares_detail):
    mock_shares_detail.purchased_date = datetime.strptime(
        "2010-11-01", "%Y-%m-%d"
    ).date()
    with patch("datetime.datetime") as mock_datetime:
        mock_datetime.now.return_value = mock_shares_detail.get_deemed_disposal_date()
        assert mock_shares_detail.is_deemed_disposal_triggered() == True


def test_deemed_disposal_triggered_status_not_triggered(mock_shares_detail):
    mock_shares_detail.purchased_date = datetime.strptime(
        "2024-11-01", "%Y-%m-%d"
    ).date()
    with patch("datetime.datetime") as mock_datetime:
        mock_datetime.now.return_value = mock_shares_detail.get_deemed_disposal_date()
        assert mock_shares_detail.deemed_disposal_triggered_status == "No"


def test_deemed_disposal_triggered_status_triggered(mock_shares_detail):
    mock_shares_detail.purchased_date = datetime.strptime(
        "2010-11-01", "%Y-%m-%d"
    ).date()
    with patch("datetime.datetime") as mock_datetime:
        mock_datetime.now.return_value = mock_shares_detail.get_deemed_disposal_date()
        assert mock_shares_detail.deemed_disposal_triggered_status == "Yes"


def test_get_deemed_disposal_price(mock_shares_detail, mock_asset_ticker):
    mock_shares_detail.purchased_date = datetime(2010, 11, 1).date()
    last_asset_close_date = datetime(2018, 10, 26).date()
    mock_asset_ticker.get_previous_price.return_value = 97.0

    deemed_disposal_price = mock_shares_detail.get_deemed_disposal_price(
        mock_asset_ticker
    )

    assert deemed_disposal_price == 97.0
    mock_asset_ticker.get_previous_price.assert_called_once_with(last_asset_close_date)


def test_get_deemed_disposal_gain_loss_true(mock_shares_detail, mock_asset_ticker):
    mock_shares_detail.purchased_date = datetime(2010, 11, 1).date()
    mock_asset_ticker.get_previous_price.return_value = 15.0

    result = round(10 * (15.0 - 10.0), 2)

    deemed_disposal_gain_loss = mock_shares_detail.get_deemed_disposal_gain_loss(
        mock_asset_ticker
    )
    assert deemed_disposal_gain_loss == result

    last_asset_close_date = mock_shares_detail.get_deemed_disposal_date() - timedelta(
        days=(mock_shares_detail.get_deemed_disposal_date().weekday() - 4) % 7
    )
    mock_asset_ticker.get_previous_price.assert_called_once_with(last_asset_close_date)


def test_get_deemed_disposal_gain_loss_false(mock_shares_detail, mock_asset_ticker):
    mock_asset_ticker.get_previous_price.return_value = 15.0

    result = 0

    deemed_disposal_gain_loss = mock_shares_detail.get_deemed_disposal_gain_loss(
        mock_asset_ticker
    )
    assert deemed_disposal_gain_loss == result


def test_get_realized_gain_loss_no(mock_shares_detail, mock_asset_ticker):
    result = round(0 * (0 - 10), 2)
    realized_gain_loss = mock_shares_detail.get_realized_gain_loss(mock_asset_ticker)
    assert realized_gain_loss == result


def test_get_realized_gain_loss_yes_deemed_disposal_not_triggered(
    mock_shares_detail, mock_asset_ticker
):
    mock_shares_detail.purchased_date = datetime(2024, 11, 1).date()
    mock_shares_detail.sold_share_status = "Yes"
    mock_asset_ticker.get_previous_price.return_value = 0

    result = round(0 * (0 - 10) - 0, 2)

    realized_gain_loss = mock_shares_detail.get_realized_gain_loss(mock_asset_ticker)
    assert realized_gain_loss == result


def test_get_realized_gain_loss_yes_deemed_disposal_triggered(
    mock_shares_detail, mock_asset_ticker
):
    mock_shares_detail.purchased_date = datetime(2010, 11, 1).date()
    mock_shares_detail.sold_share_status = "Yes"
    mock_shares_detail.quantity_sold = 10
    mock_shares_detail.sale_price = 10
    mock_asset_ticker.get_previous_price.return_value = 100

    result = round(10 * (10 - 10) - 900, 2)

    realized_gain_loss = mock_shares_detail.get_realized_gain_loss(mock_asset_ticker)
    assert realized_gain_loss == result


def test_formatted_deemed_disposal_date(mock_shares_detail, mock_asset_ticker):
    mock_shares_detail.purchased_date = datetime(2010, 11, 1).date()
    mock_asset_ticker.get_previous_price.return_value = 100

    result = "01/11/2018"

    formatted_deemed_disposal_date = mock_shares_detail.formatted_deemed_disposal_date(
        mock_asset_ticker
    )
    assert formatted_deemed_disposal_date == result


def test_formatted_deemed_disposal_date_none(mock_shares_detail, mock_asset_ticker):
    mock_shares_detail.purchased_date = datetime(2024, 11, 1).date()
    mock_asset_ticker.get_previous_price.return_value = 100

    result = None

    formatted_deemed_disposal_date = mock_shares_detail.formatted_deemed_disposal_date(
        mock_asset_ticker
    )
    assert formatted_deemed_disposal_date == result


def test_get_sale_date_none(mock_shares_detail):
    result = None
    get_sale_date = mock_shares_detail.get_sale_date()
    assert get_sale_date == result


def test_get_sale_date(mock_shares_detail):
    mock_shares_detail.sale_date = "2024-11-01"
    result = "01/11/2024"
    get_sale_date = mock_shares_detail.get_sale_date()
    assert get_sale_date == result


def test_get_quantity_sold_zero(mock_shares_detail):
    result = 0
    get_quantity_sold = mock_shares_detail.get_quantity_sold()
    assert get_quantity_sold == result


def test_get_quantity_sold(mock_shares_detail):
    mock_shares_detail.quantity_sold = 100
    result = 100
    get_quantity_sold = mock_shares_detail.get_quantity_sold()
    assert get_quantity_sold == result
