from pydantic import BaseModel, Field
from typing import List, Optional

class Stock(BaseModel):
    symbol: str = Field(..., description="The stock ticker symbol.")


class StockSymbol(BaseModel):
    stock_symbols: List[Stock] = Field(..., description="A list of Stock symbols.")


class News(BaseModel):
    title: str = Field(..., description="The title of the article.")
    summary: str = Field(..., description="A brief summary of the article.")
    sentiment_score: int = Field(..., description="Sentiment score (1-10).")
    impact_score: int = Field(..., description="Impact score (1-10).")
    source: str = Field(..., description="The source link of the article.")
    publication_date: Optional[str] = Field(
        None, description="The publication date of the article in YYYY-MM-DD format."
    )


class Price(BaseModel):
    currency: str = Field(..., description="The currency symbol.")
    price: float = Field(..., description="The current price of the stock.")


class NewsModel(BaseModel):
    symbol: str = Field(..., description="The stock ticker symbol.")
    news: List[News] = Field(..., description="A list of news articles.")


class StockModel(BaseModel):
    symbol: str = Field(..., description="The stock ticker symbol.")
    price: Price = Field(
        ..., description="The current price of the stock with currency."
    )
    analyst_insights: str = Field(
        ..., description="The analyst recommendations of the stock."
    )
    performance: str = Field(..., description="The performance metrics of the stock.")


class AnalystModel(BaseModel):
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


class TeamModel(BaseModel):
    symbol: str = Field(..., description="The stock ticker symbol.")
    price: Price = Field(
        ..., description="The current price of the stock with currency."
    )
    summary: str = Field(
        ...,
        description="A summary of the sentiment analysis and financial data for the stock.",
    )
