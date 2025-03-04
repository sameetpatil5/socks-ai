# Streamlit Horizontal Component Documentation

## Overview

The `st_horizontal.py` file defines a custom Streamlit component that enables horizontal alignment of UI elements. It uses a combination of CSS styling and a context manager to modify Streamlit’s default vertical layout, allowing elements such as buttons to be displayed in a row.

## Libraries and Tools Used

The following libraries and tools are utilized in the project:

- **streamlit**: Web framework for building interactive UI components.
- **contextlib.contextmanager**: Used to create a context manager for horizontal alignment.

## Implementation

### Styling Configuration

A custom CSS block is defined to override Streamlit's default vertical stacking behavior:

```python
HORIZONTAL_STYLE = """
    <style class="hide-element">
        .element-container:has(.hide-element) {
            display: none;
        }
        div[data-testid="stVerticalBlock"]:has(> .element-container .horizontal-marker) {
            display: flex;
            flex-direction: row !important;
            flex-wrap: wrap;
            gap: 0.5rem;
            align-items: baseline;
        }
        div[data-testid="stVerticalBlock"]:has(> .element-container .horizontal-marker) div {
            width: max-content !important;
        }
    </style>
"""
```

### Context Manager: `st_horizontal()`

The `st_horizontal` function is a context manager that injects the CSS style and wraps elements within a horizontal container.

```python
@contextmanager
def st_horizontal():
    st.markdown(HORIZONTAL_STYLE, unsafe_allow_html=True)
    with st.container():
        st.markdown(
            '<span class="hide-element horizontal-marker"></span>',
            unsafe_allow_html=True,
        )
        yield
```

## Example Usage

### Display Buttons Horizontally

```python
import streamlit as st
from st_horizontal import st_horizontal

st.title("Horizontal Button Example")

with st_horizontal():
    st.button("Button 1")
    st.button("Button 2")
    st.button("Button 3")
```

### Display Input Fields in a Row

```python
with st_horizontal():
    st.text_input("First Name")
    st.text_input("Last Name")
    st.text_input("Email")
```

## Warnings

- This implementation relies on an internal Streamlit CSS selector, which may change in future versions of Streamlit.
- The component should be tested on different Streamlit versions to ensure compatibility.

## Conclusion

The `st_horizontal.py` component enhances the Streamlit UI by allowing horizontal alignment of elements, making layouts more visually appealing and functional.
