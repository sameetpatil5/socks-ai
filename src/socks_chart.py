import streamlit as st

with st.container(border=True):
    st.markdown("### Stock & Indicators Selection")
    st.markdown("Select Views Prediction / Current Position")

    st.divider()

    # Stocks Graph and Sentiment Analysis
    st.markdown("### Stocks Graph with Indicators & Predictions")
    st.button("Refresh", icon="🔄️")
