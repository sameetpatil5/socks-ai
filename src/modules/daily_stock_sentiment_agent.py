import logging
from typing import List
from pymongo import MongoClient

from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.googlesearch import GoogleSearch
from phi.tools.yfinance import YFinanceTools

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
        quick_analysis_agent (Agent): Agent combining all other agents for quick summaries.
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

        # Stocks
        self.stocks = []

        # Quick Analysis Agent
        self.quick_analysis_agent = Agent(
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

    def perform_quick_analysis(self) -> List[dict]:
        """
        Perform a quick analysis for all monitored stocks.

        Returns:
            List[dict]: A list of quick analysis summaries for stocks.
        """
        summaries = []
        for stock in self.stocks:
            try:
                response = self.quick_analysis_agent.run(
                    f"Perform a quick analysis for the stock {stock}."
                )
                summaries.append(response.content.dict())
                logging.info(f"Quick analysis for {stock} completed.")
            except Exception as e:
                logging.error(f"Error during quick analysis for {stock}: {e}")
        return summaries
