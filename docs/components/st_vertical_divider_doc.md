# Streamlit Vertical Divider Documentation

## Overview

The `st_vertical_divider.py` file defines a custom Streamlit component for adding vertical dividers to the UI. This is useful for visually separating content in a Streamlit application.

## Libraries and Tools Used

The following libraries and tools are utilized in the project:

- **streamlit**: Web framework for building interactive UI components.

## Function: `st_vertical_divider()`

### Description

Creates a vertical line divider using custom CSS and renders it inside a Streamlit application.

### Arguments

- `height` (`int`): The height of the vertical divider in pixels.

### Implementation

```python
def st_vertical_divider(height: int):
    vertical_divider = f"""
        <div class="divider-vertical-line"></div>
        <style>
            .divider-vertical-line {{
                border-left: 2px solid rgba(60,62,68,255);
                height: {height}px;
                margin: auto;
            }}
        </style>
    """
    st.markdown(vertical_divider, unsafe_allow_html=True)
```

## Example Usage

### Adding a Vertical Divider

```python
import streamlit as st
from st_vertical_divider import st_vertical_divider

st.write("Content on the left")
st_vertical_divider(height=200)
st.write("Content on the right")
```

## Notes

- The divider is implemented using HTML and CSS inside a `st.markdown()` block.
- The height of the divider can be adjusted dynamically by passing an integer value.
- The divider is centered and styled with a solid border.

## Conclusion

The `st_vertical_divider.py` component enhances Streamlit UI layouts by providing a simple way to visually separate sections with vertical lines.
