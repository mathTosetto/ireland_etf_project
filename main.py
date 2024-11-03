import streamlit as st

from src.utils.database_operations import DatabaseManipulator
from src.pages import home, investment_rules, insert_form, view_investments

PAGES = {
    "Home": home,
    "Insert Form": insert_form,
    "View Investments": view_investments,
    "Investment Rules": investment_rules
}


def init_db(database_name: str) -> None:
    return DatabaseManipulator(database_name)


def main(database_manipulator: DatabaseManipulator):
    st.sidebar.title("Pages")
    selection = st.sidebar.radio("Navigate", list(PAGES.keys()))
    page = PAGES[selection]
    page.app(database_manipulator)


if __name__ == "__main__":
    database_manipulator = init_db("etf_investments.db")
    main(database_manipulator)