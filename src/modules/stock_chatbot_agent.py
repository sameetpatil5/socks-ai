import os
import shutil
import logging
from typing import Optional
from rich.prompt import Prompt
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
from phi.tools.googlesearch import GoogleSearch


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()


class StockChatbotAgent:
    def __init__(
        self, storage_db_uri: str, storage_db_name: str, qdrant_url: str, api_key: str
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

    def socksai_agent(self, user: str = "user"):
        run_id: Optional[str] = None

        try:

            agent = Agent(
                name="Stock Chatbot Agent",
                role="Provide users with accurate financial data and analysis to assist in trade decisions.",
                model=Gemini(id="gemini-2.0-flash-exp"),
                description="This agent retrieves financial data, analyzes documents, searches the web, and assists users with stock-related queries.",
                run_id=run_id,
                user_id=user,
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
                        model=Gemini(id="gemini-2.0-flash-exp"),
                    ),
                    summarizer=MemorySummarizer(
                        model=Gemini(id="gemini-2.0-flash-exp"),
                    ),
                    create_user_memories=True,
                    update_user_memories_after_run=True,
                    create_session_summary=True,
                    update_session_summary_after_run=True,
                    updating_memory=True,
                ),
                knowledge_base=self.knowledge_base,
                tools=[
                    YFinanceTools(
                        stock_price=True,
                        analyst_recommendations=True,
                        company_info=True,
                    ),
                    GoogleSearch(),
                ],
                tool_choice="auto",
                show_tool_calls=True,
                debug_mode=False,
                add_chat_history_to_messages=True,
                num_history_responses=10,
                search_knowledge=True,
            )
            # agent.knowledge.load(recreate=False)

            logging.info("Stock Chatbot Agent initialized successfully.")
        except Exception as e:
            logging.error(f"Error initializing Agent: {e}")
            return

        if run_id is None:
            run_id = agent.run_id
            print(f"Started Run: {run_id}\n")
        else:
            print(f"Continuing Run: {run_id}\n")

        while True:
            try:
                message = Prompt.ask(f"[bold] :robot_face: {user} [/bold]")
                if message.lower() in ("exit", "bye"):
                    print("Exiting chatbot. Goodbye!")
                    break
                agent.print_response(message)
            except KeyboardInterrupt:
                print("\nChatbot interrupted. Exiting.")
                break
            except Exception as e:
                logging.error(f"Error during chatbot interaction: {e}")


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
                shutil.copy(path_or_url, dest_path)  # Copy PDF to the knowledge directory
                logging.info(f"Copied local PDF to {dest_path}")
            else:
                logging.error(f"Unsupported source type: {source_type}")
                return

            # Reload knowledge base after adding a document
            self.knowledge_base.load(recreate=False, upsert=True)
            logging.info(f"Document {path_or_url} added to {source_type} knowledge base.")

        except Exception as e:
            logging.error(f"Error adding document to knowledge base: {e}")


if __name__ == "__main__":
    # Define MongoDB and Qdrant credentials
    storage_db_uri = os.environ.get("MONGO_URI")
    storage_db_name = os.environ.get("MONGO_DB")
    qdrant_url = os.environ.get("QDRANT_URL")
    api_key = os.environ.get("QDRANT_API_KEY")

    if not all([storage_db_uri, storage_db_name, qdrant_url, api_key]):
        logging.error("Missing required environment variables.")
        exit(1)

    chatbot = StockChatbotAgent(storage_db_uri, storage_db_name, qdrant_url, api_key)
    chatbot.socksai_agent()
