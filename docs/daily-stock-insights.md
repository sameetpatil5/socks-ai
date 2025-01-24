# Daily Stock Sentiment Agent Documentation

## Overview

This project aims to analyze stock sentiment daily by gathering financial data, news articles, and conducting a sentiment analysis for multiple stocks. The system integrates various tools and agents to fetch real-time data and generate actionable insights for stock analysis.

## Libraries and Tools Used

The following libraries and tools are utilized in the project:

- **logging**: For logging system activity and errors.
- **holidays**: To check if today is a trading day, excluding holidays.
- **datetime**: For managing and manipulating date and time.
- **typing**: For type hinting (e.g., `List`).
- **pymongo**: To interact with MongoDB for storing and retrieving stock data and news.
- **phi**: A framework for building agents that can retrieve and analyze data. Agents like `Sentiment Agent`, `Finance Agent`, and `Analyst Agent` are used to process data.
- **apscheduler**: To schedule periodic tasks for fetching data and performing analyses.
- **yfinance**: For retrieving financial data for stocks.
- **GoogleSearch**: For fetching relevant news articles using Google search.

## Configuration

### MongoDB Setup

MongoDB is used to store stock data and news articles. The connection is configured as follows:

```python
self.client = MongoClient(db_uri)
self.db = self.client[db_name]
```

- `db_uri`: The URI for connecting to the MongoDB database.
- `db_name`: The name of the MongoDB database to use.

### APScheduler Setup

The APScheduler is used to automate tasks, such as fetching stock data and news articles periodically:

```python
self.scheduler = BackgroundScheduler()
```

Tasks are scheduled using `CronTrigger`, allowing periodic execution based on specified intervals (e.g., every 5 minutes during trading hours).

### Agent Setup

Several agents are configured to handle different tasks:

1. **Sentiment Agent**: Retrieves and interprets news articles related to stocks.
2. **Finance Agent**: Fetches financial data for stocks using the `yfinance` tool.
3. **Analyst Agent**: Analyzes the data from the Sentiment and Finance Agents to provide a sentiment score.
4. **Team of Agents**: Combines insights from all agents to provide a concise summary of the stock's performance.

Each agent is initialized with the required tools, instructions, and models.

## Workflow

### 1. Stock Data and News Fetching

The system fetches stock data and news articles periodically for each tracked stock symbol. The following functions are used:

- `fetch_stock_data()`: Retrieves financial data using the Finance Agent and stores it in MongoDB.
- `fetch_stock_news()`: Retrieves news articles using the Sentiment Agent and stores them in MongoDB.

### 2. Sentiment Analysis

At the end of each trading day, the system performs sentiment analysis for each stock using the Analyst Agent. This involves:

- Retrieving the stock's financial data and news articles.
- Performing sentiment analysis on the news and financial data.
- Storing the analysis result in MongoDB.

### 3. Scheduling Tasks

The system schedules tasks for fetching stock data and news using the APScheduler. Tasks are executed periodically during trading hours (Monday to Friday, 9 AM to 3 PM).

### 4. Quick Analysis

A quick analysis of all monitored stocks can be performed using the `perform_quick_analysis()` method, which combines insights from all agents.

## Problem Tackled

### Handling Holidays

To ensure that tasks are not scheduled on holidays, the `is_trading_day()` method checks if today is a trading day based on the current weekday and the list of Indian holidays.

### Storing Data

Stock data and news articles are stored in MongoDB for each stock, with timestamps to ensure the data is up-to-date.

### Sentiment Scoring

The sentiment of each news article is scored on a scale from 1 (very negative) to 10 (very positive). Similarly, the overall sentiment for a stock is derived by combining the sentiment from financial data and news articles.

### Scheduling Periodic Tasks

Using APScheduler, the system automates the fetching of data and performs sentiment analysis without manual intervention.

## Example Usage

To start the system, initialize the `DailyStockSentimentAgent` with the MongoDB URI and database name:

```python
agent = DailyStockSentimentAgent(db_uri="", db_name="")
agent.start_agents()
```

To add a stock for analysis:

```python
agent.add_stock("AAPL")
```

To perform a quick analysis:

```python
summaries = agent.perform_quick_analysis()
```

## Conclusion

This system integrates multiple agents to automate the process of stock sentiment analysis, making it easier to track and analyze stock performance based on real-time data and news. The use of MongoDB for storage and APScheduler for task automation ensures that the system runs smoothly and efficiently.

https://medium.com/@astropomeai/creating-an-ai-agent-mastering-various-tools-with-streamlit-langchain-a59a0c19494e