import streamlit as st

st.title("SocksAI Home")

navigation, details = st.columns([1, 2])

with navigation.container(border=True):
    st.subheader("Navigation")
    st.page_link("socks_home.py", label="Socks Home", icon="🏠")
    st.page_link("socksai_chatbot.py", label="SocksAI Chatbot", icon="🤖")
    st.page_link("socks_chart.py", label="Socks Chart", icon="📈")
    st.page_link("daily_socks.py", label="Daily Socks", icon="📊")

with navigation.container(border=True):
    st.subheader("Other Links")
    st.link_button("Support", "")


with details.container(border=True):
    about, how_to, privacy = st.tabs(["About SocksAI", "How to Use", "Privicy Note"])
    with about:
        st.subheader("About SocksAI")
        st.markdown("its my worst day")
    with how_to:
        st.subheader("How to Use")
        st.markdown("its my worst day")
    with privacy:
        st.subheader("Privacy Note")
        st.markdown("its my worst day")
