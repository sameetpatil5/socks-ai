from pydantic import BaseModel, Field
from typing import List, Optional


class Stock(BaseModel):
    """
    Represents a stock entity.

    Attributes:
        symbol (str): The stock ticker symbol.
    """

    symbol: str = Field(..., description="The stock ticker symbol.")


class StockSymbol(BaseModel):
    """
    Represents a collection of stock symbols.

    Attributes:
        stock_symbols (List[Stock]): A list of stock symbols.
    """

    stock_symbols: List[Stock] = Field(..., description="A list of stock symbols.")


class News(BaseModel):
    """
    Represents a news article related to stocks.

    Attributes:
        title (str): The title of the article.
        summary (str): A brief summary of the article.
        sentiment_score (int): Sentiment score (1-10).
        impact_score (int): Impact score (1-10).
        source (str): The source link of the article.
        publication_date (Optional[str]): The publication date in YYYY-MM-DD format.
    """

    title: str = Field(..., description="The title of the article.")
    summary: str = Field(..., description="A brief summary of the article.")
    sentiment_score: int = Field(..., description="Sentiment score (1-10).")
    impact_score: int = Field(..., description="Impact score (1-10).")
    source: str = Field(..., description="The source link of the article.")
    publication_date: Optional[str] = Field(
        None, description="The publication date of the article in YYYY-MM-DD format."
    )


class Price(BaseModel):
    """
    Represents the stock price along with its currency.

    Attributes:
        currency (str): The currency symbol (e.g., USD, INR).
        price (float): The current price of the stock.
    """

    currency: str = Field(..., description="The currency symbol.")
    price: float = Field(..., description="The current price of the stock.")


class NewsModel(BaseModel):
    """
    Represents stock-related news articles.

    Attributes:
        symbol (str): The stock ticker symbol.
        news (List[News]): A list of news articles.
    """

    symbol: str = Field(..., description="The stock ticker symbol.")
    news: List[News] = Field(..., description="A list of news articles.")


class StockModel(BaseModel):
    """
    Provides stock details including price, analyst insights, and performance metrics.

    Attributes:
        symbol (str): The stock ticker symbol.
        price (Price): The current stock price with currency details.
        analyst_insights (str): Analyst recommendations for the stock.
        performance (str): The stock's performance metrics.
    """

    symbol: str = Field(..., description="The stock ticker symbol.")
    price: Price = Field(
        ..., description="The current price of the stock with currency."
    )
    analyst_insights: str = Field(
        ..., description="The analyst recommendations of the stock."
    )
    performance: str = Field(..., description="The performance metrics of the stock.")


class QuickAnalysisModel(BaseModel):
    """
    Provides a quick stock analysis including price and a financial summary.

    Attributes:
        symbol (str): The stock ticker symbol.
        price (Price): The current stock price with currency details.
        summary (str): A summary of sentiment analysis and financial data for the stock.
    """

    symbol: str = Field(..., description="The stock ticker symbol.")
    price: Price = Field(
        ..., description="The current price of the stock with currency."
    )
    summary: str = Field(
        ...,
        description="A summary of the sentiment analysis and financial data for the stock.",
    )
