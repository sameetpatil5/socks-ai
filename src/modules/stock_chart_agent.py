import logging
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class StockChartAgent:
    """
    A class for fetching stock data and plotting stock charts with indicators.
    Supports Simple Moving Average (SMA) and Exponential Moving Average (EMA).
    """

    def __init__(self):
        self.stock_symbol: str = None
        self.period: str = None
        self.interval: str = None
        self.df: pd.DataFrame = None

    def get_chart_metrics(
        self, stock_symbol: str, period: str = "1mo", interval: str = "1d"
    ):
        """Fetches stock data and calculates required indicators."""
        logging.info(
            f"Fetching data for {stock_symbol} with period {period} and interval {interval}"
        )
        self.stock_symbol = stock_symbol
        self.period = period
        self.interval = interval
        self.df = self.get_stock_data()
        self.add_indicators()

    def get_stock_data(self) -> pd.DataFrame:
        """Fetches historical stock data from Yahoo Finance."""
        logging.info(f"Retrieving historical stock data for {self.stock_symbol}")
        stock = yf.Ticker(self.stock_symbol)
        df = stock.history(period=self.period, interval=self.interval)
        logging.info(f"Retrieved {len(df)} records for {self.stock_symbol}")
        return df

    def add_indicators(self) -> None:
        """Calculates technical indicators such as SMA and EMA."""
        if self.df is None or self.df.empty:
            logging.warning("Stock data is empty. Skipping indicator calculations.")
            return
        logging.info("Calculating SMA and EMA indicators.")
        self.df["SMA_50"] = self.df["Close"].rolling(window=50).mean()
        self.df["EMA_20"] = self.df["Close"].ewm(span=20, adjust=False).mean()

    def plot_stock_chart(
        self, chart_type: str = "candlestick", indicators: list = ["SMA_50", "EMA_20"]
    ) -> go.Figure:
        """Plots stock chart with selected indicators using Plotly."""
        logging.info(
            f"Plotting {chart_type} chart for {self.stock_symbol} with indicators {indicators}"
        )
        fig = go.Figure()

        # Adding main stock price chart
        if chart_type.lower() == "candlestick":
            fig.add_trace(
                go.Candlestick(
                    x=self.df.index,
                    open=self.df["Open"],
                    high=self.df["High"],
                    low=self.df["Low"],
                    close=self.df["Close"],
                    name="Candlesticks",
                )
            )
        elif chart_type.lower() == "line":
            fig.add_trace(
                go.Scatter(
                    x=self.df.index,
                    y=self.df["Close"],
                    mode="lines",
                    name="Closing Price",
                    line=dict(color="#FFA500"),  # Orange for better contrast
                )
            )

        # Adding indicators
        for indicator in indicators:
            if indicator in self.df:
                color = "#00FF00" if indicator == "SMA_50" else "#FF0000"
                fig.add_trace(
                    go.Scatter(
                        x=self.df.index,
                        y=self.df[indicator],
                        mode="lines",
                        name=indicator,
                        line=dict(color=color),
                    )
                )

        # Updating layout for better visibility
        fig.update_layout(
            title=f"Stock Chart for {self.stock_symbol}",
            xaxis_rangeslider_visible=False,
        )
        logging.info("Chart plotting completed.")
        return fig

    def plot_prediction_chart(self) -> go.Figure:
        """Plots a demo prediction chart for training stocks.

        This function is under construction.
        """
        logging.info("Generating prediction chart (Demo mode).")
        df_pred = pd.DataFrame(
            {
                "Date": pd.date_range(start="2025-01-01", periods=30, freq="D"),
                "Predicted Price": [100 + (x**1.1) for x in range(30)],
            }
        )
        df_pred.set_index("Date", inplace=True)

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df_pred.index,
                y=df_pred["Predicted Price"],
                mode="lines",
                name="Predicted Price",
                line=dict(color="gray", dash="dash"),
            )
        )
        fig.update_layout(
            title="Prediction Chart (Under Construction)",
            xaxis_title="Date",
            yaxis_title="Price",
        )
        logging.info("Prediction chart generated.")
        return fig

    def plot_chart(
        self,
        stock_symbol: str,
        period: str = "1mo",
        interval: str = "1d",
        plot_type: str = "normal",
        chart_type: str = "candlestick",
        indicators: list = ["SMA_50", "EMA_20"],
    ) -> go.Figure:
        """
        Fetches stock data and plots a chart with selected indicators.

        Args:
            stock_symbol (str): The stock ticker symbol (e.g., "AAPL").
            period (str, optional): The time period for historical data (default: "1mo").
            interval (str, optional): The interval for stock data points (default: "1d").
            plot_type (str, optional): Type of plot - "normal" for stock chart, "prediction" for forecast (default: "normal").
            chart_type (str, optional): Type of chart - "candlestick" or "line" (default: "candlestick").
            indicators (list, optional): List of indicators to include in the chart (default: ["SMA_50", "EMA_20"]).

        Returns:
            go.Figure: A Plotly figure containing the stock chart.
        """
        logging.info(f"Generating chart for {stock_symbol} with type {plot_type}")
        self.get_chart_metrics(stock_symbol, period, interval)
        if plot_type == "normal":
            return self.plot_stock_chart(chart_type, indicators)
        else:
            return self.plot_prediction_chart()
