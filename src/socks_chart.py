import streamlit as st
from contextlib import contextmanager

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


st.title("Socks Chart")

with st.container(border=True):
    st.markdown("### Stock & Indicators Selection")
    options, indicators, predictors = st.columns(3)
    with options:
        st.write("Select Views Prediction / Current Position")
        with st_horizontal():
            st.button("demo 1")
            st.button("demo 2")
            st.button("demo 3")
    with indicators:
        with st_horizontal():
            st.button("demo 4")
            st.button("demo 5")
            st.button("demo 6")
    with predictors:
        st.selectbox("select", options=["hi", "bye"])

    # Stocks Graph and Sentiment Analysis
    st.markdown("### Stocks Graph with Indicators & Predictions")
    st.area_chart()
    with st_horizontal():
        st.button("Plot", icon="📈")
        st.button("Apply", icon="✅")
        st.button("Refresh", icon="🔄️")
