import requests
import logging

import streamlit as st

from streamlit_components.st_horizontal import st_horizontal
from streamlit_components.st_show_toast import show_toast
from streamlit_components.st_vertical_divider import st_vertical_divider

URL = "http://localhost:8000"

# Configure logging
logger = logging.getLogger("app")

# Page config
st.set_page_config(
    page_title="SocksAI",
    page_icon=":socks:",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Function to fetch scheduler status
def get_scheduler_status():
    try:
        response = requests.get(f"{URL}/scheduler_status")
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Failed to fetch scheduler status."}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


# Function to reload stocks
def reload_stocks():
    try:
        response = requests.post(f"{URL}/reload_stocks")
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Failed to reload stocks."}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


@st.dialog("Quick Analysis")
def quick_analysis():
    """
    Perform a quick analysis for all monitored stocks.
    """

    st.html("<span class='big-dialog'></span>")

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
            with st_horizontal():
                for stock in st.session_state.found_stocks:
                    is_selected = stock in st.session_state.added_stocks
                    btn_label = f"✅ {stock}" if is_selected else stock

                    if st.button(btn_label, key=f"add_daily_{stock}"):
                        if is_selected:
                            st.session_state.added_stocks.remove(stock)
                        else:
                            st.session_state.added_stocks.append(stock)

            st.write("Click a stock to add/remove it. Use 'Select All' to choose all.")
    except Exception as e:
        logger.error(f"Error while loading dialog to add daily stocks: {e}")

    try:
        with st_horizontal():
            if st.button("Confirm & Add", key="confirm_daily_stocks"):
                final_stocks = [
                    stock
                    for stock in st.session_state.added_stocks
                    if stock not in st.session_state.daily_stocks
                ]
                st.session_state.daily_stocks.extend(final_stocks)
                st.session_state.dssa.add_stocks(final_stocks)
                st.session_state.found_stocks = []
                st.session_state.added_stocks = []

                # Reload the stocks for the scheduler
                response = reload_stocks()
                if response["success"]:
                    logger.info("Successfully reloaded stocks for the scheduler.")
                else:
                    logger.error("Failed to reload stocks for the scheduler.")
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
            with st_horizontal():
                for stock in st.session_state.found_stocks:
                    is_selected = stock in st.session_state.added_stocks
                    btn_label = f"❌ {stock}" if is_selected else stock

                    if st.button(btn_label, key=f"remove_daily_{stock}"):
                        if is_selected:
                            st.session_state.added_stocks.remove(stock)
                        else:
                            st.session_state.added_stocks.append(stock)

            st.write("Click a stock to add/remove it. Use 'Select All' to choose all.")
    except Exception as e:
        logger.error(f"Error while loading dialog to remove daily stocks: {e}")

    try:
        with st_horizontal():
            if st.button("Confirm & Remove", key="confirm_remove_daily"):
                st.session_state.daily_stocks = [
                    stock
                    for stock in st.session_state.daily_stocks
                    if stock not in st.session_state.added_stocks
                ]
                st.session_state.dssa.remove_stocks(st.session_state.added_stocks)
                st.session_state.found_stocks = []
                st.session_state.added_stocks = []

                # Reload the stocks for the scheduler
                response = reload_stocks()
                if response["success"]:
                    logger.info("Successfully reloaded stocks for the scheduler.")
                else:
                    logger.error("Failed to reload stocks for the scheduler.")
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
    scheduler_buttons, scheduler_divider, scheduler_status = st.columns([1, 0.1, 3])

    with scheduler_buttons.container(height=scheduler_section_height, border=False):
        if st.button(
            "Start Daily Socks Scheduler",
            key="start_daily_socks_scheduler",
            use_container_width=True,
        ):
            try:
                response = requests.post(f"{URL}/start_scheduler")
                if response.status_code == 200:
                    show_toast("Daily Socks Scheduler started successfully.")
                    st.rerun()
                else:
                    show_toast("❌ Failed to start scheduler.")
            except requests.exceptions.RequestException as e:
                logger.error(f"Error while starting stock scheduler: {e}")

        if st.button(
            "Stop Daily Socks Scheduler",
            key="stop_daily_socks_scheduler",
            use_container_width=True,
            type="primary",
        ):
            try:
                response = requests.post(f"{URL}/stop_scheduler")
                if response.status_code == 200:
                    show_toast("Daily Socks Scheduler stopped successfully.")
                    st.rerun()
                else:
                    show_toast("❌ Failed to stop scheduler.")
            except requests.exceptions.RequestException as e:
                logger.error(f"Error while stopping stock scheduler: {e}")

    with scheduler_divider.container(border=False):
        st_vertical_divider(scheduler_section_height)

    with scheduler_status.container(height=scheduler_section_height, border=False):
        scheduler_status = get_scheduler_status()

        if "error" in scheduler_status:
            st.error(scheduler_status["error"])
        else:
            jobs = scheduler_status["status"]  # Dictionary containing job statuses
            all_stopped = all(jobs[job]["Paused"] == "Job not found" for job in jobs)
            all_running = all(jobs[job]["Paused"] == False for job in jobs)

            if all_stopped:
                st.write("##### Scheduler Status:")
                st.warning("🚫 Scheduler is stopped. No active jobs.")
            elif all_running:
                st.success("✅ Scheduler is running. All jobs are active.")
                with st.expander("Show Scheduler Details"):
                    for job, details in jobs.items():
                        paused = details["Paused"]
                        next_run = details["Next Run"]

                        if paused == "Job not found" or paused == True:
                            st.error(f"❌ **{job}** - **Stopped**")
                        else:
                            st.success(f"✅ **{job}** - Running | Next Run: {next_run}")
