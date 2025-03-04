import streamlit as st


WIDE_DIALOG = """
    <style>
        div[data-testid="stDialog"] div[role="dialog"]:has(.big-dialog) {
            width: 80vw;
            /* height: 80vh; */
        }
    </style>
    <div class="big-dialog"></div>
    """

def st_wide_dialog():
    st.markdown(
        WIDE_DIALOG,
        unsafe_allow_html=True,
    )
