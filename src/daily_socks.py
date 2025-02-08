import streamlit as st
from modules.find_stock_agent import FindStockAgent
from modules.daily_stock_sentiment_agent import DailyStockSentimentAgent
from contextlib import contextmanager
import os

# Initialize stock lists in session state
if "fsa" not in st.session_state:
    st.session_state.fsa = FindStockAgent()

if "dssa" not in st.session_state:
    st.session_state.dssa = DailyStockSentimentAgent(
        os.environ.get("MONGO_URI"), os.environ.get("MONGO_DB")
    )

if "daily_stocks" not in st.session_state:
    st.session_state.daily_stocks = st.session_state.dssa.stocks

if "training_stocks" not in st.session_state:
    st.session_state.training_stocks = []

if "found_stocks" not in st.session_state:
    st.session_state.found_stocks = []

if "added_stocks" not in st.session_state:
    st.session_state.added_stocks = []


# Styling for horizontal elements
HORIZONTAL_STYLE = """
    <style class="hide-element">
        /* Hides the style container and removes the extra spacing */
        .element-container:has(.hide-element) {
            display: none;
        }
        /*
            The selector for >.element-container is necessary to avoid selecting the whole
            body of the streamlit app, which is also a stVerticalBlock.
        */
        div[data-testid="stVerticalBlock"]:has(> .element-container .horizontal-marker) {
            display: flex;
            flex-direction: row !important;
            flex-wrap: wrap;
            gap: 0.5rem;
            align-items: baseline;
        }
        /* Buttons and their parent container all have a width of 704px, which we need to override */
        div[data-testid="stVerticalBlock"]:has(> .element-container .horizontal-marker) div {
            width: max-content !important;
        }
        /* Just an example of how you would style buttons, if desired */
        /*
        div[data-testid="stVerticalBlock"]:has(> .element-container .horizontal-marker) button {
            border-color: red;
        }
        */
    </style>
"""


@contextmanager
def st_horizontal():
    st.markdown(HORIZONTAL_STYLE, unsafe_allow_html=True)
    with st.container():
        st.markdown(
            '<span class="hide-element horizontal-marker"></span>',
            unsafe_allow_html=True,
        )
        yield


@st.dialog("Quick Analysis")
def quick_analysis():
    """Perform a quick analysis for all monitored stocks."""

    st.html("<span class='big-dialog'></span>")

    if not st.session_state.dssa.stocks:
        st.toast("No stocks to analyze.")
        return

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
            # st.markdown(f"**💡 Summary:** {summary_text}")

            # Optional: Use an Expander for a cleaner look
            with st.expander("🔍 Detailed Analysis"):
                st.write(summary_text)


@st.dialog("Add Daily Stocks")
def add_daily_stock():
    """Allows users to search for and add daily stocks."""
    query = st.text_input("Enter a stock symbol or query:")
    if st.button("Find Stocks", key="find_daily_stocks"):
        st.session_state.found_stocks = st.session_state.fsa.add_stock(query)
        st.session_state.added_stocks = []
        if not st.session_state.found_stocks:
            st.toast("No stocks found. Please try again.")

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
                st.rerun()

            if st.button("Select All", key="select_all_daily_stocks"):
                st.session_state.added_stocks = st.session_state.found_stocks


@st.dialog("Remove Daily Stocks")
def remove_daily_stock():
    """Allows users to remove selected daily stocks."""
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

    with st_horizontal():
        if st.button("Confirm & Remove", key="confirm_remove_daily"):
            st.session_state.daily_stocks = [
                s
                for s in st.session_state.daily_stocks
                if s not in st.session_state.added_stocks
            ]
            st.session_state.found_stocks = []
            st.session_state.added_stocks = []
            st.rerun()

        if st.button("Select All", key="select_all_daily_stocks"):
            st.session_state.added_stocks = st.session_state.found_stocks


@st.dialog("Add Training Stocks")
def add_training_stock():
    """Allows users to search for and add training stocks."""
    query = st.text_input("Enter a stock symbol or query:")
    if st.button("Find Stocks", key="find_training_stocks"):
        st.session_state.found_stocks = st.session_state.fsa.add_stock(query)
        st.session_state.added_stocks = []
        if not st.session_state.found_stocks:
            st.toast("No stocks found. Please try again.")

    if st.session_state.found_stocks:
        st.markdown("### Found Stocks:")
        with st_horizontal():
            for stock in st.session_state.found_stocks:
                is_selected = stock in st.session_state.added_stocks
                btn_label = f"✅ {stock}" if is_selected else stock

                if st.button(btn_label, key=f"add_training_{stock}"):
                    if is_selected:
                        st.session_state.added_stocks.remove(stock)
                    else:
                        st.session_state.added_stocks.append(stock)

        st.write("Click a stock to add/remove it. Use 'Select All' to choose all.")

        with st_horizontal():
            if st.button("Confirm & Add", key="confirm_training_stocks"):
                st.session_state.training_stocks.extend(
                    [
                        stock
                        for stock in st.session_state.added_stocks
                        if stock not in st.session_state.training_stocks
                    ]
                )
                st.session_state.found_stocks = []
                st.session_state.added_stocks = []
                st.rerun()

            if st.button("Select All", key="select_all_training_stocks"):
                st.session_state.added_stocks = st.session_state.found_stocks


@st.dialog("Remove Training Stocks")
def remove_training_stock():
    """Allows users to remove selected training stocks."""
    st.markdown("### Select Stocks to Remove:")
    st.session_state.found_stocks = st.session_state.training_stocks

    if st.session_state.found_stocks:
        with st_horizontal():
            for stock in st.session_state.found_stocks:
                is_selected = stock in st.session_state.added_stocks
                btn_label = f"❌ {stock}" if is_selected else stock

                if st.button(btn_label, key=f"remove_training_{stock}"):
                    if is_selected:
                        st.session_state.added_stocks.remove(stock)
                    else:
                        st.session_state.added_stocks.append(stock)

        st.write("Click a stock to add/remove it. Use 'Select All' to choose all.")

    with st_horizontal():
        if st.button("Confirm & Remove", key="confirm_remove_training"):
            st.session_state.training_stocks = [
                s
                for s in st.session_state.training_stocks
                if s not in st.session_state.added_stocks
            ]
            st.session_state.found_stocks = []
            st.session_state.added_stocks = []
            st.rerun()

        if st.button("Select All", key="select_all_training_stocks"):
            st.session_state.added_stocks = st.session_state.found_stocks


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
        st.button("Perform Quick Analysis", on_click=quick_analysis, key="quick_analysis")

# Training Stocks Section
with st.container(border=True):
    st.markdown("### Train SocksAI for Future Prediction")
    with st_horizontal():
        for stock in st.session_state.training_stocks:
            with st.container(border=True):
                st.markdown(f"**{stock}**")
    with st_horizontal():
        st.button(
            "Train more Stocks", on_click=add_training_stock, key="add_training_stocks"
        )
        st.button(
            "Remove Stocks",
            on_click=remove_training_stock,
            key="remove_training_stocks",
            type="primary",
            disabled=not st.session_state.training_stocks,
        )
