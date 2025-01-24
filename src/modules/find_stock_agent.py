import logging
import yfinance as yf
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.googlesearch import GoogleSearch
from phi.tools.yfinance import YFinanceTools
from typing import List
import ast
from .models.models import StockSymbol

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class FindStockAgent:
    """
    A class to find and validate stock ticker symbols based on user queries.

    This class uses an AI agent to identify stock symbols and validate them
    using the yfinance library.
    """

    def __init__(self):
        """
        Initialize the FindStockAgent with a stock agent configuration.
        """
        self.stock = None

        # Stock Agent configuration
        self.stock_agent = Agent(
            name="Stock Symbol Finder",
            role="Identify the exact stock ticker symbol based on the user's query.",
            description="This Agent will search for the exact stock ticker symbol based on the user's query.",
            response_model=StockSymbol,
            model=Gemini(id="gemini-2.0-flash-exp"),
            tools=[YFinanceTools(), GoogleSearch()],
            instructions=[
                "Your task is to search for the exact stock ticker symbol based on the user's query.",
                "Do not include any descriptions, explanations, or additional details in the output.",
                "If a single stock ticker is found, return only the ticker symbol as a plain string inside a list.",
                "If multiple stock tickers are found, return them as a list of plain strings.",
                "If no stock ticker is found, return an empty list.",
                "Avoid providing any additional commentary, context, or information in your response.",
            ],
            markdown=False,
            structured_outputs=True,
            tool_choice="auto",
        )

    def get_stock(self, query: str) -> str:
        """
        Use the stock agent to find stock ticker symbols based on a user query.

        Args:
        query (str): The user's query to search for stock ticker symbols.

        Returns:
        str: The stock ticker symbol(s) as a plain string or an empty list if none found.
        """
        logging.info(f"Querying stock symbols for: {query}")
        stock = self.stock_agent.run(
            f"Find the stock ticker symbol(s) for the following query: '{query}'.\n"
            "Only return the ticker symbol(s)."
        )
        return stock.content

    def is_valid_stock(self, symbol: str) -> bool:
        """
        Validates a stock symbol using the yfinance library.

        Args:
        symbol (str): The stock symbol to validate (e.g., "AAPL", "GOOG").

        Returns:
        bool: True if the symbol is valid, False otherwise.
        """
        logging.info(f"Validating stock symbol: {symbol}")
        ticker = yf.Ticker(symbol)
        return (
            True
            if "symbol" in ticker.info and ticker.info["symbol"] == symbol
            else False
        )

    def add_stock(self, query: str) -> List[str]:
        """
        Add a stock symbol to the list if valid, or find and return potential symbols.

        Args:
        query (str): The stock symbol or user query to process.

        Returns:
        List[str]: A list of valid stock symbols.
        """
        logging.info(f"Processing stock query: {query}")

        if self.is_valid_stock(query):
            logging.info(f"Stock symbol '{query}' is valid.")
            return [query.upper()]
        else:
            logging.info(
                f"Stock symbol '{query}' is not valid. Searching for alternatives."
            )
            stock_symbols = self.get_stock(query)
            try:
                # Parse the returned stock symbols into a list
                list_symbols = ast.literal_eval(stock_symbols.strip().splitlines()[0])
                logging.info(f"Found stock symbols: {list_symbols}")
                return list_symbols
            except (SyntaxError, ValueError) as e:
                logging.error(f"Error parsing stock symbols: {e}")
                return []
