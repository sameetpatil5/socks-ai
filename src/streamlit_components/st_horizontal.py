from contextlib import contextmanager

import streamlit as st


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
    """
    A context manager that allows you to horizontally align Streamlit elements.

    Examples
    --------
    >>> with st_horizontal():
    ...     st.button("Button 1")
    ...     st.button("Button 2")
    ...     st.button("Button 3")

    This will display three buttons horizontally aligned, next to each other.

    Warning
    -------
    This function uses an implementation detail of Streamlit, and may break in future versions.
    Use at your own risk!

    Style
    -----
    The horizontal alignment is achieved by adding a custom CSS style to the Streamlit app.
    The style is defined in the `HORIZONTAL_STYLE` variable above. If you want to override
    the default style, you can define your own CSS in a `<style>` block and add it to your
    Streamlit app before calling `st_horizontal()`.
    """
    st.markdown(HORIZONTAL_STYLE, unsafe_allow_html=True)
    with st.container():
        st.markdown(
            '<span class="hide-element horizontal-marker"></span>',
            unsafe_allow_html=True,
        )
        yield
