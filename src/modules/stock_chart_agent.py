import os
import tempfile
import logging
import datetime as dt
from typing import Tuple

import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.yfinance import YFinanceTools
from phi.tools.googlesearch import GoogleSearch

# Configure logger
logger = logging.getLogger("app")


class StockChartAgent:
    """
    A class for fetching stock data and plotting stock charts with indicators.

    Attributes:
        model (Gemini): The Gemini model used by the AI agent.
    """

    def __init__(self, model: Gemini):
        """
        Initializes the StockChartAgent with the given model.

        Args:
            model (Gemini): The Gemini model to use for the AI agent.
        """
        # Model setup
        try:
            self.model = model
            logger.info("Model Loaded")
        except Exception as e:
            logger.error(f"Error while loading model: {e}")

        self.stock_symbol: str = None
        self.period: str = None
        self.interval: str = None
        self.df: pd.DataFrame = None
        self.indicator_colors = {
            "SMA_20": "#00FF00",
            "EMA_20": "#FF0000",
            "BB_20": ["#0000FF", "#FF0000"],
            "VWAP": "#FFA500",
        }
        try:
            self.chart_agent = Agent(
                name="Chart Analysis Expert",
                role="Technical Stock Chart Analyst",
                description="This agent will analyse the stock charts to present a comprehensive AI analysis of the chart image.",
                model=self.model,
                tools=[YFinanceTools(enable_all=True), GoogleSearch()],
                instructions=[
                    "You are a Stock Trader specializing in Technical Analysis at a top financial institution.",
                    "**Analysis Guidelines:**",
                    "- Analyze the stock chart's technical indicators and provide a **Buy / Hold / Sell** recommendation.",
                    "- Base your recommendation **only** on the candlestick chart and the displayed technical indicators.",
                    "- Provide the recommendation first, followed by a well-structured detailed reasoning.",
                    "- Search or gather additional information to support your recommendation.",
                    "**Output Requirements:**",
                    "- Provide the analysis in properly formatted **Markdown format**.",
                    "- Use bullet points, headings, and spacing to ensure readability.",
                    "- Make sure to keep the analysis detailed but not redundant or too long.",
                    "- Structure the response as follows:",
                    "  - **Recommendation:** Buy / Hold / Sell",
                    "  - **Technical Indicators Observed:** (e.g., Moving Averages, RSI, MACD, etc.)",
                    "  - **Rationale:** A concise yet insightful explanation of the decision.",
                    "**Strict Constraints:**",
                    "- Do **not** include any speculative or external market data.",
                ],
                markdown=True,
                tool_choice="auto",
            )
            logger.info("Chart Agent Loaded")
        except Exception as e:
            logger.error("Error while loading Chart Agent")

    def get_start_end_dates(
        self, period: tuple[dt.date, dt.date] | dt.date
    ) -> tuple[dt.date | None, dt.date | None]:
        """
        Determines the start and end dates based on the provided period.

        Args:
            period (tuple[dt.date, dt.date] | dt.date): A tuple containing start and end dates, or a single date.

        Returns:
            tuple[dt.date | None, dt.date | None]: The extracted start and end dates.
        """
        try:
            logger.info("Checking 'period' instance...")
            if isinstance(period, tuple):
                if len(period) == 2:
                    start_date, end_date = period
                else:
                    return None, None
            elif isinstance(period, dt.date):
                start_date = period
                end_date = start_date
            else:
                return None, None
            logger.info("Valid 'period' instance")
            return start_date, end_date
        except Exception as e:
            logger.error(f"Error while checking 'period' instance: {e}")
            return None, None

    def get_chart_metrics(self, stock_symbol: str, period: str, interval: str):
        """
        Fetches stock data and calculates required indicators.

        Args:
            stock_symbol (str): The stock ticker symbol (e.g., "AAPL").
            period (str): The time period for historical data.
            interval (str): The interval for stock data points.
        """
        try:
            logger.info(
                f"Fetching data for {stock_symbol} with period {period} and interval {interval}"
            )
            self.stock_symbol = stock_symbol
            self.interval = interval
            self.start_date, self.end_date = self.get_start_end_dates(period)
            self.df = self.get_stock_data()
            self.add_indicators()
            logger.info(f"Successfully obtained chart metrics for '{stock_symbol}'")
        except Exception as e:
            logger.error(f"Error while fetching chart metrics: {e}")

    def get_stock_data(self) -> pd.DataFrame:
        """
        Fetches historical stock data from Yahoo Finance.

        Returns:
            pd.DataFrame: DataFrame containing historical stock data.
        """
        try:
            logger.info(f"Retrieving historical stock data for {self.stock_symbol}")
            stock = yf.Ticker(self.stock_symbol)
            df = stock.history(
                start=self.start_date, end=self.end_date, interval=self.interval
            )
            logger.info(f"Retrieved {len(df)} records for {self.stock_symbol}")
            return df
        except Exception as e:
            logger.error(f"Error while fetching stock Data: {e}")

    def add_indicators(self) -> None:
        """
        Calculates technical indicators such as SMA, EMA, Bollinger Bands, and VWAP.
        """
        try:
            if self.df is None or self.df.empty:
                logger.warning("Stock data is empty. Skipping indicator calculations.")
                return
            logger.info("Calculating data for indicators.")
            rolling_20 = self.df["Close"].rolling(window=20)
            self.df["SMA_20"] = rolling_20.mean()
            self.df["EMA_20"] = self.df["Close"].ewm(span=20, adjust=False).mean()
            self.df["BB_20_Upper"] = rolling_20.mean() + 2 * rolling_20.std()
            self.df["BB_20_Lower"] = rolling_20.mean() - 2 * rolling_20.std()
            self.df["VWAP"] = (self.df["Close"] * self.df["Volume"]).cumsum() / self.df[
                "Volume"
            ].cumsum()
            logger.info("Indicators data successfully fetched")
        except Exception as e:
            logger.error(f"Error while adding indicators: {e}")

    def plot_indicators(self, fig: go.Figure, indicator: str) -> None:
        """
        Plots a specific indicator on the stock chart.

        Args:
            fig (go.Figure): The Plotly figure to which the indicator will be added.
            indicator (str): The name of the indicator to plot.
        """
        try:
            if self.df is None or self.df.empty:
                logger.warning("Stock data is empty. Skipping indicator plot.")
                return
            if indicator not in self.df:
                logger.error(f"Indicator {indicator} not found.")
                return

            if indicator in self.df and indicator != "BB_20":
                fig.add_trace(
                    go.Scatter(
                        x=self.df.index,
                        y=self.df[indicator],
                        mode="lines",
                        name=indicator,
                        line=dict(color=self.indicator_colors[indicator]),
                    )
                )
            if indicator == "BB_20":
                fig.add_trace(
                    go.Scatter(
                        x=self.df.index,
                        y=self.df["BB_20_Upper"],
                        mode="lines",
                        name="BB_20_Upper",
                        line=dict(color=self.indicator_colors[indicator][0]),
                    )
                )
                fig.add_trace(
                    go.Scatter(
                        x=self.df.index,
                        y=self.df["BB_20_Lower"],
                        mode="lines",
                        name="BB_20_Lower",
                        line=dict(color=self.indicator_colors[indicator][1]),
                    )
                )
            logger.info(f"Indicator {indicator} plotted.")
        except Exception as e:
            logger.error(f"Error while plotting {indicator} on figure: {e}")

    def plot_stock_chart(self, chart_type: str, indicators: list) -> go.Figure:
        """
        Plots a stock chart with selected indicators using Plotly.

        Args:
            chart_type (str): Type of chart - "candlestick" or "line".
            indicators (list): List of indicators to include in the chart.

        Returns:
            go.Figure: A Plotly figure containing the stock chart.
        """
        try:
            logger.info(
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
                        line=dict(color="#FFA500"),
                    )
                )

            # Adding indicators
            for indicator in indicators:
                if indicator in self.df:
                    self.plot_indicators(fig, indicator)

            # Updating layout for better visibility
            fig.update_layout(
                title=f"Stock Chart for {self.stock_symbol}",
                xaxis_rangeslider_visible=False,
            )
            logger.info("Chart plotting completed.")
            return fig
        except Exception as e:
            logger.error(f"Error while plotting chart: {e}")

    def plot_chart(
        self,
        stock_symbol: str,
        period: Tuple[dt.date, dt.date] = (
            dt.date.today() - dt.timedelta(days=1),
            dt.date.today(),
        ),
        interval: str = "5m",
        chart_type: str = "candlestick",
        indicators: list = ["SMA_20", "EMA_20"],
    ) -> go.Figure:
        """
        Fetches stock data and plots a chart with selected indicators.

        Args:
            stock_symbol (str): The stock ticker symbol (e.g., "AAPL").
            period (Tuple[dt.date, dt.date], optional): The time period for historical data (default: last 1 day).
            interval (str, optional): The interval for stock data points (default: "5m").
            chart_type (str, optional): Type of chart - "candlestick" or "line" (default: "candlestick").
            indicators (list, optional): List of indicators to include in the chart (default: ["SMA_20", "EMA_20"]).

        Returns:
            go.Figure: A Plotly figure containing the stock chart.
        """
        logger.info(f"Generating chart for {stock_symbol}")
        self.get_chart_metrics(stock_symbol, period, interval)
        fig = self.plot_stock_chart(chart_type, indicators)
        return fig

    def analyze_plot(self, fig: go.Figure):
        """
        Analyzes the given stock chart using an AI agent.

        Args:
            fig (go.Figure): The Plotly figure representing the stock chart.

        Yields:
            str: Analysis output generated by the AI agent.
        """
        temp_dir = "/data/chart_images"
        try:
            os.makedirs(temp_dir, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                suffix=".png", dir=temp_dir, delete=False
            ) as tmpfile:
                tmpfile_path = tmpfile.name
            logger.info("Temporary file successfully created")
        except Exception as e:
            logger.error("Error while creating a temporary file")

        try:
            fig.write_image(tmpfile_path)
            logger.info("Plotly Figure converted to image")

            response = self.chart_agent.run(
                f"You have been provided the Stock Chart of {self.stock_symbol} from {self.start_date} to {self.end_date}",
                images=[tmpfile_path],
                stream=True,
            )

            logger.info("Response recieved from the Agent")

            for chunk in response:
                yield chunk.content + ""

        except Exception as e:
            logger.error(f"Error while generating chart Analysis report: {e}")

        finally:
            try:
                os.remove(tmpfile_path)
                logger.info(f"Temporary file {tmpfile_path} removed successfully")
            except Exception as e:
                logger.error(f"Error removing temporary file: {e}")
