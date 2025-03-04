# Daily Socks Page Documentation

## Overview

The `daily_socks.py` file is a Streamlit page for managing the `Daily Socks` stock sentiment analysis scheduler. It allows users to add, remove, and analyze stocks daily while providing real-time insights through a scheduled automation system.

## Libraries and Tools Used

The following libraries and tools are utilized in the project:

- **streamlit**: Web framework for UI development.
- **logging**: For logging system events and debugging.
- **requests**: For making API calls to the backend server.
- **streamlit_components**: Custom components for enhanced UI experience.

## Page Configuration

The page is configured with a custom layout and sidebar state:

```python
st.set_page_config(
    page_title="SocksAI",
    page_icon=":socks:",
    layout="wide",
    initial_sidebar_state="expanded",
)
```

## Scheduler State Mapping

The application maintains different states for the sentiment analysis scheduler:

```python
SCHEDULER_STATE = {
    0: "Stopped",
    1: "Running",
    2: "Paused",
}
```

## Workflow

### 1. Fetching Scheduler Status

The application fetches the scheduler status from the backend server:

```python
def get_scheduler_status():
    try:
        response = requests.get(f"{st.session_state.server_url}/scheduler_status")
        return response.json() if response.status_code == 200 else {"error": "Failed to fetch scheduler status."}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
```

### 2. Managing Stock Symbols

Users can add or remove stock symbols that should be analyzed daily.

#### Add Daily Stocks

```python
def add_daily_stock():
    query = st.text_input("Enter a stock symbol or query:")
    if st.button("Find Stocks", key="find_daily_stocks"):
        st.session_state.found_stocks = st.session_state.fsa.find_stock(query)
        if not st.session_state.found_stocks:
            show_toast("No stocks found. Please try again.")
```

#### Remove Daily Stocks

```python
def remove_daily_stock():
    if st.session_state.found_stocks:
        stocks_to_remove = st.pills(
            label="Remove Daily Stocks",
            options=st.session_state.found_stocks,
            selection_mode="multi",
        )
    if st.button("Confirm & Remove", key="confirm_remove_daily"):
        st.session_state.dssa.remove_stocks(stocks_to_remove)
        reload_stocks()
```

### 3. Controlling the Scheduler

Users can start, stop, refresh, and toggle the scheduler state.

#### Start Scheduler

```python
def start_scheduler():
    response = requests.post(f"{st.session_state.server_url}/start_scheduler")
    if response.status_code == 200:
        show_toast("Daily Socks Scheduler started successfully.")
```

#### Stop Scheduler

```python
def stop_scheduler():
    response = requests.post(f"{st.session_state.server_url}/stop_scheduler")
    if response.status_code == 200:
        show_toast("Daily Socks Scheduler stopped successfully.")
```

#### Toggle Scheduler State

```python
def toggle_scheduler():
    response = requests.post(f"{st.session_state.server_url}/toggle_scheduler")
    if response.status_code == 200:
        show_toast(response.json()["message"])
```

#### Refresh Scheduler

```python
def refresh_scheduler():
    response = requests.post(f"{st.session_state.server_url}/refresh_scheduler")
    if response.status_code == 200:
        show_toast("Daily Socks Scheduler refreshed successfully.")
```

## UI Components

### Daily Stocks Section

Displays a list of stocks being monitored for daily sentiment analysis:

```python
with st.container(border=True):
    st.markdown("### Stocks with Daily Socks Sentiment Analysis")
    for stock in st.session_state.daily_stocks:
        st.markdown(f"**{stock}**")
    st.button("Add more Stocks", on_click=add_daily_stock)
    st.button("Remove Stocks", on_click=remove_daily_stock)
```

### Scheduler Control Section

Allows users to start, stop, and refresh the scheduler:

```python
with st.container(border=True):
    st.markdown("### Daily Stocks Analysis Scheduler")
    st.button("Start Daily Socks Scheduler", on_click=start_scheduler)
    st.button("Stop Daily Socks Scheduler", on_click=stop_scheduler)
    st.button("Refresh Scheduler", on_click=refresh_scheduler)
    st.toggle("Pause Scheduler", key="pause_scheduler", on_change=toggle_scheduler)
```

## Example Usage

### Running the App

To launch the Streamlit app, run the following command:

```bash
streamlit run app.py
```

### Adding a New Stock for Analysis

```python
st.session_state.dssa.add_stocks(["AAPL"])
```

### Performing Quick Analysis

```python
summaries = st.session_state.dssa.perform_quick_analysis()
print(summaries)
```

## Conclusion

The `Daily Socks` page provides an interactive interface for managing the daily stock sentiment analysis scheduler. It enables users to automate stock tracking, sentiment evaluation, and quick market analysis with real-time insights.
