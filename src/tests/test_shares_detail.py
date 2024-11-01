import pytest
import pandas as pd

from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from assets.scripts.shares_detail import SharesDetail


def test_asset_transaction_initialization():
    purchased_date = "2024-11-01"
    initial_amount = 10
    initial_unit_price = 10.0
    transaction_fee = 1.0
    current_price = 20.0
    sold_share_status = "No"
    remaining_shares = 10
    sale_date = None
    quantity_sold = 0
    sale_price = 0

    shares_detail = SharesDetail(
        purchased_date=purchased_date,
        initial_amount=initial_amount,
        initial_unit_price=initial_unit_price,
        transaction_fee=transaction_fee,
        current_price=current_price,
        sold_share_status=sold_share_status,
        remaining_shares=remaining_shares,
        sale_date=sale_date,
        quantity_sold=quantity_sold,
        sale_price=sale_price,
    )

    assert shares_detail.purchased_date == datetime.strptime(purchased_date, "%Y-%m-%d").date()
    assert shares_detail.initial_amount == initial_amount
    assert shares_detail.initial_unit_price == initial_unit_price
    assert shares_detail.transaction_fee == transaction_fee
    assert shares_detail.current_price == current_price
    assert shares_detail.deemed_disposal_realized_gain_loss == 0
    assert shares_detail.deemed_disposal_price is None
    assert shares_detail.sold_share_status == sold_share_status
    assert shares_detail.remaining_shares == remaining_shares
    assert shares_detail.sale_date == sale_date
    assert shares_detail.quantity_sold == quantity_sold
    assert shares_detail.sale_price == sale_price