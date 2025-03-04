# SocksAI Home Page Documentation

## Overview

The `socks_home.py` file is the main home page for the `SocksAI` Streamlit application. It provides an entry point for users to navigate different features of the app, such as chatbot interactions, stock charts, and daily stock sentiment analysis. Additionally, it contains important information about the project, usage instructions, and privacy policies.

## Libraries and Tools Used

The following libraries and tools are utilized in the project:

- **streamlit**: Web framework for building the UI.
- **logging**: For tracking user interactions and debugging.

## Page Configuration

The home page is configured with a wide layout and a collapsed sidebar:

```python
st.set_page_config(
    page_title="SocksAI",
    page_icon=":socks:",
    layout="wide",
    initial_sidebar_state="collapsed",
)
```

## Workflow

### 1. Navigation Panel

Users can navigate to different sections of the app using the page links:

```python
st.subheader("Navigation")
st.page_link("socks_home.py", label="Socks Home", icon="🏠")
st.page_link("socks_chatbot.py", label="SocksAI Chatbot", icon="🤖")
st.page_link("socks_chart.py", label="Socks Chart", icon="📈")
st.page_link("daily_socks.py", label="Daily Socks", icon="📊")
```

### 2. Contact Information

Provides external links for the developer’s LinkedIn and GitHub profiles:

```python
st.link_button("LinkedIn", "https://www.linkedin.com/in/sameetpatil5/", type="tertiary")
st.link_button("GitHub", "https://github.com/sameetpatil5", type="tertiary")
```

### 3. Support Section

Allows users to contribute to the project:

```python
st.link_button("Buy Me a Coffee", "https://buymeacoffee.com/sameetpatil5", icon="☕️")
```

## Content Sections

The home page contains three main information tabs: **About SocksAI, How to Use, and Privacy Note**.

### 1. About SocksAI

Describes the main features and purpose of SocksAI:

```python
st.markdown(
    """
    ### SocksAI: Your Stock Trading Assistant  
    **SocksAI** helps traders research, analyze market trends, and make informed decisions.
    
    #### Features  
    - 🤖 **Chatbot** - Get AI-powered stock market insights.  
    - 📈 **Stock Charts & Indicators** - Visualize trends with technical indicators.  
    - 📊 **Daily Stock Insights** - Get daily updates on your watchlisted stocks.  
    """
)
```

### 2. How to Use

Explains how users can set up their API keys and interact with SocksAI:

```python
st.markdown(
    """
    ### How to Use SocksAI  
    **Step 1:** Add your environment keys (Gemini API, MongoDB URL, Qdrant URL, OpenAI API Key).  
    **Step 2:** Explore features like chatbot, stock chart analysis, and daily stock insights.  
    **Step 3:** Watchlist stocks and receive alerts.  
    **Step 4:** Stay updated with AI-driven predictions.  
    """
)
```

### 3. Privacy Note

Details SocksAI’s privacy policies and how it handles user data:

```python
st.markdown(
    """
    ### Privacy Note  
    - SocksAI **does not store** any user data or API keys.  
    - API keys are used only during the session and are not logged or retained.  
    - No third-party tracking is implemented.  
    """
)
```

## Example Usage

### Running the App

To launch the Streamlit app, run:

```bash
streamlit run app.py
```

### Navigating to the Chatbot

```python
st.page_link("socks_chatbot.py", label="SocksAI Chatbot", icon="🤖")
```

## Conclusion

The `SocksAI Home` page serves as the central hub for navigating SocksAI’s features, providing users with essential project information, usage instructions, and privacy policies.
