import pandas as pd
import streamlit as st

from src.utils.database_operations import DatabaseManipulator


def app(database_manipulator: DatabaseManipulator):
    data = {
        "Rule": [
            "Exit Tax Rate",
            "Losses",
            "Exemption",
            "Dividend Income",
            "Deemed Disposal",
            "FIFO"
        ],
        "Detail": [
            "41%",
            "Can only be offset against asset e.g., loss on VUSA cannot be offset against profit on VUAA",
            "No annual exemptions like you would have when you invest in stocks",
            "41% on all income in the year received",
            "Even if you do not dispose of ETF holdings, you will be subject to an exit tax at 41% on unrealized gains on the 8th anniversary of when you bought your shares",
            "Normal rules apply when you sell part of a position - First In, First Out is used to calculate your chargeable gain"
        ]
    }
    rules_df = pd.DataFrame(data)

    st.title("Investment Rules")
    st.write("These are the guidelines and tax rules relevant to your investments.")
    st.dataframe(rules_df, hide_index=True)
