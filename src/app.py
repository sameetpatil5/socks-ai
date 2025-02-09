import streamlit as st
import logging
from dotenv import load_dotenv
import requests
from pymongo import MongoClient
from qdrant_client import QdrantClient
from qdrant_client.http import exceptions as qdrant_exceptions
from pymongo.errors import InvalidURI

load_dotenv()

# Configure Logging
logging.basicConfig(
    # filename="socksai.log",  # Log file name
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Page config
st.set_page_config(
    page_title="SocksAI",
    page_icon=":socks:",
    layout="wide",
    # initial_sidebar_state="collapsed",
)

st.logo("assests/socksai.png")

pages = [
    st.Page("socks_home.py", title="Home"),
    st.Page("socksai_chatbot.py", title="SocksAI Chatbot"),
    st.Page("socks_chart.py", title="Charts & Indicators"),
    st.Page("daily_socks.py", title="Daily Socks"),
]

pg = st.navigation(pages)
pg.run()


# Custom Styling
st.markdown(
    """
    <style>
        /* Remove blank space at top and bottom */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        .st-emotion-cache-janbn0 {
            flex-direction: row-reverse;
            text-align: right;
        }

        .st-emotion-cache-1dnm2d2 .es2srfl5 {
            display: none;
        }

        [data-testid='stFileUploader'] {
            display: none 
            width: min-content;
        }
        [data-testid='stFileUploader'] section {
            padding: 0;
            float: left;
        }
        [data-testid='stFileUploader'] section > input + div {
            display: none;
        }
        [data-testid='stFileUploader'] section + div {
            float: right;
            padding-top: 0;
        }
        div[data-testid="stDialog"] div[role="dialog"]:has(.big-dialog) {
            width: 80vw;
            /* height: 80vh; */
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# Sidebar Header
st.sidebar.header("Environment Keys")

# Initialize session state keys
for key in ["gemini_api_key", "mongodb_cluster_url", "qdrant_url", "qdrant_api_key"]:
    if key not in st.session_state:
        st.session_state[key] = ""


# Function to mask API keys for logging
def mask_key(key, visible_chars=4):
    if not key:
        return "None"
    return key[:visible_chars] + "*" * (len(key) - visible_chars)


# Function to clear environment keys
def clear_environment_keys():
    for key in st.session_state.keys():
        st.session_state[key] = ""
    logging.info("Environment keys cleared.")


# Function to get persistent values
def get_persistent_value(key, default=""):
    if key not in st.session_state:
        st.session_state[key] = default
    return st.session_state[key]


# Function to validate Gemini API Key
def validate_gemini_api_key(api_key):
    masked_key = mask_key(api_key)
    api_url = "https://generativelanguage.googleapis.com/v1/models"

    headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}

    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            logging.info(f"Gemini API Key validation successful: {masked_key}")
            return True
        else:
            logging.warning(f"Invalid Gemini API Key: {masked_key}")
            st.toast("Invalid Gemini API Key")
            return False
    except Exception as e:
        logging.error(f"Gemini API Key validation error: {masked_key} - {str(e)}")
        st.sidebar.warning(f"Gemini API Key Error: {str(e)}")
        return False


# Function to validate MongoDB URL
def validate_mongodb_url(cluster_url):
    masked_url = mask_key(cluster_url)
    try:
        client = MongoClient(cluster_url, serverSelectionTimeoutMS=3000)
        client.server_info()  # Test connection
        logging.info(f"MongoDB URL validation successful: {masked_url}")
        return True
    except InvalidURI:
        logging.warning(f"Invalid MongoDB Cluster URL: {masked_url}")
        st.toast("Invalid MongoDB Cluster URL")
        return False
    except Exception as e:
        logging.error(f"MongoDB Connection Error: {masked_url} - {str(e)}")
        st.sidebar.warning(f"MongoDB Error: {str(e)}")
        return False


# Function to validate Qdrant
def validate_qdrant_url(qdrant_url, api_key):
    masked_url = mask_key(qdrant_url)
    masked_key = mask_key(api_key)
    try:
        client = QdrantClient(url=qdrant_url, api_key=api_key)
        client.get_collections()  # Test connection
        logging.info(
            f"Qdrant validation successful: {masked_url} | API Key: {masked_key}"
        )
        return True
    except qdrant_exceptions.UnauthorizedException:
        logging.warning(f"Invalid Qdrant API Key: {masked_key}")
        st.toast("Invalid Qdrant API Key")
        return False
    except qdrant_exceptions.ConnectionError:
        logging.warning(f"Invalid Qdrant URL: {masked_url}")
        st.toast("Invalid Qdrant URL")
        return False
    except Exception as e:
        logging.error(
            f"Qdrant Connection Error: {masked_url} | API Key: {masked_key} - {str(e)}"
        )
        st.sidebar.warning(f"Qdrant API Key Error: {str(e)}")
        return False


# Input fields for API keys with password masking
gemini_api_key = st.sidebar.text_input(
    "Gemini API Key", value=get_persistent_value("gemini_api_key"), type="password"
)
mongodb_cluster_url = st.sidebar.text_input(
    "MongoDB Cluster URL",
    value=get_persistent_value("mongodb_cluster_url"),
    type="password",
    help="Make sure to add your IP address to MongoDB's IP whitelist.",
)
qdrant_url = st.sidebar.text_input(
    "Qdrant URL", value=get_persistent_value("qdrant_url"), type="password"
)
qdrant_api_key = st.sidebar.text_input(
    "Qdrant API Key", value=get_persistent_value("qdrant_api_key"), type="password"
)

# Validation before storing the keys
if gemini_api_key:
    if validate_gemini_api_key(gemini_api_key):
        st.session_state["gemini_api_key"] = gemini_api_key
    else:
        st.sidebar.error("❌ Invalid Gemini API Key!")

if mongodb_cluster_url:
    if validate_mongodb_url(mongodb_cluster_url):
        st.session_state["mongodb_cluster_url"] = mongodb_cluster_url
    else:
        st.sidebar.error("❌ Invalid MongoDB Cluster URL!")

if qdrant_api_key and qdrant_url:
    if validate_qdrant_url(qdrant_url, qdrant_api_key):
        st.session_state["qdrant_url"] = qdrant_url
        st.session_state["qdrant_api_key"] = qdrant_api_key
    else:
        st.sidebar.error("❌ Invalid Qdrant URL or API Key!")

st.sidebar.write(
    "🔒 Your keys are stored securely in the session and won't be shared or logged."
)

st.sidebar.button("Clear Keys", on_click=clear_environment_keys)
st.sidebar.divider()
