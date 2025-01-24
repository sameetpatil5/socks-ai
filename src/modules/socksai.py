from daily_stock_sentiment_agent import DailyStockSentimentAgent
from dotenv import load_dotenv
import os

load_dotenv()

dss_agent = DailyStockSentimentAgent(os.environ.get("MONGO_URI"), os.environ.get("MONGO_DB"))

dss_agent.add_stock("ZOMATO.NS")

# response = dss_agent.perform_quick_analysis()

# dss_agent.fetch_stock_data()
# dss_agent.fetch_stock_news()
# print(response)
# print(response.content)

