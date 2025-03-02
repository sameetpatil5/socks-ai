from typing import List, Optional

from pydantic import BaseModel, Field


class News(BaseModel):
    """
    Represents a news article related to a stock.

    Attributes:
        title (str): The title of the article.
        summary (str): A brief summary of the article.
        sentiment_score (int): Sentiment score of the article (1-10).
        impact_score (int): Impact score of the article (1-10).
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
    Represents the price details of a stock.

    Attributes:
        currency (str): The currency symbol (e.g., USD, INR).
        price (float): The current price of the stock.
    """

    currency: str = Field(..., description="The currency symbol.")
    price: float = Field(..., description="The current price of the stock.")


class NewsModel(BaseModel):
    """
    Represents a collection of news articles related to a stock.

    Attributes:
        symbol (str): The stock ticker symbol.
        news (List[News]): A list of news articles.
    """

    symbol: str = Field(..., description="The stock ticker symbol.")
    news: List[News] = Field(..., description="A list of news articles.")


class StockModel(BaseModel):
    """
    Represents stock information including price, analyst insights, and performance.

    Attributes:
        symbol (str): The stock ticker symbol.
        price (Price): The current price of the stock with currency.
        analyst_insights (str): Analyst recommendations for the stock.
        performance (str): The performance metrics of the stock.
    """

    symbol: str = Field(..., description="The stock ticker symbol.")
    price: Price = Field(
        ..., description="The current price of the stock with currency."
    )
    analyst_insights: str = Field(
        ..., description="The analyst recommendations of the stock."
    )
    performance: str = Field(..., description="The performance metrics of the stock.")


class DailyStockAnalysisModel(BaseModel):
    """
    Represents the daily analysis of a stock.

    Attributes:
        symbol (str): The stock ticker symbol.
        closing_price (Price): The closing price of the stock with currency.
        analyst_insights (str): Analyst recommendations for the stock.
        performance (str): The performance metrics of the stock.
        sentiment_score (int): Sentiment score of the stock (1-10).
        sentiment_statement (str): Summary statement for the stock’s daily sentiment.
    """

    symbol: str = Field(..., description="The stock ticker symbol.")
    closing_price: Price = Field(
        ..., description="The closing price of the stock with currency."
    )
    analyst_insights: str = Field(
        ..., description="The analyst recommendations of the stock."
    )
    performance: str = Field(..., description="The performance metrics of the stock.")
    sentiment_score: int = Field(..., description="Sentiment score (1-10).")
    sentiment_statement: str = Field(
        ...,
        description="Overall summary for the stock for the day along with the sentiment.",
    )
