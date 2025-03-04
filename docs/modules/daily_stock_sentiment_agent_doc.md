# Daily Stock Sentiment Agent Documentation

## Overview

The `DailyStockSentimentAgent` is responsible for performing sentiment analysis on stocks by gathering financial data, news articles, and generating a high-level summary of market sentiment. It uses AI-driven agents to retrieve real-time data and provide actionable insights.

## Libraries and Tools Used

The following libraries and tools are utilized in the project:

- **logging**: For logging system activity and errors.
- **datetime**: For handling date and time operations.
- **pymongo**: To interact with MongoDB for storing and retrieving stock data.
- **phi**: A framework for building AI-powered agents for stock analysis.
- **GoogleSearch**: For fetching relevant news articles.
- **YFinanceTools**: For retrieving financial data, including stock prices and trends.

## Configuration

### MongoDB Setup

The system connects to MongoDB for data storage:

```python
self.client = MongoClient(db_uri)
self.db = self.client["socksai-daily-stocks-db"]
```

### Agent Setup

The agent responsible for quick sentiment analysis:

1. **Quick Analysis Agent**: Fetches real-time stock data and news to generate a concise market summary.

```python
self.quick_analysis_agent = Agent(
    name="Quick Analysis Agent",
    role="Stock Analysis Assistant",
    description="Generates a quick, data-driven analysis of the given stock to provide users with a concise market snapshot.",
    response_model=QuickAnalysisModel,
    model=self.model,
    tools=[YFinanceTools(enable_all=True), GoogleSearch()],
    structured_outputs=True,
)
```

## Workflow

### 1. Stock Management

The system loads and manages tracked stocks from MongoDB:

- `load_stocks()`: Loads stock symbols from the database.
- `add_stocks(stock_symbols: list[str])`: Adds stock symbols for monitoring.
- `remove_stocks(stock_symbols: list[str])`: Removes stocks from monitoring.

### 2. Quick Analysis

The agent performs real-time stock analysis:

- Fetches stock data and recent news.
- Generates a structured market summary.
- Provides sentiment insights.

### 3. Data Storage

Analysis results are stored in MongoDB for further processing and retrieval.

## Example Usage

### Initialize the Agent

```python
agent = DailyStockSentimentAgent(db_uri="mongodb://localhost:27017", model=Gemini(id="gemini-2.0-flash-exp"))
```

### Add Stocks for Monitoring

```python
agent.add_stocks(["AAPL", "TSLA"])
```

### Perform Quick Analysis

```python
summaries = agent.perform_quick_analysis()
print(summaries)
```

### Remove Stocks from Monitoring

```python
agent.remove_stocks(["AAPL"])
```

## Conclusion

The `DailyStockSentimentAgent` integrates AI-based stock sentiment analysis, leveraging real-time financial data and news articles. It allows users to track stock performance efficiently and receive structured insights into market trends.
