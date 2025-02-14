import os
import shutil
import logging
from pymongo import MongoClient
from qdrant_client import QdrantClient
from dotenv import load_dotenv

from phi.storage.agent.mongodb import MongoAgentStorage
from phi.vectordb.qdrant import Qdrant
from phi.model.google import Gemini
from phi.embedder.google import GeminiEmbedder
from phi.agent import Agent, AgentMemory, AgentKnowledge

from phi.memory.db.mongodb import MongoMemoryDb
from phi.memory.classifier import MemoryClassifier
from phi.memory.summarizer import MemorySummarizer
from phi.memory.manager import MemoryManager

from phi.knowledge.combined import CombinedKnowledgeBase
from phi.knowledge.website import WebsiteKnowledgeBase
from phi.knowledge.pdf import PDFKnowledgeBase, PDFReader
from phi.knowledge.pdf import PDFUrlKnowledgeBase, PDFUrlReader

from phi.tools.yfinance import YFinanceTools
from phi.tools.openbb_tools import OpenBBTools
from phi.tools.googlesearch import GoogleSearch
from phi.tools.crawl4ai_tools import Crawl4aiTools
from phi.tools.website import WebsiteTools
from phi.tools.python import PythonTools
from phi.tools.pandas import PandasTools


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()


class StockChatbotAgent:
    def __init__(
        self,
        storage_db_uri: str,
        storage_db_name: str,
        qdrant_url: str,
        api_key: str,
        session_id: str,
        run_id: str,
        user_id: str,
    ):
        try:
            # MongoDB setup
            self.client = MongoClient(storage_db_uri)
            self.db = self.client[storage_db_name]
            self.db.name
            logging.info("Connected to MongoDB successfully.")
        except Exception as e:
            logging.error(f"Error connecting to MongoDB: {e}")
            raise

        try:
            # Qdrant setup
            self.vector_db = Qdrant(
                embedder=GeminiEmbedder(api_key=os.environ.get("GOOGLE_API_KEY")),
                collection="socksai-knowledge",
                url=qdrant_url,
                api_key=api_key,
            )
            logging.info("Connected to Qdrant successfully.")
        except Exception as e:
            logging.error(f"Error connecting to Qdrant: {e}")
            raise

        try:
            # Knowledge Setup
            url_pdf_knowledge_base = PDFUrlKnowledgeBase(
                urls=[],
                vector_db=Qdrant(
                    embedder=GeminiEmbedder(api_key=os.environ.get("GOOGLE_API_KEY")),
                    collection="pdf-documents",
                    url=qdrant_url,
                    api_key=api_key,
                ),
                reader=PDFUrlReader(chunk=True),
            )

            website_knowledge_base = WebsiteKnowledgeBase(
                urls=[],
                max_links=10,
                vector_db=Qdrant(
                    embedder=GeminiEmbedder(api_key=os.environ.get("GOOGLE_API_KEY")),
                    collection="website-documents",
                    url=qdrant_url,
                    api_key=api_key,
                ),
            )

            local_pdf_knowledge_base = PDFKnowledgeBase(
                path="data/knowledge_pdfs",
                vector_db=Qdrant(
                    embedder=GeminiEmbedder(api_key=os.environ.get("GOOGLE_API_KEY")),
                    collection="pdf-documents",
                    url=qdrant_url,
                    api_key=api_key,
                ),
                reader=PDFReader(chunk=True),
            )

            self.knowledge_base = CombinedKnowledgeBase(
                sources=[
                    url_pdf_knowledge_base,
                    website_knowledge_base,
                    local_pdf_knowledge_base,
                ],
                vector_db=self.vector_db,
            )
            logging.info("Knowledge base successfully created")
        except Exception as e:
            logging.error(f"Error while making a knowledge base: {e}")
            raise

        try:
            self.finance_agnet = Agent(
                name="Finance Agent",
                role="Fetch accurate stock data, analyze financial metrics, and provide trading insights.",
                description="This agent retrieves real-time and historical stock data, fundamental analysis, analyst recommendations, and company news to assist traders in making informed decisions.",
                instructions=[
                    "Fetch live stock prices when requested.",
                    "Retrieve and analyze historical stock performance data.",
                    "Provide analyst recommendations for given stocks.",
                    "Fetch and summarize relevant company news.",
                    "Assist with stock market research by analyzing fundamentals and financial metrics.",
                ],
                model=Gemini(id="gemini-1.5-flash"),
                tools=[
                    YFinanceTools(
                        stock_price=True,
                        analyst_recommendations=True,
                        company_info=True,
                        stock_fundamentals=True,
                        historical_prices=True,
                        company_news=True,
                    ),
                    OpenBBTools(),
                ],
                tool_choice="auto",
            )
            self.search_agent = Agent(
                name="Search Agent",
                role="Search for relevant news articles and events impacting specific stocks, sectors, or the overall market.",
                description="This agent finds and compiles news articles, economic updates, and global events that may influence stock movements.",
                instructions=[
                    "Perform web searches for stock-related news.",
                    "Identify macroeconomic and geopolitical events affecting the market.",
                    "Retrieve recent articles from financial news sources.",
                    "Provide summaries of relevant news impacting stocks or sectors.",
                    "Highlight potential risks and opportunities based on news trends.",
                ],
                model=Gemini(id="gemini-1.5-flash"),
                tools=[GoogleSearch()],
                tool_choice="auto",
            )
            self.web_agent = Agent(
                name="Web Agent",
                role="Retrieve, analyze, and summarize the contents of provided website URLs.",
                description="This agent extracts financial insights from web pages, news sites, and official company reports, helping traders make data-driven decisions.",
                instructions=[
                    "Fetch and analyze content from user-provided URLs.",
                    "Summarize financial reports, stock analysis, and earnings calls.",
                    "Extract key data points from financial news and investor updates.",
                    "Identify market sentiment based on content analysis.",
                    "Provide concise takeaways from lengthy financial documents.",
                ],
                model=Gemini(id="gemini-1.5-flash"),
                tools=[
                    Crawl4aiTools(),
                    WebsiteTools(knowledge_base=website_knowledge_base),
                ],
                tool_choice="auto",
            )
            self.chart_agent = Agent(
                name="Chart Agent",
                role="Generate and visualize stock charts based on user requests.",
                description="This agent plots stock performance charts using historical data, enabling users to analyze trends and patterns visually.",
                instructions=[
                    "Plot stock price charts based on historical data.",
                    "Generate technical indicators like moving averages and RSI.",
                    "Customize chart views based on timeframes (daily, weekly, etc.).",
                    "Overlay multiple stock charts for comparison.",
                    "Provide insights based on visualized data trends.",
                ],
                model=Gemini(id="gemini-1.5-flash"),
                tools=[
                    PythonTools(),
                    PandasTools(),
                ],
                tool_choice="auto",
            )

            self.chat_agent = Agent(
                name="SocksAI Chat Agent",
                role="An advanced AI trading assistant that leverages multiple specialized agents to provide real-time market insights, stock analysis, and trade recommendations.",
                description="This AI-powered trading assistant integrates multiple agents to fetch stock data, analyze financial trends, search the web for relevant news,\
                    extract insights from reports, and generate technical charts. It assists traders in making informed buy/sell decisions with real-time market analysis,risk assessments, and strategy suggestions.",
                instructions=[
                    "Analyze live stock market data and identify profitable trading opportunities.",
                    "Utilize the Finance Agent to fetch stock fundamentals, historical data, and analyst ratings.",
                    "Engage the Search Agent to gather breaking news and events impacting stock prices.",
                    "Use the Web Agent to extract insights from company reports, earnings calls, and market research.",
                    "Leverage the Chart Agent to generate technical analysis charts, including trend lines and indicators.",
                    "Provide real-time trade signals based on technical and fundamental analysis.",
                    "Assess market sentiment using news trends and stock movements.",
                    "Evaluate risk levels before suggesting entry and exit points for trades.",
                    "Assist users in building customized trading strategies based on market conditions.",
                    "Support both short-term day trading and long-term investment strategies.",
                ],
                guidelines=[
                    "Prioritize accuracy by sourcing data from reliable financial APIs, stock exchanges, and trusted news outlets.",
                    "Recommend trades based on a combination of technical indicators, historical performance, and live market trends.",
                    "Alert users about potential risks, market volatility, and upcoming economic events that may impact trading decisions.",
                    "Offer explanations for each trade recommendation, including reasoning based on technical and fundamental analysis.",
                    "Encourage risk management by suggesting stop-loss and take-profit levels.",
                    "Optimize trading strategies based on user preferences and risk tolerance.",
                    "Always provide users with a full breakdown of market conditions before confirming trade actions.",
                    "Continuously monitor stock movements and notify users about real-time changes that may affect their portfolio.",
                ],
                model=Gemini(id="gemini-2.0-flash-exp"),
                session_id=session_id,
                run_id=run_id,
                user_id=user_id,
                storage=MongoAgentStorage(
                    collection_name="agent_storage",
                    client=self.client,
                    db_name=self.db.name,
                ),
                memory=AgentMemory(
                    db=MongoMemoryDb(
                        collection_name="agent_memory",
                        client=self.client,
                        db_name=self.db.name,
                    ),
                    manager=MemoryManager(
                        model=Gemini(id="gemini-1.5-flash"),
                    ),
                    classifier=MemoryClassifier(
                        model=Gemini(id="gemini-1.5-flash"),
                    ),
                    summarizer=MemorySummarizer(
                        model=Gemini(id="gemini-1.5-flash"),
                    ),
                    create_user_memories=True,
                    update_user_memories_after_run=True,
                    create_session_summary=True,
                    update_session_summary_after_run=True,
                    updating_memory=True,
                ),
                knowledge_base=self.knowledge_base,
                team=[
                    self.finance_agnet,
                    self.search_agent,
                    self.web_agent,
                    # self.chart_agent,
                ],
                add_chat_history_to_messages=True,
                num_history_responses=10,
                search_knowledge=True,
                add_context=True,
                markdown=True,
            )
            self.chat_agent.knowledge.load(recreate=False)
            logging.info("Stock Chatbot Agent initialized successfully.")
        except Exception as e:
            logging.error(f"Error initializing Agent: {e}")
            return

    def chat(self, prompt):
        response = self.chat_agent.run(prompt, stream=True)

        for chunk in response:
            yield chunk.content + ""


    def add_knowledge(self, path_or_url: str, source_type: str = "website"):
        """Adds a document to the appropriate knowledge base."""
        try:
            if source_type == "website":
                self.knowledge_base.sources[1].urls.append(
                    path_or_url
                )  # WebsiteKnowledgeBase is at index 1
            elif source_type == "pdf_url":
                self.knowledge_base.sources[0].urls.append(
                    path_or_url
                )  # PDFUrlKnowledgeBase is at index 0
            elif source_type == "local_pdf":
                dest_path = os.path.join(
                    "data/knowledge_pdfs", os.path.basename(path_or_url)
                )
                shutil.copy(
                    path_or_url, dest_path
                )  # Copy PDF to the knowledge directory
                logging.info(f"Copied local PDF to {dest_path}")
            else:
                logging.error(f"Unsupported source type: {source_type}")
                return

            # Reload knowledge base after adding a document
            self.knowledge_base.load(recreate=False, upsert=True)
            logging.info(
                f"Document {path_or_url} added to {source_type} knowledge base."
            )

        except Exception as e:
            logging.error(f"Error adding document to knowledge base: {e}")
