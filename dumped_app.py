import streamlit as st

st.set_page_config(
    page_title="SocksAI",
    page_icon=":socks:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Dashboard Styling
st.markdown(
    """
    <style>
        /* Remove blank space at top and bottom */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 0rem;
        }

        /* Remove app horizontal padding */
        .st-emotion-cache-1ibsh2c {
            padding-left: 1.25rem;
            padding-right: 0.9rem;
        }

        /* Adjust sidebar horizontal padding */
        .st-emotion-cache-a6qe2i {
            padding: 0px 1.2rem 0px 1.2rem;
        }

        /* Remove sidebar top space */
        .st-emotion-cache-kgpedg {
            padding: 1.35rem 1.5rem 1.25rem;
        }

        /* Remove sidebar title top padding */
        .st-emotion-cache-1espb9k h1 {
            padding: 0rem 0px 1rem;
        }

        /* Remove title bottom padding */
        .st-emotion-cache-1cvow4s h1 {
            padding: 1.25rem 0px 0rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Socks AI Dashboard", anchor=False)

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state["messages"] = []


st.sidebar.title("SocksAI Options")
with st.sidebar:
    with st.container(height=645, border=True):
        st.markdown("### Show Stocks Trained/Training for Future Prediction")
        st.markdown("Show Stocks for Day-based Sentiment Analysis")

col1, col2 = st.columns([1, 2])

with col1:
    with st.container(height=645, border=True):
        st.markdown("### SocksAI Chatbot")

        # Display conversation history
        for message in st.session_state["messages"]:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        with st.container():
            # messages = st.container(height=500, border=False)
            messages = st.container(border=False)

            if prompt := st.chat_input("Talk to SocksAI"):
                # Add user message to session state
                st.session_state["messages"].append({"role": "user", "content": prompt})
                messages.chat_message("user").write(prompt)

                # Hardcoded AI response
                ai_response = "Message received"
                st.session_state["messages"].append(
                    {"role": "assistant", "content": ai_response}
                )
                messages.chat_message("assistant").write(ai_response)

with col2:
    with st.container(height=645, border=True):
        st.markdown("### Stock & Indicators Selection")
        st.markdown("Select Views Prediction / Current Position")

        st.divider()

        # Stocks Graph and Sentiment Analysis
        st.markdown("### Stocks Graph with Indicators & Predictions")
        st.button("Refresh", icon="🔄️")
