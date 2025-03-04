import os
import logging
import holidays
import datetime as dt
from typing import Optional, Dict

from pymongo import MongoClient
from google.api_core.exceptions import ResourceExhausted

from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.googlesearch import GoogleSearch
from phi.tools.yfinance import YFinanceTools
from phi.tools.email import EmailTools

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.base import BaseScheduler

from .models.models import NewsModel, StockModel, DailyStockAnalysisModel

# Configure logger
logger = logging.getLogger("api")


class DailyStockSchedulerAgent:
    """
    A class to manage daily stock sentiment analysis using multiple agents.

    Attributes:
        client (MongoClient): MongoDB client instance.
        db: MongoDB database instance.
        scheduler (BackgroundScheduler): Scheduler for automating tasks.
        indian_holidays (holidays.India): List of Indian holidays.
        stocks (List[str]): List of stock symbols to analyze.
        news_agent (Agent): Agent for fetching and analyzing news articles.
        stock_agent (Agent): Agent for fetching financial data.
        daily_stock_analyst_agent (Agent): Agent for analyzing combined data.
        email_agent (Agent): Agent for emailing the Daily analysis report.
    """

    def __init__(self):
        """
        Initialize the DailyStockSentimentAgent with database and agents.
        """
        # Model setup
        try:
            self.model = Gemini(id="gemini-2.0-flash-exp")
            logger.info("Model Loaded")
        except Exception as e:
            logger.error(f"Error loading model: {e}")

        # MongoDB setup
        try:
            self.client = MongoClient(os.environ.get("MONGO_URI"))
            self.db = self.client["socksai-daily-stocks-db"]
            logger.info("MongoDB connected.")
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}")

        # APScheduler setup
        try:
            self.scheduler = BackgroundScheduler()
            self.indian_holidays = holidays.India()
            logger.info("APScheduler connected.")
        except Exception as e:
            logger.error(f"Error connecting to APScheduler: {e}")

        # Stocks
        try:
            self.stocks = []
            self.load_stocks()
            logger.info(f"Stocks loaded: {self.stocks}")
        except Exception as e:
            logger.error(f"Error while loading stocks: {e}")

        # News Agent setup
        try:
            self.news_agent = Agent(
                name="News Agent",
                role="Search and interpret news articles.",
                description="This Agent will search and interpret news articles related to a provided stock, its sector, and any global events that might impact the stock or stock market.",
                response_model=NewsModel,
                model=self.model,
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

            # Stock Agent setup
            self.stock_agent = Agent(
                name="Finance Agent",
                role="Get financial data and interpret trends.",
                model=self.model,
                description="This Agent will retrieve and analyze financial data for a given stock, focusing on real-time, short-term metrics that are critical for immediate analysis.",
                response_model=StockModel,
                tools=[
                    YFinanceTools(
                        stock_price=True,
                        analyst_recommendations=True,
                        company_info=True,
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

            # Daily Stock Analyst Agent setup
            self.daily_stock_analyst_agent = Agent(
                name="Analyst Agent",
                role="Understand data and draw conclusions based on the provided stock financial data and news.",
                description="This Agent will analyze the provided financial data along with the news about the stock and give a proper sentiment statement for the stock.",
                response_model=DailyStockAnalysisModel,
                model=self.model,
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

            # Email Agent setup
            self.email_agent = Agent(
                name="Email Agent",
                role="Send a report to the user via email.",
                description="This Agent will send a report to the user via email.",
                model=self.model,
                tools=[
                    EmailTools(
                        receiver_email=os.environ.get("EMAIL"),
                        sender_email=os.environ.get("EMAIL"),
                        sender_name="SocksAI",
                        sender_passkey=os.environ.get("EMAIL_PASSKEY"),
                    )
                ],
                instructions=[
                    "Send the provided report to the user via email.",
                    "Subject: SocksAI Daily Stock Report",
                ],
                markdown=False,
            )
        except Exception as e:
            logger.error(f"Error while Setting up Agents: {e}")

    def is_daily_stocks_empty(self, func: str = "process") -> bool:
        if not self.stocks:
            logger.info(f"No stocks to process. Skipping {func}.")
            return True
        else:
            return False

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
        try:
            daily_stocks = self.db.get_collection("daily-stocks")
            stored_daily_stocks_data = daily_stocks.find_one(
                {"_id": "daily_stocks_list"}, {"_id": 0, "stocks": 1}
            )

            self.stocks = (
                stored_daily_stocks_data["stocks"] if stored_daily_stocks_data else []
            )
            logger.info("Daily Stocks Loaded")

        except Exception as e:
            logger.error(f"Error while loading Daily Stocks from MongoDB: {e}")

    def reload_stocks(self):
        """
        Reload stock symbols from MongoDB.
        """
        self.load_stocks()

    def fetch_stock_data(self):
        """
        Fetch and store financial data for all tracked stocks.
        """

        if self.is_daily_stocks_empty("fetch_stock_data"):
            return

        today = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")

        if self.is_trading_day():
            logger.info("Today is not a trading day. Skipping stock data fetching.")
            self.pause_scheduler()
            return
        else:
            self.resume_scheduler()
            for stock in self.stocks:
                try:
                    logger.info(f"Fetching stock data for {stock}...")
                    data = self.stock_agent.run(
                        f"Retrieve the latest financial data for the stock ticker {stock}."
                    )
                    try:
                        stock_entry = {
                            "timestamp": dt.datetime.now(dt.timezone.utc),
                            "contents": data.content.dict(),
                        }

                        logger.info(f"Storing data for {stock}...")

                        stock_data = self.db.get_collection("stock-data")

                        result = stock_data.update_one(
                            {"stock_symbol": stock, "date": today},
                            {"$push": {"data": stock_entry}},
                            upsert=True,
                        )

                        if result.matched_count > 0:
                            logger.info(
                                f"Updated existing document for {stock} Data on {today}."
                            )
                        else:
                            logger.info(
                                f"Created new document for {stock} Data on {today}."
                            )
                    except Exception as e:
                        logger.error(f"Error storing stock data for {stock}: {e}")
                except ResourceExhausted as e:
                    logger.warning(
                        f"ResourceExhausted error while fetching stock data for {stock}: {e}"
                    )
                except Exception as e:
                    logger.error(f"Error fetching stock data for {stock}: {e}")

    def fetch_stock_news(self):
        """
        Fetch and store news articles for all tracked stocks.
        """

        if self.is_daily_stocks_empty("fetch_stock_news"):
            return

        today = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")

        if not self.is_trading_day():
            logger.info("Today is not a trading day. Skipping news fetching.")
            self.pause_scheduler()
            return
        else:
            self.resume_scheduler()
            for stock in self.stocks:
                try:
                    logger.info(f"Fetching news for {stock}...")
                    news = self.news_agent.run(
                        f"Retrieve the latest news articles for {stock}."
                    )
                    try:
                        news_entry = {
                            "timestamp": dt.datetime.now(dt.timezone.utc),
                            "contents": news.content.dict(),
                        }

                        logger.info(f"Storing news for {stock}...")

                        stock_news = self.db.get_collection("stock-news")

                        result = stock_news.update_one(
                            {"stock_symbol": stock, "date": today},
                            {"$push": {"data": news_entry}},
                            upsert=True,
                        )

                        if result.matched_count > 0:
                            logger.info(
                                f"Updated existing document for {stock} News on {today}."
                            )
                        else:
                            logger.info(
                                f"Created new document for {stock} News on {today}."
                            )
                    except Exception as e:
                        logger.error(f"Error storing news for {stock}: {e}")
                except ResourceExhausted as e:
                    logger.warning(
                        f"ResourceExhausted error while fetching news for {stock}: {e}"
                    )
                except Exception as e:
                    logger.error(f"Error fetching news for {stock}: {e}")

    def email_report(self, report: str):
        """
        Email a report for all tracked stocks.
        """
        try:
            message = f"Send the provided report for all stocks to <{os.environ.get('EMAIL')}>.\n\n{report}"
            self.email_agent.run(message)
            logger.info("Email report sent successfully.")
        except Exception as e:
            logger.error(f"Error sending email report: {e}")

    def perform_end_of_day_analysis(self) -> None:
        """
        Perform end-of-day analysis for monitored stocks.
        """

        if self.is_daily_stocks_empty("perform_end_of_day_analysis"):
            return

        today = dt.datetime.now(dt.timezone.utc)

        if not self.is_trading_day():
            logger.info("Today is not a trading day. Skipping end-of-day analysis.")
            self.pause_scheduler()
            return
        else:
            self.resume_scheduler()
            for stock in self.stocks:
                # Fetch today's financial data and news
                try:
                    # Fetch today's financial data document
                    stock_doc = self.db.stock_data.find_one(
                        {"stock_symbol": stock, "date": today}
                    )
                    if stock_doc:
                        financial_data = stock_doc.get(
                            "data", []
                        )  # Extract stored periodic data
                    else:
                        financial_data = []

                    # Fetch today's stock news document
                    news_doc = self.db.stock_news.find_one(
                        {"stock_symbol": stock, "date": today}
                    )
                    if news_doc:
                        news_data = news_doc.get(
                            "data", []
                        )  # Extract stored news articles
                    else:
                        news_data = []
                except Exception as e:
                    logger.error(f"Error fetching data for {stock} from MongoDB: {e}")
                    continue

                # Perform analysis
                try:
                    analysis = self.daily_stock_analyst_agent.run(
                        f"Perform analysis for stock {stock} with financial data {financial_data} and news data {news_data}."
                    )

                    self.db.daily_sentiment.update_one(
                        {"stock_symbol": stock, "date": today},
                        {
                            "$set": {
                                "stock_symbol": stock,
                                "date": today,
                                "analysis": analysis,
                                "last_updated": dt.datetime.now(dt.timezone.utc),
                            }
                        },
                        upsert=True,
                    )
                    logger.info(f"End-of-day analysis for {stock} stored successfully.")
                except ResourceExhausted as e:
                    logger.warning(
                        f"ResourceExhausted error during end-of-day analysis for {stock}: {e}"
                    )
                except Exception as e:
                    logger.error(f"Error during end-of-day analysis for {stock}: {e}")

    def schedule_jobs(self) -> None:
        """
        Schedule periodic tasks for fetching stock data and news.
        """
        try:
            # Fetch stock data every 5 minutes during trading hours
            self.scheduler.add_job(
                self.fetch_stock_data,
                trigger=CronTrigger(day_of_week="mon-fri", hour="9-15", minute="*/5"),
                id="fetch_stock_data",
                replace_existing=True,
            )
            # Fetch stock news at the start of every hour during trading hours
            self.scheduler.add_job(
                self.fetch_stock_news,
                trigger=CronTrigger(day_of_week="mon-fri", hour="9-15", minute="0"),
                id="fetch_stock_news",
                replace_existing=True,
            )
            # Perform end-of-day analysis at 16:00 (4:00 PM) after market close
            self.scheduler.add_job(
                self.perform_end_of_day_analysis,
                trigger=CronTrigger(day_of_week="mon-fri", hour="16", minute="0"),
                id="perform_end_of_day_analysis",
                replace_existing=True,
            )
            logger.info("Scheduled periodic tasks.")
        except Exception as e:
            logger.error(f"Error scheduling periodic tasks: {e}")

    def start_scheduler(self) -> None:
        """
        Start the scheduler.
        """
        try:
            if not self.scheduler.running:
                self.schedule_jobs()
                self.scheduler.start()
                logger.info("Agents and scheduler started.")
            else:
                logger.info("Scheduler is already running.")
        except Exception as e:
            logger.error(f"Error starting agents and scheduler: {e}")

    def stop_scheduler(self) -> None:
        """
        Stop the scheduler.
        """
        try:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped.")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")

    def resume_scheduler(self) -> None:
        """
        Restart the scheduler and agents.
        """
        try:
            if self.scheduler.state == 2:
                self.scheduler.resume()
                logger.info("Scheduler resumed.")
            else:
                logger.info("Scheduler is not paused. Skipping resume.")
        except Exception as e:
            logger.error(f"Error resuming scheduler: {e}")

    def pause_scheduler(self) -> None:
        """
        Pause the scheduler and agents.
        """
        try:
            if self.scheduler.state == 1:
                self.scheduler.pause()
                logger.info("Scheduler paused.")
            else:
                logger.info("Scheduler is not running. Skipping pause.")
        except Exception as e:
            logger.error(f"Error pausing scheduler: {e}")

    def toggle_scheduler(self) -> str:
        """
        Toggle the current state of the scheduler between paused and resumed.

        Returns:
            str: A message indicating the new state of the scheduler, either
            "paused" or "resumed". Returns "error" if an exception occurs.
        """

        try:
            if self.scheduler.state == 1:
                self.scheduler.pause()
                logger.info("Scheduler toggle paused.")
                return "paused"
            elif self.scheduler.state == 2:
                self.scheduler.resume()
                logger.info("Scheduler toggle resumed.")
                return "resumed"
            else:
                logger.info("Scheduler is not running. Skipping toggle.")
                return "error"
        except Exception as e:
            logger.error(f"Error toggling scheduler: {e}")
            return "error"

    def refresh_scheduler(self) -> None:
        """
        Refresh the scheduler by stopping and restarting it.
        """
        try:
            self.stop_scheduler()
            self.start_scheduler()
            logger.info("Scheduler refreshed.")
        except Exception as e:
            logger.error(f"Error refreshing scheduler: {e}")

    def get_scheduler_state(self) -> int:
        """
        Get the current state of the scheduler.

        Returns:
            int: The state of the scheduler, either 0 (stopped) or 1 (running) or 2 (paused).
        """
        return self.scheduler.state

    def get_scheduler_status(self) -> Optional[Dict[str, Dict[bool | str, str]]]:
        try:
            status = {}

            job_ids = {
                "Fetch Stock Data": "fetch_stock_data",
                "Fetch Stock News": "fetch_stock_news",
                "Perform End-of-Day Analysis": "perform_end_of_day_analysis",
            }

            scheduler_state = self.get_scheduler_state()

            if scheduler_state == 2 or scheduler_state == 0:
                status["State"] = scheduler_state
            elif scheduler_state == 1:
                status["State"] = scheduler_state
                status["Jobs"] = {}
                for job_name, job_id in job_ids.items():
                    job = self.scheduler.get_job(job_id)
                    logger.info(job)
                    if job:
                        status["Jobs"][job_name] = (
                            job.next_run_time.strftime("%Y-%m-%d %H:%M:%S")
                            if job.next_run_time
                            else "Not scheduled"
                        )
                        
                    else:
                        status["Jobs"] = {job_name: "Job not found"}

            return status
        except Exception as e:
            logger.error(f"Error getting scheduler status: {e}")
            return None
