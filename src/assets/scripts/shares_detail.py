import logging

from datetime import datetime, timedelta
from src.assets.scripts.asset_ticker import AssetTicker

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, filename="logs/user_log.log")


class SharesDetail:
    def __init__(
        self,
        purchased_date: str,
        initial_amount: int,
        initial_unit_price: float,
        transaction_fee: float,
        current_price: float,
        sold_share_status: str,
        remaining_shares: int,
        sale_date: datetime,
        quantity_sold: int,
        sale_price: float,
    ) -> None:
        self.purchased_date = datetime.strptime(purchased_date, "%Y-%m-%d").date()
        self.initial_amount = initial_amount
        self.initial_unit_price = initial_unit_price
        self.transaction_fee = transaction_fee
        self.current_price = current_price
        self.deemed_disposal_realized_gain_loss = 0
        self.deemed_disposal_price = None
        self.sold_share_status = sold_share_status
        self.remaining_shares = remaining_shares
        self.sale_date = sale_date
        self.quantity_sold = quantity_sold
        self.sale_price = sale_price

    def get_total_cost(self) -> float:
        return self.initial_amount * self.initial_unit_price

    def get_unrealized_gain_loss(self) -> float:
        return round(
            (self.current_price - self.initial_unit_price) * self.initial_amount
            - self.transaction_fee,
            2,
        )

    def get_deemed_disposal_date(self) -> datetime:
        return self.purchased_date + timedelta(days=365.25 * 8)

    def is_deemed_disposal_triggered(self) -> bool:
        return datetime.now().date() >= self.get_deemed_disposal_date()

    @property
    def deemed_disposal_triggered_status(self) -> str:
        return "Yes" if self.is_deemed_disposal_triggered() else "No"

    def get_deemed_disposal_price(self, asset_ticker: AssetTicker) -> float:
        if self.is_deemed_disposal_triggered():
            deemed_disposal_date = self.get_deemed_disposal_date()

            last_asset_close_date = deemed_disposal_date - timedelta(
                days=(deemed_disposal_date.weekday() - 4) % 7
            )

            return asset_ticker.get_previous_price(last_asset_close_date)

    def get_deemed_disposal_gain_loss(self, asset_ticker: AssetTicker) -> float:
        if self.is_deemed_disposal_triggered():
            return round(
                self.initial_amount
                * (
                    self.get_deemed_disposal_price(asset_ticker)
                    - self.initial_unit_price
                ),
                2,
            )
        return 0

    def get_realized_gain_loss(self, asset_ticker: AssetTicker) -> float:
        if self.sold_share_status != "No":
            return round(
                self.quantity_sold * (self.sale_price - self.initial_unit_price)
                - self.get_deemed_disposal_gain_loss(asset_ticker),
                2,
            )
        return round(
            self.quantity_sold * (self.sale_price - self.initial_unit_price), 2
        )

    def formatted_deemed_disposal_date(self, asset_ticker: AssetTicker) -> float:
        return (
            self.get_deemed_disposal_date().strftime("%d/%m/%Y")
            if self.get_deemed_disposal_price(asset_ticker)
            else None
        )

    def get_sale_date(self) -> datetime:
        return (
            datetime.strptime(self.sale_date, "%Y-%m-%d").strftime("%d/%m/%Y")
            if self.sale_date
            else None
        )

    def get_quantity_sold(self) -> int:
        return self.quantity_sold if self.quantity_sold else 0
