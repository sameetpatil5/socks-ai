import streamlit as st
from modules.find_stock_agent import FindStockAgent
from contextlib import contextmanager

# Initialize stock lists in session state
if "daily_stocks" not in st.session_state:
    st.session_state.daily_stocks = []

if "training_stocks" not in st.session_state:
    st.session_state.training_stocks = []

if "found_stocks" not in st.session_state:
    st.session_state.found_stocks = []

if "added_stocks" not in st.session_state:
    st.session_state.added_stocks = []

if "stock_for_sentiment" not in st.session_state:
    st.session_state.stock_for_sentiment = False

if "stock_for_training" not in st.session_state:
    st.session_state.stock_for_training = False

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


@st.dialog("Find & Add Stocks")
def add_stock():
    """Dialog box for finding and adding stocks"""

    query = st.text_input("Enter a stock symbol or query:")

    if st.button("Find Stocks", key="find_stocks"):
        find_stock_agent = FindStockAgent()
        st.session_state.found_stocks = find_stock_agent.add_stock(query)

    if st.session_state.found_stocks:
        st.markdown("### Found Stocks:")
        with st_horizontal():
            for stock in st.session_state.found_stocks:
                is_selected = (
                    stock in st.session_state.added_stocks
                )  # Check if stock is added
                btn_label = (
                    f"✅ {stock}" if is_selected else stock
                )  # Change button text

                if st.button(btn_label, key=f"add_{stock}"):
                    if is_selected:
                        st.session_state.added_stocks.remove(stock)  # Remove stock
                    else:
                        st.session_state.added_stocks.append(stock)  # Add stock
        st.write("Double on a stock to add it to the list.")

        if st.button("Confirm & Add", key="add_stocks"):
            if st.session_state.stock_for_sentiment:
                st.session_state.daily_stocks.extend(st.session_state.added_stocks)
                st.session_state.stock_for_sentiment = False
            elif st.session_state.stocks_for_training:
                st.session_state.training_stocks.extend(st.session_state.added_stocks)
                st.session_state.stocks_for_training = False

            # Clear found stocks after adding
            st.session_state.found_stocks = []
            st.session_state.added_stocks = []
            st.rerun()


@st.dialog("Remove Stocks")
def remove_stock():
    """Dialog box for removing stocks"""
    st.markdown("### Select Stocks to Remove:")

    with st_horizontal():
        if st.session_state.stock_for_sentiment:
            st.session_state.found_stocks = st.session_state.daily_stocks
        elif st.session_state.stock_for_training:
            st.session_state.found_stocks = st.session_state.training_stocks

    if st.session_state.found_stocks:
        with st_horizontal():
            for stock in st.session_state.found_stocks:
                is_selected = (
                    stock in st.session_state.added_stocks
                )  # Check if stock is added
                btn_label = (
                    f"❌ {stock}" if is_selected else stock
                )  # Change button text

                if st.button(btn_label, key=f"add_{stock}"):
                    if is_selected:
                        st.session_state.added_stocks.remove(stock)  # Remove stock
                    else:
                        st.session_state.added_stocks.append(stock)  # Add stock
        st.write("Double on a stock to add it to the list.")

        if st.button("Confirm & Remove", key="remove_stocks"):
            if st.session_state.stock_for_sentiment:
                st.session_state.daily_stocks = [
                    s
                    for s in st.session_state.daily_stocks
                    if s not in st.session_state.added_stocks
                ]
                st.session_state.stock_for_sentiment = False
            elif st.session_state.stocks_for_training:
                st.session_state.training_stocks = [
                    s
                    for s in st.session_state.daily_stocks
                    if s not in st.session_state.added_stocks
                ]
                st.session_state.stocks_for_training = False

            # Clear found stocks after adding
            st.session_state.found_stocks = []
            st.session_state.added_stocks = []
            st.rerun()


# UI Layout
st.title("Daily Socks & Socks Training")

# Daily Socks Section
with st.container(border=True):
    st.markdown("### Stocks with Daily Socks Sentiment Analysis")

    with st_horizontal():
        for stock in st.session_state.daily_stocks:
            with st.container(border=True):
                st.markdown(f"**{stock}**")

    with st_horizontal():
        if st.button(
            "Add more Stocks", on_click=add_stock, key="add_stocks_for_sentiment"
        ):
            st.session_state.found_stocks = []
            st.session_state.added_stocks = []
            st.session_state.stock_for_training = False
            st.session_state.stock_for_sentiment = True

        if st.button(
            "Remove Stocks",
            on_click=remove_stock,
            key="remove_stocks_for_sentiment",
            type="primary",
        ):
            st.session_state.found_stocks = []
            st.session_state.added_stocks = []
            st.session_state.stock_for_training = False
            st.session_state.stock_for_sentiment = True

        st.button("Perform Quick Analysis", key="quick_analysis")

# Training Stocks Section
with st.container(border=True):
    st.markdown("### Train SocksAI for Future Prediction")

    with st_horizontal():
        for stock in st.session_state.training_stocks:
            with st.container(border=True):
                st.markdown(f"**{stock}**")

    with st_horizontal():
        if st.button(
            "Train more Stocks", on_click=add_stock, key="add_stocks_for_training"
        ):
            st.session_state.found_stocks = []
            st.session_state.added_stocks = []
            st.session_state.stock_for_sentiment = False
            st.session_state.stock_for_training = True

        if st.button(
            "Remove Stocks",
            on_click=remove_stock,
            key="remove_stocks_for_training",
            type="primary",
        ):
            st.session_state.found_stocks = []
            st.session_state.added_stocks = []
            st.session_state.stock_for_sentiment = False
            st.session_state.stock_for_training = True
