# App Models Documentation

## Overview

The `models.py` file defines the data models used across the `SocksAI` Streamlit application. These models ensure structured data representation for stock symbols, stock prices, news articles, and financial analysis.

## Libraries and Tools Used

The following libraries and tools are utilized in the project:

- **pydantic**: Used for data validation and model serialization.
- **typing**: Provides type hints for optional and list-based attributes.

## Models

### 1. `Stock`

Represents a stock entity.

```python
class Stock(BaseModel):
    symbol: str = Field(..., description="The stock ticker symbol.")
```

### 2. `StockSymbol`

Represents a collection of stock symbols.

```python
class StockSymbol(BaseModel):
    stock_symbols: List[Stock] = Field(..., description="A list of stock symbols.")
```

### 3. `Price`

Represents the stock price along with its currency.

```python
class Price(BaseModel):
    currency: str = Field(..., description="The currency symbol.")
    price: float = Field(..., description="The current price of the stock.")
```

### 4. `News`

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

### 5. `NewsModel`

Represents stock-related news articles.

```python
class NewsModel(BaseModel):
    symbol: str = Field(..., description="The stock ticker symbol.")
    news: List[News] = Field(..., description="A list of news articles.")
```

### 6. `StockModel`

Provides stock details, including price, analyst insights, and performance metrics.

```python
class StockModel(BaseModel):
    symbol: str = Field(..., description="The stock ticker symbol.")
    price: Price = Field(..., description="The current price of the stock with currency.")
    analyst_insights: str = Field(..., description="Analyst recommendations for the stock.")
    performance: str = Field(..., description="The stock's performance metrics.")
```

### 7. `QuickAnalysisModel`

Provides a quick stock analysis, including price and financial summary.

```python
class QuickAnalysisModel(BaseModel):
    symbol: str = Field(..., description="The stock ticker symbol.")
    price: Price = Field(..., description="The current price of the stock with currency.")
    summary: str = Field(..., description="A summary of sentiment analysis and financial data for the stock.")
```

## Example Usage

### Creating a Stock Instance

```python
stock = Stock(symbol="AAPL")
```

### Creating a Stock Price Instance

```python
price = Price(currency="USD", price=150.25)
```

### Creating a Stock Analysis Instance

```python
analysis = QuickAnalysisModel(symbol="AAPL", price=price, summary="Positive outlook due to earnings growth.")
```

## Conclusion

The `models.py` file provides structured data representation for stocks, news, and financial insights, ensuring consistency across the `SocksAI` application.
