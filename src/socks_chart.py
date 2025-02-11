import streamlit as st
import yfinance as yf
from modules.stock_chart_agent import StockChartAgent
from streamlit_components.st_horizontal import st_horizontal
import datetime

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
    for key in ["symbol", "time_period", "chart_type", "indicators"]:
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
            symbol= st.text_input(
                "Stock Symbol",
                placeholder="Stock ticker symbol",
            ).upper()
        with col2:
            time_period = st.selectbox(
                "Time Frame",
                ["1d", "1w", "1mo", "3mo", "6mo", "1y", "5y"],
                index=2,
            )
        with col3:
            time_interval = st.selectbox(
                "Time Interval",
                ["1m", "5m", "1d", "1w", "1mo"],
            )
        with col4:
            chart_type = st.selectbox("Chart Type", ["Candlestick", "Line"])
        with col5:
            indicators = st.multiselect(
                "Indicators",
                ["SMA_50", "EMA_20", "RSI", "MACD"],
                max_selections=3,
            )

    if symbol and st.session_state.plot_type == "normal":
        if st.session_state.fsa.is_valid_stock(symbol):

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
        else:
            st.toast(f"Stock ticker symbol {symbol} is not valid")
        st.session_state.plot_type = "none"

    elif symbol and st.session_state.plot_type == "prediction":
        if symbol.split(".") in st.session_state.training_stocks:
            chart = plot_chart(symbol=symbol, plot_type="prediction")

            st.markdown(f"### Predicted Stock Movement for {symbol}")
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.toast(f"Stock ticker symbol {symbol} not found in trained stocks")
        st.session_state.plot_type = "none"

    else:
        st.markdown("### Stock Chart with Indicators & Predictions")
        st.area_chart()

    with st.container():
        with st_horizontal():
            if st.button("Plot", icon="📈"):
                st.session_state.plot_type = "normal"
                st.rerun()

            if st.button("Predict", icon="🔮", disabled=True):
                trained_stocks = st.session_state.get("training_stocks", [])
                if not symbol in trained_stocks:
                    st.toast("One or more selected stocks are not trained!", icon="⚠️")

                st.session_state.plot_type = "prediction"
            if st.button("Reset", icon="❌"):
                reset_selections()
            if st.button("Refresh", icon="🔃"):
                st.cache_data.clear()
