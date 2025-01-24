import streamlit as st
from modules.find_stock_agent import FindStockAgent

from contextlib import contextmanager

if "daily_stocks" not in st.session_state:
    st.session_state.daily_stocks = ["SAM", "MAAAAAS"]

if "training_stocks" not in st.session_state:
    st.session_state.training_stocks = ["SAM", "MAS"]

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
        st.markdown('<span class="hide-element horizontal-marker"></span>', unsafe_allow_html=True)
        yield

@st.dialog("Add Stock")
def add_stock():
    query = st.text_input("Enter a stock symbol or query:")

    if st.button("Add"):
        print(query)
        find_stock_agent = FindStockAgent()
        if st.session_state.add_stock_for_sentiment:
            st.session_state.add_stock_for_sentiment = False
            test_stock = find_stock_agent.add_stock(query)
            print(test_stock[0])
            st.session_state.daily_stocks.extend(test_stock)
            print(st.session_state.daily_stocks)
            print("added for sentiments")
            # st.session_state.daily_stocks.append(find_stock_agent.get_stock())
        if st.session_state.add_stocks_for_training:
            st.session_state.add_stocks_for_training = False
            print("from training")
            # st.session_state.training_stocks.append(find_stock_agent.get_stock())
        # st.session_state.stocks.append(find_stock_agent.get_stock())
        st.rerun()


st.title("Daily Socks & Socks Training")

with st.container(border=True):
    st.markdown("### Stocks with Daily Socks Sentiment Analysis")

    # List of stocks
    daily_socks = st.session_state.daily_stocks

    with st_horizontal():
        for stock in daily_socks:
            with st.container(border=True):
                # st.markdown(
                #     f"<div style='display: flex; justify-content: center; align-items: center; text-align: center;'><strong>{stock}</strong></div>",
                #     unsafe_allow_html=True,
                # )
                st.markdown(f"**{stock}**")

    with st_horizontal():

        if st.button(
            "Add more Stocks",
            on_click=add_stock,
            key="add_stocks_for_sentiment",
            # type="primary",
        ):
            st.session_state.add_stock_for_sentiment = True

        st.button("Remove Stocks")
        st.button("Perform Quick Analysis")

with st.container(border=True):

    # List of stocks
    training_stocks = st.session_state.training_stocks

    st.markdown("### Train SocksAI for Future Prediction")
    max_columns = min(len(training_stocks), 10)
    for i in range(0, len(training_stocks), max_columns):
        cols = st.columns(max_columns)
        for col, stock in zip(cols, training_stocks[i : i + max_columns]):
            with col:
                with st.container(border=True):
                    st.markdown(
                        f"<div style='display: flex; justify-content: center; align-items: center; text-align: center;'>{stock}</div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown("")

    if st.button(
        "Add more Stocks",
        on_click=add_stock,
        key="add_stocks_for_training",
        type="primary",
    ):
        st.session_state.add_stocks_for_training = True
