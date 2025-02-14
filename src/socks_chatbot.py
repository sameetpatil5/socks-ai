import streamlit as st
import time

# Page config
st.set_page_config(
    page_title="SocksAI",
    page_icon=":socks:",
    layout="centered",
    initial_sidebar_state="expanded",
)


def limit_resources(seconds=10):
    st.session_state.chat_input_disabled = True
    time.sleep(seconds)
    st.session_state.chat_input_disabled = False

st.title("SocksAI Chatbot")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display conversation history
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Talk to SocksAI", placeholder="Talk to SocksAI...", disabled=st.session_state.get("chat_input_disabled", False)):

    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state["messages"].append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        response = st.session_state.scba.chat(prompt)
        full_response = st.write_stream(response)

    limit_resources()

    st.session_state["messages"].append({"role": "assistant", "content": full_response})
