import streamlit as st
from modules.stock_chatbot_agent import StockChatbotAgent
import os

# Page config
st.set_page_config(
    page_title="SocksAI",
    page_icon=":socks:",
    layout="centered",
    initial_sidebar_state="expanded",
)

# if "scba" not in st.session_state:
#     st.session_state.scba = StockChatbotAgent(
#         storage_db_uri=os.environ.get("MONGO_URI"),
#         storage_db_name=os.environ.get("MONGO_DB"),
#         qdrant_url=os.environ.get("QDRANT_URL"),
#         api_key=os.environ.get("QDRANT_API_KEY"),
#         session_id="temp",
#         run_id="new",
#         user_id="user"
#     )

scba = StockChatbotAgent(
    storage_db_uri=os.environ.get("MONGO_URI"),
    storage_db_name=os.environ.get("MONGO_DB"),
    qdrant_url=os.environ.get("QDRANT_URL"),
    api_key=os.environ.get("QDRANT_API_KEY"),
    session_id="temp",
    run_id="new",
    user_id="user",
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
