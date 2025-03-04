# Streamlit Toast Notification Documentation

## Overview

The `st_show_toast.py` file defines a utility function for displaying toast notifications in a Streamlit application. It provides a way to show temporary messages that inform users of actions or events.

## Libraries and Tools Used

The following libraries and tools are utilized in the project:

- **streamlit**: Web framework for building interactive UI components.

## Function: `show_toast()`

### Description

Displays a toast notification in the Streamlit application by updating the session state.

### Arguments

- `message` (`str`): The message to be displayed as a toast notification.

### Implementation

```python
def show_toast(message: str) -> None:
    """
    Displays a toast message on the Streamlit application.

    Args:
        message (str): The message to be displayed as a toast notification.
    """
    st.session_state.show_toast = True
    st.session_state.toast_message = message
```

## Example Usage

### Displaying a Toast Message

```python
import streamlit as st
from st_show_toast import show_toast

if st.button("Click Me"):
    show_toast("Button Clicked!")
```

## Notes

- The toast message is stored in `st.session_state`, making it accessible across different components of the Streamlit app.
- Additional logic may be needed to handle toast message display timing and dismissal.

## Conclusion

The `st_show_toast.py` utility simplifies toast notifications in Streamlit, improving user feedback for interactive applications.
