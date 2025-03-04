# FindStockAgent Documentation

## Overview

The `FindStockAgent` class is designed to identify and validate stock ticker symbols based on user queries. It uses an AI-driven agent to find stock symbols and validate them using the `yfinance` library to ensure accuracy.

## Libraries and Tools Used

The following libraries and tools are utilized in the project:

- **logging**: For tracking operations and errors.
- **yfinance**: A library for retrieving stock data and validating stock symbols.
- **phi.agent.Agent**: AI agent for finding stock symbols.
- **phi.model.google.Gemini**: AI model used for searching stock symbols.
- **phi.tools.googlesearch.GoogleSearch**: Tool for fetching stock symbols via Google search.
- **phi.tools.yfinance.YFinanceTools**: Tool that interacts with `yfinance` for stock data retrieval.
- **ast**: Used for safely parsing stock symbols.
- **models.models.StockSymbol**: Model that defines the structure for stock symbols.

## Class: `FindStockAgent`

### Constructor: `__init__(self, model: Gemini)`

Initializes the `FindStockAgent` with the AI model.

- **Arguments:**
  - `model` (`Gemini`): The AI model to use for stock symbol retrieval.

- **Attributes:**
  - `self.stock_agent`: AI agent configured to search for stock ticker symbols.
  - `self.model`: AI model used for analysis.

### Method: `get_stock(self, query: str) -> List[str]`

Uses the AI agent to find stock ticker symbols based on a user query.

- **Arguments:**
  - `query` (`str`): The query to search for stock symbols.

- **Returns:**
  - `List[str]`: A list of stock ticker symbols.

**Example:**

```python
agent = FindStockAgent(model=Gemini(id="gemini-2.0-flash-exp"))
symbols = agent.get_stock("Tesla")
print(symbols)  # Example output: ['TSLA']
```

### Method: `is_valid_stock(self, symbol: str) -> bool`

Validates a stock symbol using the `yfinance` library.

- **Arguments:**
  - `symbol` (`str`): The stock ticker symbol (e.g., "AAPL", "GOOG").

- **Returns:**
  - `bool`: `True` if the symbol is valid, otherwise `False`.

**Example:**

```python
agent = FindStockAgent(model=Gemini(id="gemini-2.0-flash-exp"))
valid = agent.is_valid_stock("AAPL")
print(valid)  # Example output: True
```

### Method: `find_stock(self, query: str) -> List[str]`

Finds stock ticker symbols based on a user query. If the query is already a valid stock ticker, it returns the symbol directly. Otherwise, it searches for stock symbols.

- **Arguments:**
  - `query` (`str`): The user query to search for stock ticker symbols.

- **Returns:**
  - `List[str]`: A list of valid stock ticker symbols.

**Example:**

```python
agent = FindStockAgent(model=Gemini(id="gemini-2.0-flash-exp"))
symbols = agent.find_stock("Tesla")
print(symbols)  # Example output: ['TSLA']
```

## Logging

The class uses the `logging` module to log query attempts, errors, and validation status of stock symbols.

## Error Handling

- If stock symbols cannot be parsed correctly, an error is logged.
- If `yfinance` fails to validate a symbol, it falls back on the AI agent to find alternative symbols.

## Example Usage

```python
# Create an instance of FindStockAgent
agent = FindStockAgent(model=Gemini(id="gemini-2.0-flash-exp"))

# Search for a stock symbol
query = "Tesla"
symbols = agent.find_stock(query)
print(symbols)  # Output: ['TSLA']

# Validate a stock symbol
valid = agent.is_valid_stock("TSLA")
print(valid)  # Output: True
```

## Conclusion

The `FindStockAgent` class provides an AI-powered solution for finding and validating stock ticker symbols efficiently. By integrating `yfinance` and AI search tools, it ensures accurate and reliable stock symbol identification.
