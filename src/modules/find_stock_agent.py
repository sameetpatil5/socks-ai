import ast
import logging
from typing import List

import yfinance as yf

from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.googlesearch import GoogleSearch
from phi.tools.yfinance import YFinanceTools

from .models.models import StockSymbol

# Configure logging
logger = logging.getLogger("app")


class FindStockAgent:
    """
    A class to find and validate stock ticker symbols based on user queries.

    Attributes:
        model (Gemini): The Gemini model used by the AI agent.
        stock_agent (Agent): The AI agent used to find stock symbols.
    """

    def __init__(self, model: Gemini):
        """
        Initializes the FindStockAgent with the given model.

        Args:
            model (Gemini): The Gemini model to use for the AI agent.

        """
        # Model setup
        try:
            self.model = model
            logger.info("Model Loaded")
        except Exception as e:
            logger.error(f"Error while loading model: {e}")

        # Stock Agent
        try:
            self.stock_agent = Agent(
                name="Stock Symbol Finder",
                role="Stock Ticker Identifier",
                description="Finds the exact stock ticker symbol based on the user's query.",
                response_model=StockSymbol,
                model=self.model,
                tools=[YFinanceTools(), GoogleSearch()],
                instructions=[
                    "Identify the correct stock ticker symbol based on the user's query.",
                    "Search on Google for the appropriate stock ticker symbol.",
                    "Validate the stock ticker symbol using yfinance.",
                    "**Response Guidelines:**",
                    "- If a single ticker is found, return it as a plain string inside a list.",
                    "- If multiple tickers are found, return them as a list of plain strings.",
                    "- If no ticker is found, return an empty list.",
                    "**Strict Constraints:**",
                    "- Do **not** include descriptions, explanations, or additional details.",
                    "- Do **not** provide any context, commentary, or extra information.",
                    "- Keep the response strictly formatted as per the schema.",
                    "**Output Requirements:**",
                    "- `stock_symbols` (List): A list of stock ticker symbols.",
                    "  - Each item in the list follows the structure:",
                    "    - `symbol` (str): The stock ticker symbol.",
                ],
                markdown=False,
                structured_outputs=True,
                tool_choice="auto",
            )
            logger.info("Stock Agent Loaded")
        except Exception as e:
            logger.error("Error while loading Stock Agent")

    def get_stock(self, query: str) -> List:
        """
        Use the stock agent to find stock ticker symbols based on a user query.

        Args:
        query (str): The user's query to search for stock ticker symbols.

        Returns:
        List[str]: List of valid stock ticker symbol(s) appropriate as per the query.
        """
        stocks = []
        try:
            logger.info(f"Querying stock symbols for: {query}")
            response = self.stock_agent.run(
                f"Find the stock ticker symbol(s) for the following query: '{query}'.\n"
                "Only return the ticker symbol(s)."
            )
            stocks = response.content
            logger.info(f"Querying was successful with {len(stocks)}, {stocks} found")
        except Exception as e:
            logger.error(f"Error while Querying[{query}]: {e}")
        return stocks

    def is_valid_stock(self, symbol: str) -> bool:
        """
        Validates a stock symbol using the yfinance library.

        Args:
        symbol (str): The stock symbol to validate (e.g., "AAPL", "GOOG").

        Returns:
        bool: True if the symbol is valid, False otherwise.
        """
        try:
            logger.info(f"Validating stock symbol: {symbol}")
            ticker = yf.Ticker(symbol)
            if ticker is not None:
                return (
                    True
                    if "symbol" in ticker.info and ticker.info["symbol"] == symbol
                    else False
                )
            else:
                logger.warning("Invalid stock symbol. Will run a Query...")
                return False            
        except Exception as e:
            logger.error(f"Error while validing the stock symbol[{symbol}]: {e}")

    def find_stock(self, query: str) -> List[str]:
        """
        Find stock ticker symbols based on a user query.

        Args:
            query (str): The user's query to search for stock ticker symbols.

        Returns:
            List[str]: List of valid stock ticker symbol(s) appropriate as per the query.
        """
        try:
            logger.info(f"Processing stock query: {query}")

            if self.is_valid_stock(query):
                logger.info(f"Stock symbol '{query}' is valid.")
                return [query.upper()]
            else:
                logger.info(
                    f"Stock symbol '{query}' is not valid. Searching the stock with Stock Agent."
                )
                stock_symbols = self.get_stock(query)
                try:
                    list_symbols = ast.literal_eval(
                        stock_symbols.strip().splitlines()[0]
                    )
                    logger.info(f"Found stock symbols: {list_symbols}")
                    return list_symbols
                except (SyntaxError, ValueError) as e:
                    logger.error(f"Error parsing stock symbols: {e}")
                    return []
        except Exception as e:
            logger.error("Error while Processing the stock")
            return []
