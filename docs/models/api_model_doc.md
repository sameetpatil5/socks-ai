# API Models Documentation

## Overview

The `models.py` file defines the data models used in the `SocksAI` server modules. These models ensure structured data representation for stock symbols, prices, news articles, and daily stock analysis.

## Libraries and Tools Used

The following libraries and tools are utilized in the project:

- **pydantic**: Used for data validation and serialization.
- **typing**: Provides type hints for list-based and optional attributes.

## Models

### 1. `News`

Represents a stock-related news article.

```python
class News(BaseModel):
    title: str = Field(..., description="The title of the article.")
    summary: str = Field(..., description="A brief summary of the article.")
    sentiment_score: int = Field(..., description="Sentiment score (1-10).")
    impact_score: int = Field(..., description="Impact score (1-10).")
    source: str = Field(..., description="The source link of the article.")
    publication_date: Optional[str] = Field(None, description="Publication date (YYYY-MM-DD).")
```

### 2. `Price`

Represents the stock price along with its currency.

```python
class Price(BaseModel):
    currency: str = Field(..., description="The currency symbol.")
    price: float = Field(..., description="The current price of the stock.")
```

### 3. `NewsModel`

Represents stock-related news articles.

```python
class NewsModel(BaseModel):
    symbol: str = Field(..., description="The stock ticker symbol.")
    news: List[News] = Field(..., description="A list of news articles.")
```

### 4. `StockModel`

Represents stock details, including price, analyst insights, and performance metrics.

```python
class StockModel(BaseModel):
    symbol: str = Field(..., description="The stock ticker symbol.")
    price: Price = Field(..., description="The current price of the stock with currency.")
    analyst_insights: str = Field(..., description="Analyst recommendations for the stock.")
    performance: str = Field(..., description="The performance metrics of the stock.")
```

### 5. `DailyStockAnalysisModel`

Represents the daily sentiment analysis of a stock.

```python
class DailyStockAnalysisModel(BaseModel):
    symbol: str = Field(..., description="The stock ticker symbol.")
    closing_price: Price = Field(..., description="The closing price of the stock with currency.")
    analyst_insights: str = Field(..., description="Analyst recommendations for the stock.")
    performance: str = Field(..., description="The performance metrics of the stock.")
    sentiment_score: int = Field(..., description="Sentiment score (1-10).")
    sentiment_statement: str = Field(..., description="Overall sentiment summary for the stock.")
```

## Example Usage

### Creating a Stock Price Instance

```python
price = Price(currency="USD", price=150.25)
```

### Creating a Stock Analysis Instance

```python
analysis = DailyStockAnalysisModel(
    symbol="AAPL",
    closing_price=price,
    analyst_insights="Strong Buy Recommendation",
    performance="Positive Growth in Q2",
    sentiment_score=8,
    sentiment_statement="Bullish trend due to strong earnings report."
)
```

## Conclusion

The `models.py` file in the server module ensures structured data representation for stock market insights, supporting API-driven analysis and sentiment evaluation.

