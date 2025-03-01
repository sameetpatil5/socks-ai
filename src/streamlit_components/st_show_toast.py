import streamlit as st


# Function to show a toast message
def show_toast(message: str) -> None:
    """
    Displays a toast message on the Streamlit application.

    Args:
        message (str): The message to be displayed as a toast notification.
    """

    st.session_state.show_toast = True
    st.session_state.toast_message = message
