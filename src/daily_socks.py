import requests
import logging

import streamlit as st

from streamlit_components.st_horizontal import st_horizontal
from streamlit_components.st_show_toast import show_toast
from streamlit_components.st_vertical_divider import st_vertical_divider
from streamlit_components.st_wide_dialog import st_wide_dialog

# Configure logging
logger = logging.getLogger("app")

# Page config
st.set_page_config(
    page_title="SocksAI",
    page_icon=":socks:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Scheduler state Mapping
SCHEDULER_STATE = {
    0: "Stopped",
    1: "Running",
    2: "Paused",
}


# Function to fetch scheduler status
def get_scheduler_status():
    """
    Fetches the current status of the daily stock sentiment analysis scheduler.

    Returns a dictionary with one of the following structures:

    - If successful, returns a dictionary with the following keys:
        - "success": boolean indicating whether the request was successful.
        - "message": string indicating the current state of the scheduler.
    - If unsuccessful, returns a dictionary with the following keys:
        - "error": string indicating the error that occurred.

    :return: A dictionary with the current status of the scheduler.
    :rtype: Dict[str, Union[bool, str]]
    """
    
    try:
        response = requests.get(f"{st.session_state.server_url}/scheduler_status")
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Failed to fetch scheduler status."}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


# Function to get scheduler state
def scheduler_state() -> int:
    """
    Fetches the current state of the daily stock sentiment analysis scheduler.

    Returns:
        int: The current state of the scheduler, which can be one of the following:
            - 0: Stopped
            - 1: Running
            - 2: Paused
        If the request fails or an error occurs, it defaults to returning 0.

    Exceptions:
        If a network-related error occurs during the request, returns a dictionary
        with an "error" key containing the error message.
    """

    try:
        response = requests.get(f"{st.session_state.server_url}/scheduler_state")
        if response.status_code == 200:
            if response.json()["success"] == True:
                state = response.json()["state"]
                show_toast(f"Scheduler is currently in {SCHEDULER_STATE[state]} state")
                return state
            else:
                return 0
        else:
            return 0
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


# Function to reload stocks
def reload_stocks():
    """
    Reload stock symbols from MongoDB for the scheduler.
    """
    try:
        response = requests.post(f"{st.session_state.server_url}/reload_stocks")
        if response.status_code == 200 and response.json()["success"] == True:
            logger.info("Successfully reloaded stocks for the scheduler.")
        else:
            logger.error("Failed to reload stocks for the scheduler.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error while reloading stocks for the scheduler: {e}")


# Function to start scheduler
def start_scheduler():
    """
    Start the daily stock sentiment analysis scheduler by sending a request
    to the server.
    """
    try:
        response = requests.post(f"{st.session_state.server_url}/start_scheduler")
        if response.status_code == 200:
            logger.info("Scheduler started successfully.")
            show_toast("Daily Socks Scheduler started successfully.")
            st.rerun()
        else:
            logger.error("Failed to start scheduler.")
            show_toast("❌ Failed to start scheduler.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error while starting stock scheduler: {e}")


# Function to stop scheduler
def stop_scheduler():
    """
    Stop the daily stock sentiment analysis scheduler by sending a request
    to the server.
    """

    try:
        response = requests.post(f"{st.session_state.server_url}/stop_scheduler")
        if response.status_code == 200:
            logger.info("Scheduler stopped successfully.")
            show_toast("Daily Socks Scheduler stopped successfully.")
            st.rerun()
        else:
            logger.error("Failed to stop scheduler.")
            show_toast("❌ Failed to stop scheduler.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error while stopping stock scheduler: {e}")


# Function to toggle scheduler
def toggle_scheduler():
    """
    Toggle the state of the daily stock sentiment analysis scheduler by
    sending a request to the server.
    """

    try:
        response = requests.post(f"{st.session_state.server_url}/toggle_scheduler")
        if response.status_code == 200:
            status_message = response.json()["message"]
            logger.info(f"Scheduler toggled successfully. {status_message}")
            show_toast(status_message)
        else:
            error_message = response.json()["error"]
            logger.error(f"Failed to toggle scheduler: {error_message}")
            show_toast(error_message)
            logger.error(f"Failed to toggle scheduler: {error_message}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error while toggling stock scheduler: {e}")


# Function to refresh scheduler
def refresh_scheduler():
    """
    Refresh the daily stock sentiment analysis scheduler completely.
    """

    try:
        response = requests.post(f"{st.session_state.server_url}/refresh_scheduler")
        if response.status_code == 200:
            logger.info("Scheduler refreshed successfully.")
            st.session_state["pause_scheduler"] = False
            logger.info("Scheduler refreshed successfully.")
            show_toast("Daily Socks Scheduler refreshed successfully.")
            st.rerun()
        else:
            logger.error("Failed to refresh scheduler.")
            show_toast("❌ Failed to refresh scheduler.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error while refreshing stock scheduler: {e}")


@st.dialog("Quick Analysis")
def quick_analysis():
    """
    Perform a quick analysis for all monitored stocks.
    """

    st_wide_dialog()

    if not st.session_state.dssa.stocks:
        show_toast("No stocks to Analyze")
        st.rerun()

    try:
        logger.info("Generating Quick analysis...")
        summaries = st.session_state.dssa.perform_quick_analysis()

        st.markdown("## 📊 Quick Analysis Summaries")

        if not summaries:
            st.info("No analysis results available.")
            return

        for summary in summaries:
            with st.container():
                # Extract stock details from the summary (assuming summary is a dict)
                symbol = summary.get("symbol", "N/A")
                price_data = summary.get("price", {})
                price = price_data.get("price", "N/A")  # Float
                currency = price_data.get("currency", "")  # String
                full_price = f"{currency} {price}" if price != "N/A" else "N/A"
                summary_text = summary.get("summary", "No summary available.")

                # Display Stock Info
                st.markdown(f"### 📈 {symbol} - {full_price}")

                # Optional: Use an Expander for a cleaner look
                with st.expander("🔍 Detailed Analysis"):
                    st.write(summary_text)
        logger.info("Generated Quick analysis for all daily stocks")

    except Exception as e:
        logger.error(f"Error while performing quick analysis: {e}")


@st.dialog("Add Daily Stocks")
def add_daily_stock():
    """
    Allows users to search for and add daily stocks.
    """
    try:
        query = st.text_input("Enter a stock symbol or query:")
        if st.button("Find Stocks", key="find_daily_stocks"):
            st.session_state.found_stocks = st.session_state.fsa.find_stock(query)
            st.session_state.added_stocks = []
            if not st.session_state.found_stocks:
                show_toast("No stocks found. Please try again.")

        if st.session_state.found_stocks:
            st.markdown("### Found Stocks:")
            stocks_to_add = st.pills(
                label="Add Daily Stocks",
                options=st.session_state.found_stocks,
                selection_mode="multi",
                default=st.session_state.added_stocks,
                key="add_daily_stocks_pills",
                label_visibility="collapsed",
            )
            st.write("Click a stock to add/remove it.")
    except Exception as e:
        logger.error(f"Error while loading dialog to add daily stocks: {e}")

    try:
        st.write("Double Click `Select All` to choose all.")
        with st_horizontal():
            if st.button("Confirm & Add", key="confirm_daily_stocks"):
                final_stocks = [
                    stock
                    for stock in stocks_to_add
                    if stock not in st.session_state.daily_stocks
                ]
                st.session_state.daily_stocks.extend(final_stocks)
                st.session_state.dssa.add_stocks(final_stocks)
                st.session_state.found_stocks = []
                st.session_state.added_stocks = []

                if st.session_state.server_url == "":
                    logger.warning(
                        "Server URL is not set. Daily stocks will not reloaded."
                    )
                else:
                    # Reload the stocks for the scheduler
                    reload_stocks()

                    show_toast("Successfully Added Daily stocks from Database")
                    st.rerun()

            if st.button("Select All", key="select_all_daily_stocks"):
                st.session_state.added_stocks = st.session_state.found_stocks
    except Exception as e:
        logger.error("Error while adding daily stocks.")


@st.dialog("Remove Daily Stocks")
def remove_daily_stock():
    """
    Allows users to remove selected daily stocks.
    """
    try:
        st.markdown("### Select Stocks to Remove:")
        st.session_state.found_stocks = st.session_state.daily_stocks

        if st.session_state.found_stocks:
            stocks_to_remove = st.pills(
                label="Remove Daily Stocks",
                options=st.session_state.found_stocks,
                selection_mode="multi",
                default=st.session_state.added_stocks,
                key="remove_daily_stocks_pills",
                label_visibility="collapsed",
            )
            st.write("Click a stock to add/remove it.")
    except Exception as e:
        logger.error(f"Error while loading dialog to remove daily stocks: {e}")

    try:
        st.write("Double Click `Select All` to choose all.")
        with st_horizontal():
            if st.button("Confirm & Remove", key="confirm_remove_daily"):
                st.session_state.daily_stocks = [
                    stock
                    for stock in st.session_state.daily_stocks
                    if stock not in stocks_to_remove
                ]
                st.session_state.dssa.remove_stocks(stocks_to_remove)
                st.session_state.found_stocks = []
                st.session_state.added_stocks = []

                if st.session_state.server_url == "":
                    logger.warning(
                        "Server URL is not set. Daily stocks will not reloaded."
                    )
                else:
                    # Reload the stocks for the scheduler
                    reload_stocks()

                    show_toast("Successfully Removed Daily stocks from Database")
                    st.rerun()

            if st.button("Select All", key="select_all_daily_stocks"):
                st.session_state.added_stocks = st.session_state.found_stocks
    except Exception as e:
        logger.error("Error while removing daily stocks.")


# UI Layout
st.title("Daily Socks & Socks Training")

# Daily Stocks Section
with st.container(border=True):
    st.markdown("### Stocks with Daily Socks Sentiment Analysis")
    with st_horizontal():
        for stock in st.session_state.daily_stocks:
            with st.container(border=True):
                st.markdown(f"**{stock}**")

    with st_horizontal():
        st.button("Add more Stocks", on_click=add_daily_stock, key="add_daily_stocks")
        st.button(
            "Remove Stocks",
            on_click=remove_daily_stock,
            key="remove_daily_stocks",
            type="primary",
            disabled=not st.session_state.daily_stocks,
        )
        st.button(
            "Perform Quick Analysis", on_click=quick_analysis, key="quick_analysis"
        )

# Daily Stocks Analysis Scheduler Section
with st.container(border=True):
    scheduler_section_height = 300
    st.markdown("### Daily Stocks Analysis Scheduler")
    if st.session_state.server_url == "":
        st.warning(
            "You are not connected to a server. Please provide the server URL in the sidebar to use the scheduler.",
            icon="⚠️",
        )
        logger.warning("Server URL is not set. Daily stocks will not be scheduled.")
    else:
        scheduler_buttons, scheduler_divider, scheduler_status = st.columns([1, 0.1, 3])

        with scheduler_buttons.container(height=scheduler_section_height, border=False):
            st.button(
                "Start Daily Socks Scheduler",
                key="start_daily_socks_scheduler",
                use_container_width=True,
                on_click=start_scheduler,
            )
            st.button(
                "Stop Daily Socks Scheduler",
                key="stop_daily_socks_scheduler",
                use_container_width=True,
                type="primary",
                on_click=stop_scheduler,
            )

            st.button(
                "Refresh Scheduler",
                key="refresh_scheduler",
                use_container_width=True,
                on_click=refresh_scheduler,
            )

            st.toggle(
                "Pause Scheduler",
                key="pause_scheduler",
                on_change=toggle_scheduler,
                disabled=scheduler_state() == 0,
            )

        with scheduler_divider.container(border=False):
            st_vertical_divider(scheduler_section_height)

        with scheduler_status.container(height=scheduler_section_height, border=False):
            scheduler_response = get_scheduler_status()
            if "error" in scheduler_response:
                st.error(scheduler_status["error"])
                logger.error(
                    f"Failed to get scheduler status. {scheduler_response["error"]}"
                )
            else:
                scheduler_status_response = scheduler_response["status"]
                scheduler_state_reponse = int(scheduler_status_response["State"])

                if scheduler_state_reponse == 1:
                    st.write("##### Scheduler Status:")
                    st.success(
                        f"✅ Scheduler is {SCHEDULER_STATE[scheduler_state_reponse]}."
                    )
                    logger.info(
                        f"Scheduler is running. Scheduler Jobs: {scheduler_status_response["Jobs"]}"
                    )
                    with st.expander("Show Scheduler Details"):
                        for job, details in scheduler_status_response["Jobs"].items():
                            if details == "Job not found":
                                st.error(f"⚠️ **{job}** - **Job not found**")
                            else:
                                st.success(f"**{job}** - Running | Next Run: {details}")
                else:
                    st.write("##### Scheduler Status:")
                    st.warning(
                        f"🚫 Scheduler is {SCHEDULER_STATE[scheduler_state_reponse]}. No active jobs."
                    )
                    logger.info(f"Scheduler is not running.")
