import logging
import pandas as pd
import yfinance as yf
import streamlit as st

from src.utils.database_operations import DatabaseManipulator

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, filename="logs/user_log.log")

def app(database_manipulator: DatabaseManipulator):

    st.title("Investment Tracker")

    with st.form(key="investment_form", clear_on_submit=True):
        ticker = st.text_input("Ticker (e.g: IWDA.AS)")
        purchase_date = st.date_input("Purchase Date", format="DD/MM/YYYY")
        initial_amount = st.number_input("Amount", min_value=0)
        initial_unit_price = st.number_input("Unit Price", min_value=0.0)
        transaction_fee = st.number_input("Transaction Fee", min_value=0.0)
        sold_share_status = "No"

        submit_button = st.form_submit_button(label="Submit")

        if submit_button:
            database_manipulator.insert_investment(
                ticker=ticker.upper(),
                purchase_date=purchase_date.strftime("%Y-%m-%d"),
                initial_amount=initial_amount,
                initial_unit_price=initial_unit_price,
                transaction_fee=transaction_fee,
                sold_share_status=sold_share_status
            )

            st.success(f"Investment added: {ticker.upper()}", icon="✅")
