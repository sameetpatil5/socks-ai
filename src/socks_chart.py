import datetime as dt
from typing import Tuple
import logging

import streamlit as st
import plotly.graph_objects as go

from streamlit_components.st_horizontal import st_horizontal
from streamlit_components.st_show_toast import show_toast

# Configure logging
logger = logging.getLogger("app")

# Page config
st.set_page_config(
    page_title="SocksAI",
    page_icon=":socks:",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(ttl=dt.timedelta(days=1), max_entries=100)
def plot_chart(
    symbol: str,
    period: Tuple[dt.date, dt.date],
    interval: str,
    chart_type: str,
    indicators: list,
) -> go.Figure:
    """
    Plots a chart for the given stock symbol with the specified period, interval, chart type, and indicators.

    Args:
        symbol (str): The stock ticker symbol (e.g., "AAPL").
        period (Tuple[dt.date, dt.date]): The time period for historical data.
        interval (str): The interval for stock data points (e.g., "1d").
        chart_type (str): Type of chart - "candlestick" or "line".
        indicators (list): List of indicators to include in the chart (e.g., ["SMA_20", "EMA_20"]).

    Returns:
        go.Figure: A Plotly figure containing the stock chart.
    """
    try:
        logger.info(
            f"Plotting chart for {symbol} with period={period}, interval={interval}"
        )
        fig = st.session_state.sca.plot_chart(
            symbol, period, interval, chart_type, indicators
        )
        show_toast(f"Plotted the Chart for {symbol}")
        return fig
    except Exception as e:
        logger.error(
            f"Error while plotting chart for {symbol} with period={period}, interval={interval}: {e}"
        )
        return go.Figure()


def both_interval_selected(time_period):
    """
    Checks if the given time_period is a tuple of two dates.

    Args:
        time_period (tuple or other): The time period to check.

    Returns:
        bool: True if the time period is a tuple of two dates, False otherwise.
    """
    if isinstance(time_period, tuple) and len(time_period) == 2 and all(isinstance(d, dt.date) for d in time_period):
        return True
    return False


def reset_selections():
    """
    Resets all user selections and reloads the page.
    """
    logger.info("Resetting user selections.")
    for key in [
        "chart_symbol",
        "chart_time_period",
        "chart_time_interval",
        "chart_chart_type",
        "chart_indicators",
    ]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()


@st.dialog("Stock Chart Analysis")
def analyze_chart(chart: go.Figure):
    """
    Analyzes the stock chart and returns a summary.

    Args:
        chart (go.Figure): The plotted stock chart to be analyzed. 
    """
    st.html("<span class='big-dialog'></span>")

    try:
        logger.info(f"Analysing Stock Chart...")
        response = st.session_state.sca.analyze_plot(chart)

        with st.spinner("Reading Chart"):
            st.write_stream(response)
        logger.info("Loaded the AI response from Chart Agent")
    except:
        logger.error("Error while Analysing Stock Chart")

# Page Title
st.title("Socks Chart")

with st.container(border=True):
    st.markdown("### Stock & Indicators Selection")

    # Input Section
    with st.container():
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1.5, 4])

        with col1:
            symbol = st.text_input(
                "Stock Symbol", placeholder="Stock ticker symbol", key="chart_symbol"
            ).upper()
        with col2:
            time_period = st.date_input(
                "Time Period",
                value=(dt.date.today() - dt.timedelta(days=1), dt.date.today()),
                max_value=dt.date.today(),
                key="chart_time_period",
            )
        with col3:
            time_interval = st.selectbox(
                "Time Interval",
                ["1m", "5m", "1d", "1w", "1mo"],
                index=1,
                key="chart_time_interval",
            )
        with col4:
            chart_type = st.selectbox(
                "Chart Type", ["Candlestick", "Line"], key="chart_chart_type"
            )
        with col5:
            indicators = st.multiselect(
                "Indicators",
                ["SMA_20", "EMA_20", "BB_20", "VWAP"],
                default=["SMA_20", "EMA_20"],
                key="chart_indicators",
            )

    # Chart Rendering Logic
    if symbol:
        logger.info(f"Generating normal stock chart for {symbol}.")

        if both_interval_selected(time_period):
            chart = plot_chart(
                symbol=symbol,
                period=time_period,
                interval=time_interval,
                chart_type=chart_type,
                indicators=indicators,
            )
            st.markdown(f"### Stock Chart for {symbol}")
            fig = st.plotly_chart(chart, use_container_width=True)
        else:
            st.markdown(f"### Stock Chart for {symbol}")
            st.area_chart()

    else:
        st.markdown("### Stock Chart with Indicators & Predictions")
        st.area_chart()

    # Button Actions
    with st.container():
        with st_horizontal():
            if st.button("Plot", icon="📈"):
                if st.session_state.fsa.is_valid_stock(symbol):
                    logger.info(
                        f"Valid stock symbol detected: {symbol}. Proceeding to plot."
                    )
                    st.rerun()
                else:
                    logger.error(
                        f"Stock ticker symbol {symbol} was not found. {symbol} is either invalid or missing exchange identifiers."
                    )
                    show_toast(f"⚠️ Stock ticker symbol {symbol} is not valid!")

            if st.button("Analyze", icon="🔍"):
                analyze_chart(chart)

            if st.button("Reset", icon="❌"):
                reset_selections()

            if st.button("Refresh", icon="🔃", help="Clears all the cache data and performs a refresh"):
                logger.info("Clearing cache and refreshing page.")
                st.cache_data.clear()
                show_toast("Cleared the Streamlit Cache Data!")
                st.rerun()
