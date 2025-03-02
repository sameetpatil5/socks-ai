import os
import logging
import colorlog
import requests
import datetime as dt
import streamlit as st
from dotenv import load_dotenv

from phi.model.google import Gemini
from phi.embedder.google import GeminiEmbedder

from pymongo import MongoClient
from pymongo.errors import InvalidURI
from qdrant_client import QdrantClient
from qdrant_client.http import exceptions as qdrant_exceptions

from streamlit_components.st_show_toast import show_toast
from streamlit_components.st_horizontal import st_horizontal

from modules.find_stock_agent import FindStockAgent
from modules.daily_stock_sentiment_agent import DailyStockSentimentAgent
from modules.stock_chart_agent import StockChartAgent
from modules.stock_chatbot_agent import StockChatbotAgent


load_dotenv()

# Configure logging
logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

formatter = colorlog.ColoredFormatter(
    "%(asctime)s - %(log_color)s%(levelname)-8s%(reset)s - "
    "%(module)s - %(funcName)s - \033[37m%(lineno)d%(reset)s: "
    "%(message_log_color)s%(message)s%(reset)s",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    },
    secondary_log_colors={
        "message": {
            "DEBUG": "cyan",
            "INFO": "light_green",
            "WARNING": "light_yellow",
            "ERROR": "light_red",
            "CRITICAL": "bold_red",
        },
    },
)

handler = logging.StreamHandler()
handler.setFormatter(formatter)

if not logger.hasHandlers():
    logger.addHandler(handler)


ENVIRONMENT_KEYS = {
    "gemini_api_key": "GOOGLE_API_KEY",
    "mongodb_cluster_url": "MONGO_URI",
    "qdrant_url": "QDRANT_URL",
    "qdrant_api_key": "QDRANT_API_KEY",
    "server_url": "SERVER_URL",
}

# App logo
st.logo("assests/socksai.png")

# App pages
pages = [
    st.Page("socks_home.py", title="Home"),
    st.Page("socks_chatbot.py", title="SocksAI Chatbot"),
    st.Page("socks_chart.py", title="Socks Chart"),
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

        div[data-testid="stDialog"] div[role="dialog"]:has(.big-dialog) {
            width: 80vw;
            /* height: 80vh; */
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize keys session state
for key, env_var in ENVIRONMENT_KEYS.items():
    try:
        if key not in st.session_state:
            st.session_state[key] = os.environ.get(env_var, "")
            environment_session_key = st.session_state[key]
            logger.info(
                f"Initializing Environment Key[{key}]: {' ' if environment_session_key == '' else ('...' + '***' + environment_session_key[-4:])}"
            )
    except KeyError:
        logger.critical(
            "File `.env` or variable `ENVIRONMENT_KEYS` was altered Environment Key mapping maynot work properly"
        )
    except Exception as e:
        logger.error(f"Error while initializing Keys: {e}")


# Function to mask API keys for logging
def mask_key(key, visible_chars=4):
    if not key:
        return "None"
    masked_key = str("..." + "***" + key[-visible_chars:])
    return masked_key


# Function to validate Gemini API Key
def validate_gemini_api_key(api_key):
    masked_key = mask_key(api_key)
    api_url = "https://generativelanguage.googleapis.com/v1/models"

    headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}

    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            logger.info(f"Gemini API Key validation successful: {masked_key}")
            show_toast(f"Gemini API Key validation successful: {masked_key}")
            return True
        else:
            logger.warning(f"Invalid Gemini API Key: {masked_key}")
            show_toast("⚠️ Invalid Gemini API Key")
            return False
    except Exception as e:
        logger.error(f"Gemini API Key validation error: {masked_key} - {str(e)}")
        return False


# Function to validate MongoDB URL
def validate_mongodb_url(cluster_url):
    masked_url = mask_key(cluster_url)
    try:
        client = MongoClient(cluster_url, serverSelectionTimeoutMS=3000)
        client.server_info()  # Test connection
        logger.info(f"MongoDB URL validation successful: {masked_url}")
        show_toast(f"MongoDB URL validation successful: {masked_url}")
        return True
    except InvalidURI:
        logger.warning(f"Invalid MongoDB Cluster URL: {masked_url}")
        show_toast("⚠️ Invalid MongoDB Cluster URL")
        return False
    except Exception as e:
        logger.error(f"MongoDB Connection Error: {masked_url} - {str(e)}")
        return False


# Function to validate Qdrant
def validate_qdrant_url(qdrant_url, api_key):
    masked_url = mask_key(qdrant_url)
    masked_key = mask_key(api_key)
    try:
        client = QdrantClient(url=qdrant_url, api_key=api_key)
        client.get_collections()  # Test connection
        logger.info(
            f"Qdrant validation successful: {masked_url} | API Key: {masked_key}"
        )
        show_toast(
            f"Qdrant validation successful: {masked_url} | API Key: {masked_key}"
        )
        return True
    except qdrant_exceptions.UnauthorizedException:
        logger.warning(f"Invalid Qdrant API Key: {masked_key}")
        show_toast("⚠️ Invalid Qdrant API Key")
        return False
    except qdrant_exceptions.ConnectionError:
        logger.warning(f"Invalid Qdrant URL: {masked_url}")
        show_toast("⚠️ Invalid Qdrant URL")
        return False
    except Exception as e:
        logger.error(
            f"Qdrant Connection Error: {masked_url} | API Key: {masked_key} - {str(e)}"
        )
        return False

# Function to validate Server URL
def validate_server_url(server_url):
    masked_url = mask_key(server_url)
    try:
        response = requests.get(f"{server_url}/")
        if response.status_code == 200 and response.json()["success"] == True:
            logger.info(f"Server URL validation successful: {masked_url}")
            show_toast(f"Server URL validation successful: {masked_url}")
            return True
        else:
            logger.warning(f"Invalid Server URL: {masked_url}")
            show_toast("⚠️ Invalid Server URL")
            return False
    except Exception as e:
        logger.error(f"Server Connection Error: {masked_url} - {str(e)}")
        return False

# Validation before storing the keys
def check_gemini_api_key():
    gemini_api_key = st.session_state.get("input_gemini_api_key", "")

    if validate_gemini_api_key(gemini_api_key):
        st.session_state["gemini_api_key"] = gemini_api_key
    else:
        st.sidebar.error("❌ Invalid Gemini API Key!")


def check_mongodb_cluster_url():
    mongodb_cluster_url = st.session_state.get("input_mongodb_cluster_url", "")

    if validate_mongodb_url(mongodb_cluster_url):
        st.session_state["mongodb_cluster_url"] = mongodb_cluster_url
    else:
        st.sidebar.error("❌ Invalid MongoDB Cluster URL!")


def check_qdrant_url_api_key():
    qdrant_url = st.session_state.get("input_qdrant_url", "")
    qdrant_api_key = st.session_state.get("input_qdrant_api_key", "")
    if validate_qdrant_url(qdrant_url, qdrant_api_key):
        st.session_state["qdrant_url"] = qdrant_url
        st.session_state["qdrant_api_key"] = qdrant_api_key
    else:
        st.sidebar.error("❌ Invalid Qdrant URL or API Key!")


def check_server_url():
    server_url = st.session_state.get("input_server_url", "")

    if validate_server_url(server_url):
        st.session_state["server_url"] = server_url
    else:
        st.sidebar.error("❌ Invalid Server URL!")

# Get the environment keys when running the app for the first time
@st.dialog("Enter Environment Keys")
def add_env_keys():

    st.write("API Keys are required to make the app work at your end rather than mine.")
    st.write("You can add these keys in the `.env` file when hosting locally or in the UI sidebar.")
    st.write("Please add your environment keys to access the SocksAI platform.")

    with st.form("env_keys_form"):
        form_gemini_api_key = st.text_input(
            "Gemini API Key",
            type="password",
            value=st.session_state.get("gemini_api_key", ""),
        )
        form_mongodb_cluster_url = st.text_input(
            "MongoDB Cluster URL",
            type="password",
            value=st.session_state.get("mongodb_cluster_url", ""),
            help="Format: mongodb+srv://<username>:<password>@<database>/?retryWrites=true&w=majority&appName=<app-name>",
        )
        form_qdrant_url = st.text_input(
            "Qdrant URL", type="password", value=st.session_state.get("qdrant_url", "")
        )
        form_qdrant_api_key = st.text_input(
            "Qdrant API Key",
            type="password",
            value=st.session_state.get("qdrant_api_key", ""),
        )
        form_server_url = st.text_input(
            "Server URL", type="password", value=st.session_state.get("server_url", "")
        )

        confirm = st.form_submit_button("Confirm", icon="✔️")

        if confirm:
            is_validated = (
                validate_gemini_api_key(form_gemini_api_key)
                and validate_mongodb_url(form_mongodb_cluster_url)
                and validate_qdrant_url(form_qdrant_url, form_qdrant_api_key)
                and validate_server_url(form_server_url)
            )

            if is_validated:
                st.session_state["gemini_api_key"] = form_gemini_api_key
                st.session_state["mongodb_cluster_url"] = form_mongodb_cluster_url
                st.session_state["qdrant_url"] = form_qdrant_url
                st.session_state["qdrant_api_key"] = form_qdrant_api_key
                st.session_state["server_url"] = form_server_url
                st.session_state["keys_provided"] = True
                show_toast("Environment Keys successfully loaded")
                st.rerun()
            else:
                st.error("Invalid keys provided. Please try again.")


# Function to get persistent values
def get_persistent_value(key, default=""):
    if key not in st.session_state:
        st.session_state[key] = default
    return st.session_state[key]


# Function to clear environment keys
def clear_environment_keys():
    for key in ENVIRONMENT_KEYS.keys():
        st.session_state[key] = ""


# Function to clear environment agents
def clear_environment_agents():
    for agent in ["fsa", "dssa", "sca", "scba"]:
        del st.session_state[agent]

    for data in ["daily_stocks", "chatbot_interactions"]:
        del st.session_state[data]

    show_toast("Cleared Environment Agents!")


# Function to clear the entire environment
def clear_environment():
    clear_environment_keys()
    clear_environment_agents()

    del st.session_state["keys_provided"]

    logger.info("Environment cleared.")
    show_toast("Cleared the Environment!")
    add_env_keys()


# Sidebar Header
st.sidebar.header("Environment Keys")

# Input fields for API keys with password masking
gemini_api_key = st.sidebar.text_input(
    "Gemini API Key",
    value=get_persistent_value("gemini_api_key"),
    type="password",
    on_change=check_gemini_api_key,
    key="input_gemini_api_key",
)
mongodb_cluster_url = st.sidebar.text_input(
    "MongoDB Cluster URL",
    value=get_persistent_value("mongodb_cluster_url"),
    type="password",
    help="Make sure to add your IP address to MongoDB's IP whitelist.",
    on_change=check_mongodb_cluster_url,
    key="input_mongodb_cluster_url",
)
qdrant_url = st.sidebar.text_input(
    "Qdrant URL",
    value=get_persistent_value("qdrant_url"),
    type="password",
    on_change=check_qdrant_url_api_key,
    key="input_qdrant_url",
)
qdrant_api_key = st.sidebar.text_input(
    "Qdrant API Key",
    value=get_persistent_value("qdrant_api_key"),
    type="password",
    on_change=check_qdrant_url_api_key,
    key="input_qdrant_api_key",
)
server_url = st.sidebar.text_input(
    "Server URL",
    value=get_persistent_value("server_url"),
    type="password",
    on_change=check_server_url,
    key="input_server_url",
)

st.sidebar.write(
    "🔒 Your keys are stored securely in the session and won't be shared or logged."
)

with st_horizontal():
    if st.sidebar.button(
        "Clear Environment",
        icon="🚮",
        help="Clears all the environment keys and Agent history.\n\n  Use when you want to load a session with new environment",
    ):
        clear_environment()
        st.switch_page("socks_home.py")
    if st.sidebar.button(
        "Load Environment",
        icon="🔑",
        help="Loads/reloads the environment with the keys entered in the sidebar.\n\n  Use when you have changed any of the environment keys.",
    ):
        clear_environment_agents()
        st.switch_page("socks_home.py")

st.sidebar.divider()

if not st.session_state.get("keys_provided", False):
    provided_keys = [st.session_state[key] for key in ENVIRONMENT_KEYS.keys()]

    if any(key == "" for key in provided_keys):
        add_env_keys()
    else:
        st.session_state["keys_provided"] = True
        st.rerun()
else:
    # Initialize Agents in session state
    if (
        "fsa" not in st.session_state 
        or "dssa" not in st.session_state 
        or "sca" not in st.session_state 
        or "scba" not in st.session_state
    ):
        logger.info("Agents Loaded")
    if "fsa" not in st.session_state:
        st.session_state.fsa = FindStockAgent(model=Gemini())

    if "dssa" not in st.session_state:
        st.session_state.dssa = DailyStockSentimentAgent(
            db_uri=st.session_state["mongodb_cluster_url"],
            model=Gemini(),
        )

    if "sca" not in st.session_state:
        st.session_state.sca = StockChartAgent(model=Gemini())

    if "scba" not in st.session_state:
        st.session_state.scba = StockChatbotAgent(
            storage_db_uri=st.session_state["mongodb_cluster_url"],
            qdrant_url=st.session_state["qdrant_url"],
            api_key=st.session_state["qdrant_api_key"],
            session_id="",
            run_id="",
            user_id="",
            model=Gemini(),
            embedder=GeminiEmbedder(),
        )

    # Initialize Agent Data in session state
    if (
        "daily_stocks" not in st.session_state
        or "chatbot_interactions" not in st.session_state
    ):
        logger.info("Agent Data Loaded")

    if "daily_stocks" not in st.session_state:
        st.session_state.daily_stocks = st.session_state.dssa.stocks

    if "chatbot_interactions" not in st.session_state:
        st.session_state.chatbot_interactions = []

    # Helper Data
    if (
        "found_stocks" not in st.session_state
        or "added_stocks" not in st.session_state
        or "scheduler_state" not in st.session_state
    ):
        logger.info("Helper Data Loaded")

    if "found_stocks" not in st.session_state:
        st.session_state.found_stocks = []

    if "added_stocks" not in st.session_state:
        st.session_state.added_stocks = []

    if "scheduler_state" not in st.session_state:
        st.session_state.scheduler_state = 0


# Helper Functions
if "show_toast" not in st.session_state:
    st.session_state.show_toast = False

if "toast_message" not in st.session_state:
    st.session_state.toast_message = ""

if st.session_state.show_toast:
    st.toast(st.session_state.toast_message)
    st.session_state.show_toast = False
    st.session_state.toast_message = ""

if "app_loaded" not in st.session_state:
    st.session_state.app_loaded = True
    show_toast("🎉 SocksAI is setup successfully!")
    logger.info("App loaded")
