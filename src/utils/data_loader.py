import logging
import pandas as pd

from src.assets.scripts.asset_ticker import AssetTicker
from src.assets.scripts.shares_detail import SharesDetail


LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, filename="logs/user_log.log")


class DataLoader:
    def __init__(self, investments: list) -> None:
        self.investments = investments
        self.investment_data = []
    
    def process_investment(self, investment: list) -> dict:
        LOGGER.info(f"values: {investment}")
        
        (
            investment_id,
            ticker,
            purchased_date_str,
            initial_amount,
            initial_unit_price,
            transaction_fee,
            sold_share_status,
            remaining_shares,
            sale_date,
            quantity_sold,
            sale_price,
        ) = investment

        asset_ticker = AssetTicker(ticker=ticker)
        current_price = asset_ticker.get_current_price()
        asset_name = asset_ticker.get_long_name()

        share_detail = SharesDetail(
            purchased_date=purchased_date_str,
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

        purchased_date = share_detail.purchased_date.strftime("%d/%m/%Y")
        total_cost = share_detail.get_total_cost()
        unrealized_gain_loss = share_detail.get_unrealized_gain_loss()
        deemed_disposal_date = share_detail.get_deemed_disposal_date()
        deemed_disposal_triggered = share_detail.deemed_disposal_triggered_status
        deemed_disposal_price = share_detail.get_deemed_disposal_price(asset_ticker)
        deemed_disposal_realized_gain_loss = share_detail.get_deemed_disposal_gain_loss(asset_ticker)
        realized_gain_loss = share_detail.get_realized_gain_loss(asset_ticker)
        deemed_disposal_date = share_detail.formatted_deemed_disposal_date(asset_ticker)
        sale_date = share_detail.get_sale_date()
        quantity_sold = share_detail.get_quantity_sold()

        return {
            "ID": investment_id,
            "Ticker": ticker,
            "Asset Name": asset_name,
            "Purchase Date": purchased_date,
            "Initial Amount": initial_amount,
            "Initial Unit Price": initial_unit_price,
            "Total Cost": total_cost,
            "Current Price": current_price,
            "Transaction Fee": transaction_fee,
            "Unrealized Gain/Loss": unrealized_gain_loss,
            "Is Older Than Eight Years": deemed_disposal_triggered,
            "Deemed Disposal Date": deemed_disposal_date,
            "Deemed Disposal Price": deemed_disposal_price,
            "Sold Share Status": sold_share_status,
            "Sale Date": sale_date,
            "Quantity Sold": quantity_sold,
            "Sale Price": sale_price,
            "Remaining Shares": remaining_shares,
            "Realized Gain/Loss (Deemed Disposal)": deemed_disposal_realized_gain_loss,
            "Realized Gain/Loss": realized_gain_loss,
        }

    def load_data(self) -> pd.DataFrame:
        for investment in self.investments:
            processed_data = self.process_investment(investment)
            self.investment_data.append(processed_data)
        
        return pd.DataFrame(self.investment_data)
