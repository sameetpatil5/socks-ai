import os
import logging
from pymongo import MongoClient
from qdrant_client import QdrantClient

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
from phi.knowledge.website import WebsiteKnowledgeBase, WebsiteReader
from phi.knowledge.pdf import PDFKnowledgeBase, PDFReader
from phi.knowledge.pdf import PDFUrlKnowledgeBase, PDFUrlReader

from phi.tools.openbb_tools import OpenBBTools
from phi.tools.googlesearch import GoogleSearch
from phi.tools.crawl4ai_tools import Crawl4aiTools
from phi.tools.website import WebsiteTools

# Configure logging
logger = logging.getLogger("app")


class StockChatbotAgent:
    """
    A class to manage stock market analysis and trading insights using AI agents.

    Attributes:
        - model (Gemini): The AI model used for chat responses.
        - embedder (GeminiEmbedder): The embedding model for vectorization.
        - client (MongoClient): MongoDB client instance.
        - db: MongoDB database instance.
        - vector_db (Qdrant): Qdrant Vector Database instance.
        - knowledge_base (CombinedKnowledgeBase): Combined knowledgebase with
                                                  [PDFUrlKnowledgeBase, WebsiteKnowledgeBase, PDFKnowledgeBase]
        - chat_agent (Agent): An AI agent for the chatbot functionality has custom memory, storage and knowledge.
    """

    def __init__(
        self,
        storage_db_uri: str,
        qdrant_url: str,
        api_key: str,
        session_id: str,
        run_id: str,
        user_id: str,
        model: Gemini,
        embedder: GeminiEmbedder,
    ):
        """
        Initializes the StockChatbotAgent with database connections, vector database setup,
        knowledge base, and chatbot model.

        Parameters:
        - storage_db_uri (str): MongoDB connection URI.
        - qdrant_url (str): Qdrant vector database URL.
        - api_key (str): API key for Qdrant authentication.
        - session_id (str): Unique session identifier.
        - run_id (str): Unique run identifier.
        - user_id (str): Unique user identifier.
        - model (Gemini): The AI model used for chat responses.
        - embedder (GeminiEmbedder): The embedding model for vectorization.
        """
        # Model setup
        try:
            self.model = model
            self.embedder = embedder
            logger.info("Model and Embedder Loaded")
        except:
            logger.error("Error while loading Model or Embedder")
        # MongoDB setup
        try:
            self.client = MongoClient(storage_db_uri)
            self.db = self.client["socksai-db"]
            logger.info("Connected to MongoDB successfully.")
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}")

        # Qdrant setup
        try:
            self.vector_db = Qdrant(
                embedder=self.embedder,
                collection="socksai-knowledge",
                url=qdrant_url,
                api_key=api_key,
            )
            logger.info("Connected to Qdrant successfully.")
        except Exception as e:
            logger.error(f"Error connecting to Qdrant: {e}")

        # Knowledge Setup
        try:
            url_pdf_knowledge_base = PDFUrlKnowledgeBase(
                urls=[],
                vector_db=self.vector_db,
                reader=PDFUrlReader(chunk=True),
            )

            website_knowledge_base = WebsiteKnowledgeBase(
                urls=[],
                vector_db=self.vector_db,
                max_links=1,
                max_depth=1,
                reader=WebsiteReader(chunk=True, max_links=1, max_depth=1),
            )

            local_pdf_knowledge_base = PDFKnowledgeBase(
                path="data/knowledge_pdfs",
                vector_db=self.vector_db,
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
            logger.info("Knowledge base successfully created")
        except Exception as e:
            logger.error(f"Error while making a knowledge base: {e}")

        try:
            self.chat_agent = Agent(
                name="Chatbot Agent",
                role="Advanced Stock Chatbot",
                description="This agent retrieves stock data, analyzes financial trends, searches the web for relevant news, extracts insights from reports, etc. It assists traders by providing market analysis, risk assessments, and strategy recommendations, helping them make informed buy/sell decisions.",
                instructions=[
                    "**Capabilities & Functionality:**",
                    "- Retrieve and analyze **real-time stock data** from trusted financial sources.",
                    "- Conduct **technical and fundamental analysis** to assess stock performance.",
                    "- Search the web for **relevant market news** and **extract insights** from company reports.",
                    "- Provide **trade signals** based on technical indicators, historical trends, and live market conditions.",
                    "- Assess **market sentiment** by analyzing news trends, stock movements, and macroeconomic factors.",
                    "- Offer **risk evaluations** before suggesting trade entries and exits.",
                    "- Help traders develop **customized trading strategies** based on market conditions and risk appetite.",
                    "- Support both **short-term trading** and **long-term investment strategies**.",
                    "- Maintain **user memory** to track stock preferences, trading habits, and personalized risk levels.",
                    "- Continuously monitor stock movements and **alert users about critical market changes**.",
                    "**Decision Workflow:**",
                    "1. **Memory & Context Awareness:** If the user references past interactions (e.g., 'let's continue'), check memory first.",
                    "2. **Knowledge Base Search:** If memory lacks relevant data, search the knowledge base before using external tools.",
                    "3. **Direct Response vs. Tool Usage:**",
                    "   - If an answer is **certain** and does not require external data, respond directly.",
                    "   - If additional validation is needed, use tools like Yahoo Finance, Google Search, or web crawling.",
                    "4. **Market Data Retrieval:** Fetch stock fundamentals, price targets, analyst ratings, and historical trends.",
                    "5. **News & Reports Analysis:** Extract relevant news articles, earnings call insights, and financial reports.",
                    "6. **Trade Strategy & Risk Assessment:** Recommend stop-loss, take-profit levels, and evaluate market risks.",
                    "7. **User Personalization:** Update memory with user preferences, risk tolerance, and frequently tracked stocks.",
                    "**Output Requirements:**",
                    "- Use **structured responses** with headings, bullet points, and spacing for readability.",
                    "- Provide **justifications** for trade recommendations with clear technical and fundamental analysis.",
                    "- Format responses in **Markdown** for better presentation.",
                    "- **Avoid speculation**—recommendations must be based on verifiable data sources.",
                    "- Clearly **highlight risks and potential market volatility** before suggesting trades.",
                ],
                guidelines=[
                    "**Best Practices & Constraints:**",
                    "- **Accuracy First:** Prioritize data from reliable financial APIs, stock exchanges, and reputable news sources.",
                    "- **No Overpromising:** Do not guarantee stock performance; provide insights based on data trends.",
                    "- **Explain Trade Signals Clearly:** Always justify buy/sell/hold decisions using technical indicators and fundamental data.",
                    "- **Risk Management:** Encourage users to set stop-loss and take-profit levels.",
                    "- **Market Awareness:** Inform users about upcoming economic events that may affect market movements.",
                    "- **Personalized Advice:** Tailor recommendations based on user trading preferences and risk tolerance.",
                ],
                model=self.model,
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
                        model=self.model,
                    ),
                    classifier=MemoryClassifier(
                        model=self.model,
                    ),
                    summarizer=MemorySummarizer(
                        model=self.model,
                    ),
                    create_user_memories=True,
                    update_user_memories_after_run=True,
                    create_session_summary=True,
                    update_session_summary_after_run=True,
                    updating_memory=True,
                ),
                knowledge_base=self.knowledge_base,
                tools=[
                    OpenBBTools(
                        provider="yfinance",
                        stock_price=True,
                        search_symbols=True,
                        company_news=True,
                        company_profile=True,
                        price_targets=True,
                    ),
                    Crawl4aiTools(max_length=None),
                    GoogleSearch(),
                    WebsiteTools(knowledge_base=website_knowledge_base),
                ],
                tool_choice="auto",
                prevent_hallucinations=True,
                add_chat_history_to_messages=True,
                num_history_responses=10,
                read_chat_history=True,
                search_knowledge=True,
                markdown=True,
            )

            self.chat_agent.knowledge.load(recreate=False, upsert=False)
            logger.info("Chatbot Agent Loaded")
        except Exception as e:
            logger.error(f"Error while loading Chatbot Agent: {e}")

    def chat(self, prompt: str):
        """
        Generates a response to the user's input using the AI model.

        Parameters:
        - prompt (str): The user's message or query.

        Yields:
        - str: The chatbot's response, streamed in chunks.
        """
        try:
            response = self.chat_agent.run(prompt, stream=True)

            for chunk in response:
                yield chunk.content + ""

            logger.info("Chatbot response generated")
        except Exception as e:
            logger.error(f"Error while getting a response from the Chat Agent: {e}")

    def add_knowledge(self, path_or_url: str, source_type: str = "website"):
        """
        Adds a document to the chatbot's knowledge base.

        Parameters:
        - path_or_url (str): The path or URL of the document to be added.
        - source_type (str): Type of source ('website', 'pdf_url', or 'local_pdf') (default: "website").
        """
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
                # PDFKnowledgeBase is at index 2
                pass
            else:
                logger.error(f"Unsupported source type: {source_type}")
                return

            self.knowledge_base.load(recreate=False, upsert=True)

            if source_type == "local_pdf":
                try:
                    if os.path.isfile(path_or_url):
                        os.remove(path_or_url)
                        logger.info(f"{path_or_url} has been deleted successfully.")
                    else:
                        logger.warning(f"{path_or_url} does not exist.")
                except:
                    logger.error(f"Error while remove the local pdf knowledge: {e}")

            logger.info(
                f"Document {path_or_url} added to {source_type} knowledge base."
            )

        except Exception as e:
            logger.error(f"Error adding document to knowledge base: {e}")
