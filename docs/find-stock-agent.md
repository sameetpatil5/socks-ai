# FindStockAgent Documentation

## Overview

`FindStockAgent` is a class that helps identify and validate stock ticker symbols based on user queries. It uses an AI agent to process the query and find the relevant stock ticker symbols. The class also validates the stock symbol using the `yfinance` library to ensure the accuracy of the result.

## Dependencies

- `logging`: Provides logging functionality to track operations and errors.
- `yfinance`: A library to retrieve stock data and validate stock symbols.
- `phi.agent.Agent`: AI agent used to identify stock symbols.
- `phi.model.google.Gemini`: A model used by the agent to search for stock symbols.
- `phi.tools.googlesearch.GoogleSearch`: A tool for searching stock symbols using Google.
- `phi.tools.yfinance.YFinanceTools`: A tool that interacts with `yfinance` to retrieve stock data.
- `ast`: Used to safely parse returned stock symbols.
- `.models.models.StockSymbol`: A model that defines the structure for stock symbols.

## Class: `FindStockAgent`

### Constructor: `__init__(self)`

The constructor initializes the `FindStockAgent` class with the following components:

- `self.stock`: A placeholder for the stock symbol.
- `self.stock_agent`: An instance of the `Agent` class configured to search for stock ticker symbols.
- `self.stock_agent` is configured with:
  - Name: "Stock Symbol Finder"
  - Role: "Identify the exact stock ticker symbol based on the user's query."
  - Description: "Search for the exact stock ticker symbol based on the user's query."
  - Response Model: `StockSymbol`
  - Model: `Gemini(id="gemini-2.0-flash-exp")`
  - Tools: `YFinanceTools()` and `GoogleSearch()`
  - Instructions: A set of instructions for the agent to follow when processing the query.
  - Markdown: `False`
  - Structured Outputs: `True`
  - Tool Choice: `"auto"`

### Method: `get_stock(self, query: str) -> str`

Description

Uses the AI agent to find stock ticker symbols based on the user's query.

Arguments

- `query` (str): The user's query to search for stock ticker symbols.

Returns

- `str`: The stock ticker symbol(s) as a plain string or an empty list if no symbol is found.

Example

```python
agent = FindStockAgent()
symbols = agent.get_stock("Tesla")
print(symbols)  # Example output: "['TSLA']"
```

### Method: `is_valid_stock(self, symbol: str) -> bool`

Description

Validates whether a given stock symbol is valid using the `yfinance` library.

Arguments

- `symbol` (str): The stock symbol to validate (e.g., "AAPL", "GOOG").

Returns

- `bool`: `True` if the symbol is valid, `False` otherwise.

Example

```python
agent = FindStockAgent()
valid = agent.is_valid_stock("AAPL")
print(valid)  # Example output: True
```

### Method: `add_stock(self, query: str) -> List[str]`

Description

Adds a stock symbol to the list if valid or finds and returns potential symbols based on the user's query.

Arguments

- `query` (str): The stock symbol or user query to process.

Returns

- `List[str]`: A list of valid stock symbols.

Example

```python
agent = FindStockAgent()
symbols = agent.add_stock("Tesla")
print(symbols)  # Example output: ['TSLA']
```

## Logging

The class uses the `logging` module to log information about the queries and validation processes. The logging level is set to `INFO`, and the log format includes timestamps, log levels, and messages.

## Error Handling

In case of errors during the parsing of stock symbols or other issues, the class logs the errors with appropriate messages. For example, if there is an issue parsing the list of stock symbols, it will log the error with a message like:

```bash
Error parsing stock symbols: <error_message>
```

## Example Usage

```python
# Create an instance of the FindStockAgent
agent = FindStockAgent()

# Search for a stock symbol
query = "Tesla"
symbols = agent.add_stock(query)
print(symbols)  # Output: ['TSLA']

# Validate a stock symbol
valid = agent.is_valid_stock("TSLA")
print(valid)  # Output: True
```

## Conclusion

The `FindStockAgent` class provides an easy-to-use interface for finding and validating stock ticker symbols based on user queries. It integrates with an AI agent and the `yfinance` library to ensure accurate results and error-free processing.
