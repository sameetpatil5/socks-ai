# SocksAI Streamlit App Documentation

## Overview

The `app.py` file is the main entry point for the `SocksAI` Streamlit application. It provides an interactive dashboard for stock analysis, sentiment tracking, chart visualization, and AI-powered chatbot functionality. The app integrates multiple AI agents and external APIs to deliver real-time stock insights and market analysis.

## Libraries and Tools Used

The following libraries and tools are utilized in the project:

- **streamlit**: Web framework for building the UI.
- **logging & colorlog**: For logging system activity with color-coded messages.
- **requests**: For making API calls to validate keys and fetch external data.
- **dotenv**: For loading environment variables securely.
- **pymongo**: For MongoDB interactions to store stock data and chatbot memory.
- **qdrant_client**: For managing vector embeddings using Qdrant.
- **phi.model.google.Gemini**: AI model for analysis and chatbot interactions.
- **streamlit_components**: Custom Streamlit components for UI enhancements.

## Configuration

### Environment Variables

The application loads essential API keys and database URLs from environment variables:

```python
ENVIRONMENT_KEYS = {
    "gemini_api_key": "GOOGLE_API_KEY",
    "mongodb_cluster_url": "MONGO_URI",
    "qdrant_url": "QDRANT_URL",
    "qdrant_api_key": "QDRANT_API_KEY",
    "server_url": "SERVER_URL",
}
```

### Logging Setup

A color-coded logging system is configured using `colorlog`:

```python
formatter = colorlog.ColoredFormatter(
    "%(asctime)s - %(log_color)s%(levelname)-8s%(reset)s - %(message)s",
    log_colors={
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    },
)
```

## UI Structure

### Navigation and Pages

The application consists of multiple pages:

- **Home** (`socks_home.py`): Dashboard overview.
- **Chatbot** (`socks_chatbot.py`): AI-powered stock chatbot.
- **Charts** (`socks_chart.py`): Stock price visualization.
- **Daily Stocks** (`daily_socks.py`): Daily stock sentiment analysis.

Navigation is handled using `st.navigation()`:

```python
pages = [
    st.Page("socks_home.py", title="Home"),
    st.Page("socks_chatbot.py", title="SocksAI Chatbot"),
    st.Page("socks_chart.py", title="Socks Chart"),
    st.Page("daily_socks.py", title="Daily Socks"),
]
pg = st.navigation(pages)
pg.run()
```

### Sidebar Configuration

The sidebar allows users to input API keys and environment settings dynamically.

- **Gemini API Key**: Used for AI-driven insights.
- **MongoDB URL**: Stores stock and chatbot data.
- **Qdrant URL & API Key**: Manages vector embeddings.
- **Server URL**: Optional, required for daily stock scheduling.

Users can clear and reload the environment dynamically from the sidebar.

## Agent Initialization

The application initializes AI agents for stock analysis:

```python
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
```

## API Key Validation

The application validates API keys before storing them in session state:

```python
def validate_gemini_api_key(api_key):
    api_url = "https://generativelanguage.googleapis.com/v1/models"
    headers = {"x-goog-api-key": api_key}
    response = requests.get(api_url, headers=headers)
    return response.status_code == 200
```

Similar validation is done for MongoDB, Qdrant, and the server URL.

## Example Usage

### Running the App

To launch the Streamlit app, run the following command:

```bash
streamlit run app.py
```

### Setting Environment Keys

Users must input API keys in the sidebar or `.env` file:

```ini
GOOGLE_API_KEY=your-gemini-api-key
MONGO_URI=your-mongodb-uri
QDRANT_URL=your-qdrant-url
QDRANT_API_KEY=your-qdrant-api-key
SERVER_URL=your-server-url
```

## Conclusion

The `SocksAI` Streamlit app provides a seamless interface for stock market analysis, integrating AI-driven sentiment tracking, charting tools, and chatbot functionalities. Its modular design allows users to customize and expand stock-tracking capabilities dynamically.
