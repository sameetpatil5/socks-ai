import streamlit as st

st.title("SocksAI Chatbot")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display conversation history
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input("Talk to SocksAI"):
    # Add user message to session state
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Hardcoded AI response
    ai_response = "Message received"
    st.session_state["messages"].append({"role": "assistant", "content": ai_response})
    st.chat_message("assistant").write(ai_response)
