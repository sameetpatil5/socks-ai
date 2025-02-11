import streamlit as st
import yfinance as yf
from streamlit_components.st_horizontal import st_horizontal
import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


@st.cache_data(ttl=datetime.timedelta(days=1), max_entries=100)
def plot_chart(
    symbol: str,
    period: str,
    interval: str,
    plot_type: str,
    chart_type: str,
    indicators: list,
):
    """
    Generates a stock chart with given parameters.

    Args:
        symbol (str): Stock ticker symbol.
        period (str): Time period for historical data.
        interval (str): Time interval for stock data.
        plot_type (str): Type of plot - "normal" for stock chart, "prediction" for forecast.
        chart_type (str): Chart type - "Candlestick" or "Line".
        indicators (list): List of indicators to include in the chart.

    Returns:
        go.Figure: A Plotly figure containing the stock chart.
    """
    logging.info(
        f"Plotting chart for {symbol} with period={period}, interval={interval}, type={plot_type}"
    )
    fig = st.session_state.sca.plot_chart(
        symbol, period, interval, plot_type, chart_type, indicators
    )
    return fig


def reset_selections():
    """
    Resets all user selections and reloads the page.
    """
    logging.info("Resetting user selections.")
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
            time_period = st.selectbox(
                "Time Frame",
                ["1d", "1w", "1mo", "3mo", "6mo", "1y", "5y"],
                index=0,
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
                ["SMA_50", "EMA_20", "RSI", "MACD"],
                max_selections=2,
                key="chart_indicators",
            )

    # Chart Rendering Logic
    if symbol and st.session_state.plot_type == "normal":
        logging.info(f"Generating normal stock chart for {symbol}.")
        chart = plot_chart(
            symbol=symbol,
            period=time_period,
            interval=time_interval,
            plot_type="normal",
            chart_type=chart_type,
            indicators=indicators,
        )
        st.markdown(f"### Stock Chart for {symbol}")
        st.plotly_chart(chart, use_container_width=True)
        st.session_state.plot_type = "none"

    elif symbol and st.session_state.plot_type == "prediction":
        logging.info(f"Generating predicted stock movement chart for {symbol}.")
        chart = plot_chart(symbol=symbol, plot_type="prediction")
        st.markdown(f"### Predicted Stock Movement for {symbol}")
        st.plotly_chart(chart, use_container_width=True)
        st.session_state.plot_type = "none"

    else:
        st.markdown("### Stock Chart with Indicators & Predictions")
        st.area_chart()

    # Button Actions
    with st.container():
        with st_horizontal():
            if st.button("Plot", icon="📈"):
                if st.session_state.fsa.is_valid_stock(symbol):
                    logging.info(
                        f"Valid stock symbol detected: {symbol}. Proceeding to plot."
                    )
                    st.session_state.plot_type = "normal"
                    st.rerun()
                else:
                    logging.error(
                        f"Stock ticker symbol {symbol} was not found. {symbol} is either invalid or missing exchange identifiers."
                    )
                    st.toast(f"Stock ticker symbol {symbol} is not valid!", icon="⚠️")

            if st.button(
                "Predict", icon="🔮", disabled=True, help="Under Construction"
            ):
                trained_stocks = st.session_state.get("training_stocks", [])
                if symbol.split(".") in st.session_state.trained_stocks:
                    logging.info(
                        f"Stock {symbol} found in trained stocks. Plotting prediction."
                    )
                    st.session_state.plot_type = "prediction"
                    st.rerun()
                else:
                    logging.error(
                        f"Stock ticker symbol {symbol} is not trained! Train {symbol} in Daily Stock Page first!"
                    )
                    st.toast(f"Stock ticker symbol {symbol} is not trained!", icon="⚠️")

            if st.button("Reset", icon="❌"):
                reset_selections()

            if st.button("Refresh", icon="🔃"):
                logging.info("Clearing cache and refreshing page.")
                st.cache_data.clear()
                st.rerun()
