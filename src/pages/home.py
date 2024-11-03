import streamlit as st

from src.utils.database_operations import DatabaseManipulator


def app(database_manipulator: DatabaseManipulator):
    st.title("Welcome to Our Data Analysis App")
    st.write(
        "This app demonstrates various data analysis and visualization techniques."
    )
    st.write("Use the sidebar to navigate between different pages.")
