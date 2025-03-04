# Daily Stock Scheduler Agent Documentation

## Overview

The `DailyStockSchedulerAgent` automates the process of fetching, analyzing, and reporting stock data and news. It integrates financial data retrieval, sentiment analysis, and email notifications to provide users with insights into daily stock performance.

## Libraries and Tools Used

The following libraries and tools are utilized in the project:

- **logging**: For logging system activity and errors.
- **holidays**: To check if today is a trading day, excluding holidays.
- **datetime**: For managing and manipulating date and time.
- **pymongo**: To interact with MongoDB for storing and retrieving stock data and news.
- **phi**: A framework for building AI-powered agents that handle stock data retrieval and sentiment analysis.
- **apscheduler**: To schedule periodic tasks for fetching data and performing analyses.
- **GoogleSearch**: For fetching relevant news articles using Google search.
- **YFinanceTools**: For retrieving real-time financial data.
- **EmailTools**: For sending stock reports via email.

## Configuration

### MongoDB Setup

The system connects to MongoDB for data storage and retrieval:

```python
self.client = MongoClient(os.environ.get("MONGO_URI"))
self.db = self.client["socksai-daily-stocks-db"]
```

### APScheduler Setup

The APScheduler is used to automate tasks such as fetching stock data and performing sentiment analysis:

```python
self.scheduler = BackgroundScheduler()
```

Tasks are scheduled using `CronTrigger` to execute periodically during trading hours.

### Agent Setup

Several AI-powered agents are configured to handle different tasks:

1. **News Agent**: Fetches and interprets stock-related news.
2. **Finance Agent**: Retrieves and analyzes financial data for stocks.
3. **Analyst Agent**: Combines news and financial data to provide a sentiment analysis.
4. **Email Agent**: Sends daily stock reports via email.

Each agent is initialized with appropriate tools, models, and structured outputs.

## Workflow

### 1. Stock Data and News Fetching

The system periodically fetches stock data and news articles for tracked stocks.

- `fetch_stock_data()`: Retrieves real-time financial data.
- `fetch_stock_news()`: Gathers news articles related to stocks.

### 2. Sentiment Analysis

At the end of each trading day, the system analyzes the sentiment of stocks:

- Retrieves stock data and news articles.
- Processes sentiment analysis using the Analyst Agent.
- Stores the analysis in MongoDB.

### 3. Scheduling Tasks

The system schedules data retrieval and sentiment analysis jobs:

- Fetch stock data every 5 minutes during trading hours.
- Fetch stock news at the start of each hour.
- Perform end-of-day analysis at 4:00 PM.

### 4. Email Reporting

The system emails daily stock reports using the Email Agent:

- `email_report(report: str)`: Sends a summary of stock performance.

## Problem Tackled

### Handling Non-Trading Days

The `is_trading_day()` method ensures that tasks are skipped on weekends and public holidays.

### Data Storage

Stock data and news are stored in MongoDB with timestamps to maintain accuracy and history.

### Sentiment Scoring

- News articles are scored on a scale from 1 (very negative) to 10 (very positive).
- Financial data is analyzed for bullish, bearish, or neutral trends.

### Scheduling and Automation

Using APScheduler, tasks are automated for efficient execution without manual intervention.

## Example Usage

### Initialize and Start Scheduler

```python
agent = DailyStockSchedulerAgent()
agent.start_scheduler()
```

### Add Stocks for Analysis

```python
agent.stocks.append("AAPL")
agent.reload_stocks()
```

### Perform End-of-Day Analysis

```python
agent.perform_end_of_day_analysis()
```

### Fetch Stock Data and News Manually

```python
agent.fetch_stock_data()
agent.fetch_stock_news()
```

### Get Scheduler Status

```python
status = agent.get_scheduler_status()
print(status)
```

## Conclusion

The `DailyStockSchedulerAgent` automates stock monitoring and sentiment analysis. It integrates financial and news data retrieval with AI-driven sentiment analysis and email notifications, ensuring users receive timely stock insights efficiently.
