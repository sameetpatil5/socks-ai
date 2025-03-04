# Streamlit Wide Dialog Documentation

## Overview

The `st_wide_dialog.py` file defines a custom Streamlit component for making dialogs wider. It modifies the default Streamlit dialog width using CSS.

## Libraries and Tools Used

The following libraries and tools are utilized in the project:

- **streamlit**: Web framework for building interactive UI components.

## Styling Configuration

A CSS block is defined to override the default Streamlit dialog width:

```python
WIDE_DIALOG = """
    <style>
        div[data-testid="stDialog"] div[role="dialog"]:has(.big-dialog) {
            width: 80vw;
        }
    </style>
    <div class="big-dialog"></div>
"""
```

## Function: `st_wide_dialog()`

### Description

Injects the custom CSS to modify the dialog width.

### Implementation

```python
def st_wide_dialog():
    st.markdown(WIDE_DIALOG, unsafe_allow_html=True)
```

## Example Usage

### Expanding a Dialog Width

```python
import streamlit as st
from st_wide_dialog import st_wide_dialog

st.button("Open Dialog")
st_wide_dialog()
```

## Notes

- The dialog width is set to `80vw` (80% of the viewport width).
- The CSS uses the `data-testid="stDialog"` selector, which may change in future Streamlit versions.

## Conclusion

The `st_wide_dialog.py` component enhances Streamlit dialogs by making them wider, improving usability for large content display.
