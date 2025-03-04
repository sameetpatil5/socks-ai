# Socks Chart Page Documentation

## Overview

The `socks_chart.py` file is a Streamlit page that allows users to visualize stock price data with technical indicators. It provides functionalities to fetch stock charts, apply moving averages, Bollinger Bands, and perform AI-driven chart analysis.

## Libraries and Tools Used

The following libraries and tools are utilized in the project:

- **streamlit**: Web framework for UI development.
- **logging**: For tracking application activity.
- **datetime**: For handling date and time selections.
- **plotly.graph_objects**: For generating interactive stock charts.
- **streamlit_components**: Custom UI enhancements like buttons, toasts, and dialogs.

## Page Configuration

The page is configured with a custom layout:

```python
st.set_page_config(
    page_title="SocksAI",
    page_icon=":socks:",
    layout="wide",
    initial_sidebar_state="expanded",
)
```

## Workflow

### 1. Plotting Stock Charts

The application plots stock charts using historical data and selected technical indicators:

```python
@st.cache_data(ttl=dt.timedelta(days=1), max_entries=100)
def plot_chart(symbol: str, period: Tuple[dt.date, dt.date], interval: str, chart_type: str, indicators: list) -> go.Figure:
    try:
        fig = st.session_state.sca.plot_chart(symbol, period, interval, chart_type, indicators)
        show_toast(f"Plotted the Chart for {symbol}")
        return fig
    except Exception as e:
        logger.error(f"Error while plotting chart for {symbol}: {e}")
        return go.Figure()
```

### 2. Validating Date Selection

Ensures that users select both start and end dates for the stock chart:

```python
def both_interval_selected(time_period):
    return isinstance(time_period, tuple) and len(time_period) == 2 and all(isinstance(d, dt.date) for d in time_period)
```

### 3. AI-Powered Chart Analysis

The AI agent analyzes stock charts and generates insights:

```python
@st.dialog("Stock Chart Analysis")
def analyze_chart(chart: go.Figure):
    try:
        response = st.session_state.sca.analyze_plot(chart)
        with st.spinner("Reading Chart"):
            st.write_stream(response)
    except:
        logger.error("Error while Analyzing Stock Chart")
```

### 4. Reset and Refresh Functions

Allows users to reset selections or refresh cached data:

```python
def reset_selections():
    for key in ["chart_symbol", "chart_time_period", "chart_time_interval", "chart_chart_type", "chart_indicators"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()
```

```python
if st.button("Refresh", icon="🔃", help="Clears all cache data and refreshes the page"):
    st.cache_data.clear()
    show_toast("Cleared the Streamlit Cache Data!")
    st.rerun()
```

## UI Components

### Stock and Indicator Selection

Allows users to input stock symbols, time periods, intervals, chart types, and technical indicators:

```python
symbol = st.text_input("Stock Symbol", placeholder="Stock ticker symbol", key="chart_symbol").upper()
time_period = st.date_input("Time Period", value=(dt.date.today() - dt.timedelta(days=1), dt.date.today()), key="chart_time_period")
time_interval = st.selectbox("Time Interval", ["1m", "5m", "1d", "1w", "1mo"], key="chart_time_interval")
chart_type = st.selectbox("Chart Type", ["Candlestick", "Line"], key="chart_chart_type")
indicators = st.multiselect("Indicators", ["SMA_20", "EMA_20", "BB_20", "VWAP"], default=["SMA_20", "EMA_20"], key="chart_indicators")
```

### Chart Rendering and Controls

Renders the stock chart and provides action buttons for analysis and resetting selections:

```python
if symbol:
    if both_interval_selected(time_period):
        chart = plot_chart(symbol, time_period, time_interval, chart_type, indicators)
        st.plotly_chart(chart, use_container_width=True)
    else:
        st.area_chart()
```

```python
if st.button("Analyze", icon="🔍"):
    analyze_chart(chart)
```

## Example Usage

### Running the App

To launch the Streamlit app, run:

```bash
streamlit run app.py
```

### Plotting a Stock Chart

```python
chart = plot_chart(symbol="AAPL", period=(dt.date.today()-dt.timedelta(days=30), dt.date.today()), interval="1d", chart_type="Candlestick", indicators=["SMA_20", "EMA_20"])
st.plotly_chart(chart)
```

### Performing AI Analysis on the Chart

```python
analyze_chart(chart)
```

## Conclusion

The `Socks Chart` page enables users to visualize stock trends using historical price data and technical indicators. It integrates AI-powered analysis, making stock trend evaluation more efficient and insightful.
