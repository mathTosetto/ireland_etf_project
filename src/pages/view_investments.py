import logging
import pandas as pd
import streamlit as st

from src.assets.scripts.asset_ticker import AssetTicker
from src.assets.scripts.shares_detail import SharesDetail
from src.utils.database_operations import databaseManipulator


LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, filename="logs/user_log.log")


def load_data(investments: list) -> pd.DataFrame:
    investment_data = []
    for investment in investments:
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
        deemed_disposal_realized_gain_loss = share_detail.get_deemed_disposal_gain_loss(
            asset_ticker
        )
        realized_gain_loss = share_detail.get_realized_gain_loss(asset_ticker)
        deemed_disposal_date = share_detail.formatted_deemed_disposal_date(asset_ticker)
        sale_date = share_detail.get_sale_date()
        quantity_sold = share_detail.get_quantity_sold()

        investment_data.append(
            {
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
        )
    return pd.DataFrame(investment_data)


# DELETE AFTERWARDS
# def history_assets(investments: list):
#     investment_data = []
#     for investment in investments:
#         (
#             id,
#             investment_id,
#             remaining_shares,
#             sale_date,
#             quantity_sold,
#             sale_price,
#         ) = investment

#         investment_data.append(
#             {
#                 "ID": id,
#                 "Investment ID": investment_id,
#                 "Remaning Shares": remaining_shares,
#                 "Sale Date": sale_date,
#                 "Quantity Sold": quantity_sold,
#                 "Sale Price": sale_price
#             }
#         )
#     return pd.DataFrame(investment_data)


def app(database_manipulator: databaseManipulator):
    investments = database_manipulator.fetch_investments()

    if st.button("Truncate Investments Table"):
        database_manipulator.truncate_table()
        st.success("Investments table truncated.")
        st.rerun()

    st.divider()

    # DELETE AFTERWARDS
    # x = database_manipulator.temp_function()
    # y = history_assets(x)
    # st.dataframe(y, hide_index=True)

    if investments:
        df = load_data(investments=investments)
        LOGGER.info(f"df: {df.columns}")

        st.title("Investment Portfolio")
        st.write("### Investment Details")
        st.dataframe(df, hide_index=True)

        st.divider()

        investments = database_manipulator.fetch_investments()
        investment_ids = [investment[0] for investment in investments]

        if investment_ids:
            selected_id = st.selectbox(
                "Select an Investment ID to Update", investment_ids
            )
            selected_investment = database_manipulator.fetch_investments(selected_id)

            LOGGER.info(f"selected_investment: {selected_investment}")
            LOGGER.info(f"-" * 40)

            if selected_investment:
                selected_row = selected_investment[0]
                LOGGER.info(f"selected_row: {selected_row}")

                investment_id = selected_row[0]
                ticker = selected_row[1]
                initial_amount = selected_row[3]
                sold_share_status = selected_row[6]
                remaining_shares = selected_row[7]

                LOGGER.info(f"sold_share_status: {sold_share_status}")

                st.write(f"**Ticker:** {ticker}")
                st.write(f"**Total of shares:** {remaining_shares}")

                valid_sold_statuses = ("Partially Sold", "Sold")
                sold_status_index = (
                    valid_sold_statuses.index(sold_share_status)
                    if sold_share_status in valid_sold_statuses
                    else 0
                )
                sold_share_status = st.radio(
                    "Share sold?", valid_sold_statuses, index=sold_status_index
                )

            if sold_share_status == "Sold":
                sold_date = st.date_input("Sold Date")
                sale_price = st.number_input("Sale Price", min_value=0)
                quantity_sold = initial_amount
                remaining_shares = 0

            elif sold_share_status == "Partially Sold":
                sold_date = st.date_input("Sold Date")
                quantity_sold = st.number_input(
                    "Quantity Sold", min_value=0, max_value=initial_amount, value=0
                )
                sale_price = st.number_input("Sale Price", min_value=0)
                remaining_shares = initial_amount - quantity_sold

            if st.button("Update Investment"):
                database_manipulator.update_investments(
                    investment_id=investment_id,
                    sold_share_status=sold_share_status,
                    remaining_shares=remaining_shares,
                    sale_date=sold_date.strftime("%Y-%m-%d"),
                    quantity_sold=quantity_sold,
                    sale_price=sale_price,
                )

                st.success("Investment updated successfully!")

    else:
        st.write("No investments found.")
