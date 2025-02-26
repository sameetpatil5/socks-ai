import logging
import datetime as dt
from typing import List

from pymongo import MongoClient

from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.googlesearch import GoogleSearch
from phi.tools.yfinance import YFinanceTools

from .models.models import QuickAnalysisModel

# Configure logging
logger = logging.getLogger("app")


class DailyStockSentimentAgent:
    """
    A class to manage daily stock sentiment analysis using multiple agents.

    Attributes:
        model (Gemini): The Gemini model used for AI-based analysis.
        client (MongoClient): MongoDB client instance.
        db: MongoDB database instance.
        stocks (List[str]): List of stock symbols tracked for analysis.
        quick_analysis_agent (Agent): An AI agent that combines insights from
                                      multiple sources for quick stock analysis.
    """

    def __init__(self, db_uri: str, model: Gemini):
        """
        Initialize the DailyStockSentimentAgent with database and agents.

        Args:
            db_uri (str): MongoDB connection URI.
            model (Gemini): Gemini Model.
        """
        # Model setup
        try:
            self.model = model
            logger.info("Model Loaded")
        except Exception as e:
            logger.error(f"Error while loading model: {e}")

        # MongoDB setup
        try:
            self.client = MongoClient(db_uri)
            self.db = self.client["socksai-daily-stocks-db"]
            logger.info("Connected to MongoDB successfully.")
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}")

        # Stocks
        try:
            self.stocks = []
            self.load_stocks()
            logger.info(f"Loaded the Daily Stocks: {self.stocks}")
        except Exception as e:
            logger.error(f"Error while loading stocks: {e}")

        # Quick Analysis Agent
        try:
            self.quick_analysis_agent = Agent(
                name="Quick Analysis Agent",
                role="Stock Analysis Assistant",
                description="Generates a quick, data-driven analysis of the given stock to provide users with a concise market snapshot.",
                response_model=QuickAnalysisModel,
                model=self.model,
                tools=[
                    YFinanceTools(enable_all=True),
                    GoogleSearch(),
                ],
                instructions=[
                    "Generate a quick analysis report summarizing the current condition of the provided stock.",
                    "Follow these steps:",
                    "- Retrieve real-time stock data using Yahoo Finance.",
                    "- Search for relevant recent news articles via Google Search.",
                    "- Analyze and combine insights into a structured, high-level summary.",
                    "",
                    "**Output Requirements:**",
                    "- `symbol` (string): Stock ticker symbol.",
                    "- `price` (object):",
                    "   - `currency` (string): Currency in which the stock is traded.",
                    "   - `price` (float): Current stock price.",
                    "- `summary` (string): A well-structured stock analysis summary.",
                    "",
                    "Ensure that the output adheres strictly to the provided schema.",
                ],
                markdown=False,
                structured_outputs=True,
                tool_choice="auto",
            )
            logger.info("Analyst Agent Loaded")
        except Exception as e:
            logger.error("Error while loading Analyst Agent")

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

    def add_stocks(self, stock_symbols: list[str]):
        """
        Add a list of stock symbols to MongoDB for tracking.

        Args:
            stock_symbols (list[str]): List of stock symbols to add.
        """
        try:
            daily_stocks = self.db.get_collection("daily-stocks")
            result = daily_stocks.update_one(
                {"_id": "daily_stocks_list"},
                {
                    "$addToSet": {"stocks": {"$each": stock_symbols}},
                    "$set": {"last_update": dt.datetime.now(dt.timezone.utc)},
                },
                upsert=True,
            )

            if result.modified_count > 0:
                logger.info(f"Added stocks '{stock_symbols}' to MongoDB")
            else:
                logger.info(f"Stocks '{stock_symbols}' were already present")

        except Exception as e:
            logger.error(f"Error while adding stocks to MongoDB: {e}")

    def remove_stocks(self, stock_symbols: list[str]):
        """
        Remove a list of stock symbols from MongoDB for tracking.

        Args:
            stock_symbols (list[str]): List of stock symbols to remove.
        """
        try:
            daily_stocks = self.db.get_collection("daily-stocks")
            result = daily_stocks.update_one(
                {"_id": "daily_stocks_list"},
                {
                    "$pull": {"stocks": {"$in": stock_symbols}},
                    "$set": {"last_update": dt.datetime.now(dt.timezone.utc)},
                },
            )

            if result.modified_count > 0:
                logger.info(f"Removed stocks '{stock_symbols}' from MongoDB")
            else:
                logger.info(
                    f"No stocks removed (symbols may not have existed): {stock_symbols}"
                )

        except Exception as e:
            logger.error(f"Error while removing stocks from MongoDB: {e}")

    def perform_quick_analysis(self) -> List[dict]:
        """
        Perform a quick analysis for all monitored stocks.

        Returns:
            List[dict]: A list of quick analysis summaries for stocks.
        """
        summaries = []
        if len(self.stocks) > 0:
            for stock in self.stocks:
                try:
                    response = self.quick_analysis_agent.run(
                        f"Perform a quick analysis for the stock {stock}."
                    )
                    summaries.append(response.content.dict())
                    logger.info(f"Quick analysis for {stock} completed")
                except Exception as e:
                    logger.error(f"Error during quick analysis for {stock}: {e}")
            logger.info(f"Completed Quick Analysis for '{self.stocks}'")
            return summaries
        else:
            logger.warning(
                "No stocks found in Daily Stocks. Can't perform Quick Analysis"
            )
