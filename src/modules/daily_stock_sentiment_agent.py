import time
import datetime
from threading import Thread
from pymongo import MongoClient
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.googlesearch import GoogleSearch
from phi.tools.yfinance import YFinanceTools


class DailyStockSentimentAgent:
    def __init__(self, db_uri, db_name):
        # MongoDB setup
        self.client = MongoClient(db_uri)
        self.db = self.client[db_name]
        self.stocks = []
        self.running = False

        # Sentiment Agent
        self.sentiment_agent = Agent(
            name="Sentiment Agent",
            role="Search and interpret news articles.",
            model=Gemini(id="gemini-2.0-flash-exp"),
            tools=[GoogleSearch()],
            instructions=[
                f"Retrieve the latest news articles related to the provided stock, its sector, and any global events that might impact the stock or stock market.",
                "Follow these instructions:\n",
                "### **Scope of News Search**:\n",
                "1. **Stock-Specific News**:\n",
                "- Find news articles directly related to the provided stock\n",
                "2. **Sector News**:\n",
                "- Search for news relevant to the sector or industry the stock belongs to.\n",
                "3. **Global or Market-Wide News**:\n",
                "- Include any significant global or market-wide events that might impact the stock market as a whole or the specific stock.\n\n",
                "### **Output Requirements**:\n",
                "- **Number of Articles**: Provide 10 news articles in total, distributed across the categories above.\n",
                "- **Sentiment Analysis**:\n",
                "- Assign a sentiment score to each article on a scale of 1 (very negative) to 10 (very positive).\n",
                "- **Impact Assessment**:\n",
                "- Evaluate the potential impact of each article on the stock. Use a scale of 1 (low impact) to 10 (high impact).\n",
                "- **Summary**:\n",
                "- Provide a concise 2-3 sentence summary of each article.\n",
                "- Include the publication date and a direct source link.\n\n",
                "### **Formatting Instructions**:\n",
                "- Organize the data into a structured dictionary format suitable for MongoDB storage.\n",
                "- Ensure the following fields are included:\n",
                "- `symbol`: The stock ticker symbol.\n",
                "- `news`: A list of dictionaries, each representing an article with:\n",
                "- `title`: The title of the article.\n",
                "- `summary`: A brief summary of the article.\n",
                "- `sentiment_score`: Sentiment score (1-10).\n",
                "- `impact_score`: Impact score (1-10).\n",
                "- `source`: The source link of the article.\n",
                "- `publication_date`: The publication date of the article.\n",
                "- `timestamp`: The current UTC timestamp.\n\n",
                "### **Additional Notes**:\n",
                "- Ensure all numerical data is within appropriate ranges.\n",
                "- Filter out duplicate or irrelevant articles.\n",
                "- Focus on credible and up-to-date sources.\n",
            ],
            # instructions=[
            #     "Find relevant news articles for each company and analyze the sentiment.",
            #     "Provide sentiment scores from 1 (negative) to 10 (positive) with reasoning and sources.",
            #     "Cite your sources. Be specific and provide links.",
            # ],
            show_tool_calls=True,
            markdown=True,
        )

        # Finance Agent
        self.finance_agent = Agent(
            name="Finance Agent",
            role="Get financial data and interpret trends.",
            model=Gemini(id="gemini-2.0-flash-exp"),
            tools=[
                YFinanceTools(
                    stock_price=True, analyst_recommendations=True, company_info=True
                )
            ],
            instructions=[
                "Retrieve the latest financial data for the provided stock.",
                "Focus on real-time, short-term metrics that are critical for immediate analysis.",
                "Use the following properties:\n",
                "1. **Current Stock Performance**:\n",
                "- Fetch the latest stock price, percentage change, and volume.\n",
                "- Include key metrics like open, high, low, and close prices for the current trading session.\n\n",
                "2. **Analyst Recommendations**:\n",
                "- Provide the latest analyst recommendations and price targets.\n\n",
                "3. **Key Events**:\n",
                "- Highlight any recent events, earnings, or dividends scheduled for today.\n\n",
                "4. **News**:\n",
                "- Summarize the top 2-3 most recent news headlines related to this stock.\n\n",
                "**Formatting Instructions**:\n",
                "- Organize the data into a structured dictionary format suitable for MongoDB storage.\n",
                "- Ensure the data contains the following fields:\n",
                "    - `symbol`: The stock ticker symbol.\n",
                "    - `performance`: Key stock performance metrics (e.g., price, volume, percentage change).\n",
                "    - `analyst_insights`: Latest analyst recommendations and price targets.\n",
                "    - `events`: Recent or upcoming events (e.g., earnings, dividends).\n",
                "    - `news`: A brief summary of the most recent news headlines.\n\n",
                "Return the formatted data for storage. Ensure all numerical data is in appropriate units, and timestamps are in UTC.\n",
            ],
            # expected_output="",
            # instructions=[
            #     "Retrieve stock prices, analyst recommendations, and key financial data.",
            #     "Focus on trends and present the data in tables with key insights.",
            # ],
            show_tool_calls=True,
            markdown=True,
        )

        # Analyst Agent
        self.analyst_agent = Agent(
            name="Analyst Agent",
            role="Ensure thoroughness and draw conclusions.",
            model=Gemini(id="gemini-2.0-flash-exp"),
            instructions=[
                "Perform a detailed sentiment analysis for the provided stock based on the provided financial data and news articles from today.",
                "Follow these steps:\n",
                "1. **Financial Data Analysis**:\n",
                "- Analyze the provided stock data, including price trends, volume, and any other key metrics.\n",
                "- Highlight any significant changes or patterns observed during the day.\n",
                "- Summarize the overall market sentiment for the stock based on the financial data (e.g., bullish, bearish, or neutral).\n\n",
                "2. **News Sentiment Analysis**:\n",
                "- Review the following news articles for provided stock:\n",
                "- For each article:\n",
                "- Extract the key points and assess the sentiment (positive, neutral, or negative).\n",
                "- Provide a sentiment score between 1 (very negative) and 10 (very positive).\n",
                "- Cite the source and publication date for each article.\n\n",
                "3. **Overall Sentiment**:\n",
                "- Combine insights from the financial data and news sentiment analysis.\n",
                "- Assign a final sentiment score for the stock on a scale of 1 to 10, with justification.\n",
                "- Provide a brief summary explaining the key factors that influenced your final sentiment score.\n\n",
                "Ensure your analysis is comprehensive, well-structured, and includes references to all data points used. Present the results in a clear and concise manner.\n",
            ],
            # instructions=[
            #     "Check outputs for accuracy and completeness.",
            #     "Synthesize data to provide a final sentiment score (1-10) with justification.",
            # ],
            show_tool_calls=True,
            markdown=True,
        )

    def add_stock(self, stock_symbol):
        if stock_symbol not in self.stocks:
            self.stocks.append(stock_symbol)
            print(f"Added stock: {stock_symbol}")

    def fetch_stock_data(self):
        while self.running:
            for stock in self.stocks:
                data = self.finance_agent.run(
                    f"Retrieve the latest financial data for the stock ticker {stock}."
                )
                self.db.stock_data.insert_one(
                    {
                        "symbol": stock,
                        "data": data,
                        "timestamp": datetime.timezone.utc(),
                    }
                )
                print(f"Stock data fetched for {stock} and stored in MongoDB.")
            time.sleep(300)  # 5 minutes

    def fetch_stock_news(self):
        while self.running:
            for stock in self.stocks:
                news = self.sentiment_agent.run(
                    f"""
                    Retrieve the latest news articles related to the stock ticker {stock}, its sector, and any global events that might impact the stock or stock market. Follow these instructions:

                    ### **Scope of News Search**:
                    1. **Stock-Specific News**:
                        - Find news articles directly related to the stock {stock}.
                    2. **Sector News**:
                        - Search for news relevant to the sector or industry the stock belongs to.
                    3. **Global or Market-Wide News**:
                        - Include any significant global or market-wide events that might impact the stock market as a whole or the specific stock.

                    ### **Output Requirements**:
                    - **Number of Articles**: Provide 10 news articles in total, distributed across the categories above.
                    - **Sentiment Analysis**:
                        - Assign a sentiment score to each article on a scale of 1 (very negative) to 10 (very positive).
                    - **Impact Assessment**:
                        - Evaluate the potential impact of each article on the stock. Use a scale of 1 (low impact) to 10 (high impact).
                    - **Summary**:
                        - Provide a concise 2-3 sentence summary of each article.
                        - Include the publication date and a direct source link.

                    ### **Formatting Instructions**:
                    - Organize the data into a structured dictionary format suitable for MongoDB storage.
                    - Ensure the following fields are included:
                        - `symbol`: The stock ticker symbol.
                        - `news`: A list of dictionaries, each representing an article with:
                            - `title`: The title of the article.
                            - `summary`: A brief summary of the article.
                            - `sentiment_score`: Sentiment score (1-10).
                            - `impact_score`: Impact score (1-10).
                            - `source`: The source link of the article.
                            - `publication_date`: The publication date of the article.
                        - `timestamp`: The current UTC timestamp.

                    ### **Additional Notes**:
                    - Ensure all numerical data is within appropriate ranges.
                    - Filter out duplicate or irrelevant articles.
                    - Focus on credible and up-to-date sources.
                    """
                )
                self.db.stock_news.insert_one(
                    {
                        "symbol": stock,
                        "news": news,
                        "timestamp": datetime.timezone.utc(),
                    }
                )
                print(f"News articles fetched for {stock} and stored in MongoDB.")
            time.sleep(3600)  # 1 hour

    def perform_end_of_day_analysis(self):
        # Get today's date in UTC
        today = datetime.timezone.utc()
        start_of_day = datetime(today.year, today.month, today.day)
        end_of_day = start_of_day + datetime.timedelta(days=1)
        for stock in self.stocks:
            today_stock_data = list(
                self.db.stock_data.find(
                    {
                        "symbol": stock,
                        "timestamp": {"$gte": start_of_day, "$lt": end_of_day},
                    }
                )
            )

            # Query stock news for today
            today_stock_news = list(
                self.db.stock_news.find(
                    {
                        "symbol": stock,
                        "timestamp": {"$gte": start_of_day, "$lt": end_of_day},
                    }
                )
            )

            sentiment = self.analyst_agent.run(f"")

            # Store or display the analysis as needed
            self.db.daily_sentiment.insert_one(
                {
                    "symbol": stock,
                    "data": sentiment,
                    "timestamp": datetime.timezone.utc(),
                }
            )

    def start_agents(self):
        self.running = True
        Thread(target=self.fetch_stock_data, daemon=True).start()
        Thread(target=self.fetch_stock_news, daemon=True).start()

    def stop_agents(self):
        self.running = False
