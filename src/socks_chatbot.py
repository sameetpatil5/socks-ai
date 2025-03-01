import logging
from pathlib import Path
from urllib.parse import urlparse

import streamlit as st

from streamlit_components.st_show_toast import show_toast

# Configure logging
logger = logging.getLogger("app")


# Page config
st.set_page_config(
    page_title="SocksAI",
    page_icon=":socks:",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Display User Icon on the right (Pre loaded while streaming)
st.markdown(
    """
    <style>
        .st-emotion-cache-janbn0 {
            flex-direction: row-reverse;
            text-align: right;
        }

        .st-emotion-cache-1dnm2d2 .es2srfl5 {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

def is_valid_url(url: str) -> bool:
    """
    Checks if a given URL is valid.

    Args:
        url (str): URL to validate

    Returns:
        bool: True if the URL is valid, False otherwise

    Raises:
        ValueError: If the URL is invalid
    """
    try:
        result = urlparse(url)
        response = all([result.scheme, result.netloc])
        logger.info(f"{url[:10] + "..."} response generated: {response}")
        return response
    except ValueError:
        logger.info("URL may be incorrect. Check Url or try again")
        return False


@st.dialog("Add Knowledge", width="large")
def add_knowledge():
    """
    Adds a document to the chatbot's knowledge base.

    Args:
        None

    Returns:
        None

    Raises:
        ValueError: If the URL is invalid

    """
    KNOWLEDGE_TYPE = {
        "Website": "website",
        "PDF URL": "pdf_url",
        "Local PDF": "local_pdf",
    }
    knowledge_type = st.selectbox(
        "Select Knowledge Type",
        ["Website", "PDF URL", "Local PDF"],
        key="knowledge_type",
    )

    if KNOWLEDGE_TYPE[knowledge_type] == "website" or KNOWLEDGE_TYPE[knowledge_type] == "pdf_url":
        knowledge_url = st.text_input(
            "Enter the URL of the knowledge document",
            key="knowledge_url",
        )

        if st.button("Add", key="add_url_knowledge_button") and is_valid_url(knowledge_url):
            st.session_state.scba.add_knowledge(knowledge_url, KNOWLEDGE_TYPE[knowledge_type])
            logger.info(f"Knowledge added for {knowledge_type}")
            show_toast("✅ Knowledge added successfully!")
            st.rerun()
        if knowledge_url and not is_valid_url(knowledge_url):
            logger.error(f"URL is not valid: {knowledge_url}")
            st.error("URL invalid, please try again!", icon="⚠️")

    elif KNOWLEDGE_TYPE[knowledge_type] == "local_pdf":
        st.warning("Adding PDF document here will store them on the server temporarily. Use PDF links instead.", icon="🚨")
        knowledge_file = st.file_uploader(
            "Upload a PDF file",
            type=["pdf"],
            key="knowledge_pdf_uploader_key",
        )

        try:
            knowledge_data_dir = Path("data/knowledge_pdfs")
            knowledge_data_dir.mkdir(parents=True, exist_ok=True) 

            if knowledge_file:
                knowledge_file_path = knowledge_data_dir / knowledge_file.name

                with open(knowledge_file_path, mode="wb") as pdf:
                    pdf.write(knowledge_file.getbuffer())

                if knowledge_file_path.exists():
                    st.success(
                        f"File {knowledge_file.name} is successfully saved!", icon="✅"
                    )
                    logger.info("PDF document loaded locally")
        except Exception as e:
            logger.error(f"Error while saving PDF file document locally: {e}")

        if st.button("Add", key="add_local_pdf_knowledge_button") and knowledge_file is not None and knowledge_file_path is not None:
            st.session_state.scba.add_knowledge(
                knowledge_file_path, KNOWLEDGE_TYPE[knowledge_type]
            )
            logger.info(f"Knowledge added for {knowledge_type}")
            show_toast("✅ Knowledge added successfully")
            st.rerun()
        if knowledge_file is not None and knowledge_file_path is None:
            logger.error("Failed to load knowledge from local PDF")
            st.error("Failed to upload file, please try again!", icon="⚠️")

st.title("SocksAI Chatbot")

# Display conversation history
for message in st.session_state["chatbot_interactions"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input(placeholder="Talk to SocksAI...", disabled=st.session_state.get("chat_input_disabled", False)):

    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state["chatbot_interactions"].append({"role": "user", "content": prompt})

    with st.spinner("Thinking..."):
        with st.chat_message("assistant"):
            response = st.session_state.scba.chat(prompt)
            full_response = st.write_stream(response)

    st.session_state["chatbot_interactions"].append({"role": "assistant", "content": full_response})


st.button("Add Knowledge", on_click=add_knowledge, key="add_knowledge")
