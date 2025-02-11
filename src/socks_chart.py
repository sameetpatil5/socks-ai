import streamlit as st
import yfinance as yf
from modules.stock_chart_agent import StockChartAgent
from streamlit_components.st_horizontal import st_horizontal
import datetime
import logging

if "plot_type" not in st.session_state:
    st.session_state.plot_type = "none"
if "sca" not in st.session_state:
    st.session_state.sca = StockChartAgent()


@st.cache_data(ttl=datetime.timedelta(days=1), max_entries=100)
def plot_chart(symbol, period, interval, plot_type, chart_type, indicators):
    fig = st.session_state.sca.plot_chart(
        symbol, period, interval, plot_type, chart_type, indicators
    )
    return fig


def reset_selections():
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
    st.rerun()


st.title("Socks Chart")

with st.container(border=True):
    st.markdown("### Stock & Indicators Selection")

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
                index=2,
                key="chart_time_period",
            )
        with col3:
            time_interval = st.selectbox(
                "Time Interval",
                ["1m", "5m", "1d", "1w", "1mo"],
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

    if symbol and st.session_state.plot_type == "normal":
        chart = plot_chart(
            symbol=symbol,
            period=time_period,
            interval=time_interval,
            plot_type="normal",
            chart_type=chart_type,
            indicators=indicators,
        )

        st.markdown(f"### Stock Chart for {symbol}")
        st.plotly_chart(
            chart,
            use_container_width=True,
        )
        st.session_state.plot_type = "none"

    elif symbol and st.session_state.plot_type == "prediction":
        chart = plot_chart(symbol=symbol, plot_type="prediction")

        st.markdown(f"### Predicted Stock Movement for {symbol}")
        st.plotly_chart(chart, use_container_width=True)
        st.session_state.plot_type = "none"

    else:
        st.markdown("### Stock Chart with Indicators & Predictions")
        st.area_chart()

    with st.container():
        with st_horizontal():
            if st.button("Plot", icon="📈"):
                if st.session_state.fsa.is_valid_stock(symbol):
                    st.session_state.plot_type = "normal"
                    st.rerun()
                else:
                    logging.error(
                        f"Stock ticker symbol {symbol} was not found. {symbol} is either invalid or doesn't include the exchange identifiers."
                    )
                    st.toast(f"Stock ticker symbol {symbol} is not valid!", icon="⚠️")

            if st.button(
                "Predict", icon="🔮", disabled=True, help="Under Construction"
            ):
                trained_stocks = st.session_state.get("training_stocks", [])
                if symbol.split(".") in st.session_state.trained_stocks:
                    st.session_state.plot_type = "prediction"
                    st.rerun()
                else:
                    logging.error(
                        f"Stock ticker symbol {symbol} is not trained!. Train {symbol} in Daily Stock Page first!"
                    )
                    st.toast(
                        f"Stock ticker symbol {symbol} is not trained!",
                        icon="⚠️",
                    )

            if st.button("Reset", icon="❌"):
                reset_selections()
            if st.button("Refresh", icon="🔃"):
                st.cache_data.clear()
                st.rerun()
