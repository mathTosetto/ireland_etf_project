import logging
import streamlit as st
from src.utils.data_loader import DataLoader
from src.utils.database_operations import DatabaseManipulator

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, filename="logs/user_log.log")

st.set_page_config(page_title="Home", page_icon=":house:", layout="centered")

def app(database_manipulator: DatabaseManipulator):
    st.title("Investment Portfolio Manager")
    st.write("""
    ### Manage Your Investments with Ease
    This application allows you to:
    - **View** a summary of your investment portfolio, including important financial metrics.
    - **Update** investment details such as sales data.
    - **Track** unrealized and realized gains/losses on each investment.
    Use the sidebar to interact with the data or update specific investments.
    """)

    # Fetch and display investment data
    investments = database_manipulator.fetch_investments()
    
    if investments:
        data_loader = DataLoader(investments)
        df = data_loader.load_data()
        LOGGER.info(f"df: {df.columns}")

        st.title("Investment Portfolio")
        st.write("### Investment Details")
        st.dataframe(df, hide_index=True)

        # Create a placeholder for displaying icons and investment data
        for idx, row in df.iterrows():
            # Display each row in the dataframe with an "info" button
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**{row['Asset Name']}** ({row['Ticker']})")
                    st.write(f"Purchase Date: {row['Purchase Date']} | Remaining Shares: {row['Remaining Shares']}")
                with col2:
                    # Create an icon button for detailed view
                    if st.button("ℹ️", key=f"info_{idx}"):
                        show_details(row)

def show_details(row):
    """Display a detailed view of the selected investment in an expandable form."""
    with st.expander(f"Details for {row['Asset Name']} ({row['Ticker']})", expanded=True):
        with st.form(key=f"form_{row['ID']}"):
            st.write("### Investment Details")
            st.write(f"**Ticker:** {row['Ticker']}")
            st.write(f"**Asset Name:** {row['Asset Name']}")
            st.write(f"**Purchase Date:** {row['Purchase Date']}")
            st.write(f"**Initial Amount:** {row['Initial Amount']}")
            st.write(f"**Initial Unit Price:** {row['Initial Unit Price']}")
            st.write(f"**Total Cost:** {row['Total Cost']}")
            st.write(f"**Current Price:** {row['Current Price']}")
            st.write(f"**Transaction Fee:** {row['Transaction Fee']}")
            st.write(f"**Unrealized Gain/Loss:** {row['Unrealized Gain/Loss']}")
            st.write(f"**Is Older Than Eight Years:** {row['Is Older Than Eight Years']}")
            st.write(f"**Deemed Disposal Date:** {row['Deemed Disposal Date']}")
            st.write(f"**Deemed Disposal Price:** {row['Deemed Disposal Price']}")
            st.write(f"**Sold Share Status:** {row['Sold Share Status']}")
            st.write(f"**Sale Date:** {row['Sale Date']}")
            st.write(f"**Quantity Sold:** {row['Quantity Sold']}")
            st.write(f"**Sale Price:** {row['Sale Price']}")
            st.write(f"**Remaining Shares:** {row['Remaining Shares']}")
            st.write(f"**Realized Gain/Loss (Deemed Disposal):** {row['Realized Gain/Loss (Deemed Disposal)']}")
            st.write(f"**Realized Gain/Loss:** {row['Realized Gain/Loss']}")

            # Add any editable fields if required (e.g., sale data updates)
            updated_quantity_sold = st.number_input("Update Quantity Sold", value=row['Quantity Sold'], min_value=0)
            updated_sale_price = st.number_input("Update Sale Price", value=row['Sale Price'], min_value=0.0)

            # Submit button to apply updates
            if st.form_submit_button("Update Investment"):
                # Logic to update database (if needed)
                st.success("Investment updated successfully!")
                LOGGER.info(f"Updated investment {row['ID']} with new quantity {updated_quantity_sold} and sale price {updated_sale_price}")
