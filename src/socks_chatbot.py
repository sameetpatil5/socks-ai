import streamlit as st

# Page config
st.set_page_config(
    page_title="SocksAI",
    page_icon=":socks:",
    layout="centered",
    initial_sidebar_state="expanded",
)


st.title("SocksAI Chatbot")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display conversation history
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Talk to SocksAI"):

    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state["messages"].append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        response = st.session_state.scba.chat(prompt)
        full_response = st.write_stream(response)

    st.session_state["messages"].append({"role": "assistant", "content": full_response})
