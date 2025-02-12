import logging
import holidays
import datetime as dt
from typing import List
from pymongo import MongoClient
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.googlesearch import GoogleSearch
from phi.tools.yfinance import YFinanceTools
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from .models.models import QuickAnalysisModel

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class DailyStockSentimentAgent:
    """
    A class to manage daily stock sentiment analysis using multiple agents.

    Attributes:
        db_uri (str): URI for connecting to the MongoDB database.
        db_name (str): Name of the MongoDB database.
        client (MongoClient): MongoDB client instance.
        db: MongoDB database instance.
        scheduler (BackgroundScheduler): Scheduler for automating tasks.
        indian_holidays (holidays.India): List of Indian holidays.
        stocks (List[str]): List of stock symbols to analyze.
        sentiment_agent (Agent): Agent for fetching and analyzing news articles.
        finance_agent (Agent): Agent for fetching financial data.
        analyst_agent (Agent): Agent for analyzing combined data.
        agent_team (Agent): Agent combining all other agents for quick summaries.
    """

    def __init__(self, db_uri: str, db_name: str):
        """
        Initialize the DailyStockSentimentAgent with database and agents.

        Args:
            db_uri (str): MongoDB connection URI.
            db_name (str): Name of the MongoDB database.
        """
        # MongoDB setup
        self.client = MongoClient(db_uri)
        self.db = self.client[db_name]

        # APScheduler setup
        self.scheduler = BackgroundScheduler()
        self.indian_holidays = holidays.India()

        # Stocks
        self.stocks = []

        # Sentiment Agent setup
        self.sentiment_agent = Agent(
            name="Sentiment Agent",
            role="Search and interpret news articles.",
            description="This Agent will search and interpret news articles related to a provided stock, its sector, and any global events that might impact the stock or stock market.",
            response_model=NewsModel,
            model=Gemini(id="gemini-2.0-flash-exp"),
            tools=[GoogleSearch()],
            instructions=[
                "Retrieve the latest news articles related to the provided stock, its sector, and any global events that might impact the stock or stock market.",
                "Follow these instructions:",
                "### **Scope of News Search**:",
                "1. **Stock-Specific News**:",
                "- Find news articles directly related to the provided stock",
                "2. **Sector News**:",
                "- Search for news relevant to the sector or industry the stock belongs to.",
                "3. **Global or Market-Wide News**:",
                "- Include any significant global or market-wide events that might impact the stock market as a whole or the specific stock.",
                "### **Additional Notes**:",
                "- Ensure all numerical data is within appropriate ranges.",
                "- Filter out duplicate or irrelevant articles.",
                "- Focus on credible and up-to-date sources.",
                "### **Output Requirements**:",
                "- `symbol`: The stock ticker symbol (string).",
                "- `news`: A list of news articles (List[News]).",
                "- `News.title`: The title of the article (string).",
                "- `News.summary`: A brief summary of the article (string).",
                "- `News.sentiment_score`: Assign a sentiment score to each article on a scale of 1 (very negative) to 10 (very positive) (integer).",
                "- `News.impact_score`: Evaluate the potential impact of each article on the stock. Use a scale of 1 (low impact) to 10 (high impact) (integer).",
                "- `News.source`: Include the source link of the article. (string).",
                "- `News.publication_date`: Include the publication date of the article (string) [YYYY-MM-DD].",
                "Ensure the output strictly adheres to the provided schema.",
            ],
            markdown=False,
            structured_outputs=True,
        )

        # Finance Agent setup
        self.finance_agent = Agent(
            name="Finance Agent",
            role="Get financial data and interpret trends.",
            model=Gemini(id="gemini-2.0-flash-exp"),
            description="This Agent will retrieve and analyze financial data for a given stock, focusing on real-time, short-term metrics that are critical for immediate analysis.",
            response_model=StockModel,
            tools=[
                YFinanceTools(
                    stock_price=True, analyst_recommendations=True, company_info=True
                )
            ],
            instructions=[
                "Retrieve the latest financial data for the provided stock.",
                "Focus on real-time, short-term metrics that are critical for immediate analysis.",
                "Follow these instructions:",
                "1. **Current Stock Price**: Provide the current price of the stock with currency.",
                "2. **Analyst Recommendations**: Provide the latest analyst recommendations and price targets.",
                "3. **Current Stock Performance**: Fetch the latest stock price, percentage change, and volume.\
                    Include key metrics like open, high, low, and close prices for the current trading session.",
                "**Output Requirements**:",
                "- `symbol`: The stock ticker symbol (string).",
                "- `price`: An object with `currency` (string) and `price` (float) fields.",
                "- `analyst_insights`: Latest analyst recommendations and price targets (string).",
                "- `performance`: A summary of key stock performance metrics (e.g., price, volume, percentage change) (string).",
                "Ensure the output strictly adheres to the provided schema.",
            ],
            markdown=False,
            structured_outputs=True,
        )

        # Analyst Agent setup
        self.analyst_agent = Agent(
            name="Analyst Agent",
            role="Understand data and draw conclusions based on the provided stock financial data and news.",
            description="This Agent will analyze the provided financial data along with the news about the stock and give a proper sentiment statement for the stock.",
            response_model=AnalystModel,
            model=Gemini(id="gemini-2.0-flash-exp"),
            instructions=[
                "Perform a detailed sentiment analysis for the provided stock based on the provided financial data and news articles from today.",
                "Follow these instructions:",
                "1. **Financial Data Analysis**:",
                "- Analyze the provided stock data, including price trends, volume, and any other key metrics.",
                "- Highlight any significant changes or patterns observed during the day.",
                "- Summarize the overall market sentiment for the stock based on the financial data (e.g., bullish, bearish, or neutral).",
                "2. **News Sentiment Analysis**:",
                "- Review the news articles for provided stock.",
                "- Extract the key points and assess the sentiment (positive, neutral, or negative).",
                "- Understand and patterns in the articles to determine overall sentiment.",
                "3. **Overall Sentiment**:",
                "- Combine insights from the financial data and news sentiment analysis.",
                "- Assign a final sentiment score for the stock on a scale of 1 to 10, with justification.",
                "- Provide a brief summary which will be like a sentiment statement for the stock for the day.",
                "**Output Requirements**:",
                "- `symbol`: The stock ticker symbol (string).",
                "- `closing_price`: The closing price of the stock as an object with `currency` (string) and `price` (float) fields.",
                "- `analyst_insights`: Latest analyst recommendations and price targets (string).",
                "- `performance`: A summary of key stock performance metrics (e.g., price, volume, percentage change) (string).",
                "- `sentiment_score`: Sentiment score (1-10) (integer).",
                "- `sentiment_statement`: Overall summary for the stock for the day as a sentiment analysis (string).",
                "Ensure the output strictly adheres to the provided schema.",
            ],
            markdown=False,
            structured_outputs=True,
        )

        # Team of Agents setup
        self.agent_team = Agent(
            name="Team of Agents",
            role="Provide a concise summary of the provided stock",
            description="This Agent will combine the expertise of all agents to provide a cohesive, well-supported response.",
            response_model=QuickAnalysisModel,
            model=Gemini(id="gemini-2.0-flash-exp"),
            tools=[
                YFinanceTools(
                    stock_price=True, analyst_recommendations=True, company_info=True
                ),
                GoogleSearch(),
            ],
            instructions=[
                "Combine the expertise of all agents to provide a cohesive, well-supported response.",
                "Follow these instructions:",
                "Provide a quick, high-level analysis for the stock ticker.",
                "Combine insights from sentiment analysis, financial data, and expert conclusions.",
                "Focus on providing actionable insights without detailed thought chains.",
                "Summarize response in a concise manner.",
                "Ensure the summary is limited to one paragraph and includes all key points.",
                "**Output requirements**:",
                "- `symbol`: The stock ticker symbol (string).",
                "- `price`: An object with `currency` (string) and `price` (float) fields.",
                "- `summary`: A concise summary of the stock (string).",
                "Ensure the output strictly adheres to the provided schema.",
            ],
            markdown=False,
            structured_outputs=True,
            tool_choice="auto",
        )

        self.load_stocks()

    def is_trading_day(self) -> bool:
        """
        Check if today is a trading day.

        Returns:
            bool: True if today is a trading day, False otherwise.
        """
        today = dt.date.today()
        return today.weekday() < 5 and today not in self.indian_holidays

    def load_stocks(self):
        """
        Load stock symbols from MongoDB when initializing the class.
        """
        stored_data = self.db.daily_stocks.find_one(
            {"_id": "daily_stocks_list"}, {"_id": 0, "stocks": 1}
        )
        self.stocks = stored_data["stocks"] if stored_data else []

    def add_stocks(self, stock_symbols: list[str]):
        """
        Add a list of stock symbols to MongoDB for tracking.

        Args:
            stock_symbols (list[str]): List of stock symbols to add.
        """
        self.db.daily_stocks.update_one(
            {"_id": "daily_stocks_list"},
            {
                "$addToSet": {"stocks": {"$each": stock_symbols}}
            },
            upsert=True,
        )
        logging.info(f"Added stocks: {stock_symbols}")

    def fetch_stock_data(self):
        """
        Fetch and store financial data for all tracked stocks.
        """
        for stock in self.stocks:
            data = self.finance_agent.run(
                f"Retrieve the latest financial data for the stock ticker {stock}."
            )
            try:
                # pprint(data.content.dict())
                self.db.stock_data.insert_one(
                    {
                        "symbol": stock,
                        "data": data,
                        "timestamp": dt.datetime.now(dt.timezone.utc),
                    }
                )
                logging.info(f"Stock data fetched for {stock} and stored in MongoDB.")
            except Exception as e:
                logging.error(f"Error storing stock data for {stock}: {e}")

    def fetch_stock_news(self):
        """
        Fetch and store news articles for all tracked stocks.
        """
        for stock in self.stocks:
            news = self.sentiment_agent.run(
                f"Retrieve the latest news articles for {stock}."
            )
            try:
                # pprint(news.content.dict())
                self.db.stock_news.insert_one(
                    {
                        "symbol": stock,
                        "news": news,
                        "timestamp": dt.datetime.now(dt.timezone.utc),
                    }
                )
                logging.info(
                    f"News articles fetched for {stock} and stored in MongoDB."
                )
            except Exception as e:
                logging.error(f"Error storing news for {stock}: {e}")

    def perform_end_of_day_analysis(self) -> None:
        """
        Perform end-of-day analysis for monitored stocks.
        """
        # Define the start and end of the day in UTC
        today = dt.datetime.now(dt.timezone.utc)
        start_of_day = dt.datetime(
            today.year, today.month, today.day, tzinfo=dt.timezone.utc
        )
        end_of_day = start_of_day + dt.timedelta(days=1)

        for stock in self.stocks:
            # Fetch today's financial data and news
            financial_data = list(
                self.db.stock_data.find(
                    {
                        "symbol": stock,
                        "timestamp": {"$gte": start_of_day, "$lt": end_of_day},
                    }
                )
            )
            news_data = list(
                self.db.stock_news.find(
                    {
                        "symbol": stock,
                        "timestamp": {"$gte": start_of_day, "$lt": end_of_day},
                    }
                )
            )

            # Perform analysis
            analysis = self.analyst_agent.run(
                f"Perform analysis for stock {stock} with financial data {financial_data} and news {news_data}."
            )
            self.db.daily_sentiment.insert_one(
                {
                    "symbol": stock,
                    "analysis": analysis,
                    "timestamp": dt.datetime.now(dt.timezone.utc),
                }
            )
            logging.info(f"End-of-day analysis for {stock} completed.")

    def schedule_tasks(self) -> None:
        """
        Schedule periodic tasks for fetching stock data and news.
        """
        if self.is_trading_day():
            self.scheduler.add_job(
                self.fetch_stock_data,
                trigger=CronTrigger(day_of_week="mon-fri", hour="9-15", minute="*/5"),
                id="fetch_stock_data",
                replace_existing=True,
            )
            self.scheduler.add_job(
                self.fetch_stock_news,
                trigger=CronTrigger(day_of_week="mon-fri", hour="9-15", minute="0"),
                id="fetch_stock_news",
                replace_existing=True,
            )
            logging.info("Scheduled periodic tasks.")

    def start_agents(self) -> None:
        """
        Start the agents and scheduler.
        """
        self.schedule_tasks()
        self.scheduler.start()
        logging.info("Agents and scheduler started.")

    def stop_agents(self) -> None:
        """
        Stop the scheduler and agents.
        """
        self.scheduler.shutdown()
        logging.info("Scheduler stopped.")

    def perform_quick_analysis(self) -> List[dict]:
        """
        Perform a quick analysis for all monitored stocks.

        Returns:
            List[dict]: A list of quick analysis summaries for stocks.
        """
        summaries = []
        for stock in self.stocks:
            try:
                response = self.agent_team.run(
                    f"Perform a quick analysis for the stock {stock}."
                )
                summaries.append(response.content.dict())
                logging.info(f"Quick analysis for {stock} completed.")
            except Exception as e:
                logging.error(f"Error during quick analysis for {stock}: {e}")
        return summaries
