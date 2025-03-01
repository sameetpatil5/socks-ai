import streamlit as st


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

