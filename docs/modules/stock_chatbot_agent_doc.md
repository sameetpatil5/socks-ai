# StockChatbotAgent Documentation

## Overview

The `StockChatbotAgent` is an AI-powered chatbot designed to provide real-time stock market insights, technical analysis, financial news retrieval, and trading strategy recommendations. It integrates vector databases, knowledge bases, and AI-driven memory management to enhance user experience.

## Libraries and Tools Used

The following libraries and tools are utilized in the project:

- **logging**: For logging system activity and errors.
- **pymongo**: For MongoDB interactions to store chat history and user data.
- **qdrant_client**: For managing vector embeddings in Qdrant.
- **phi.agent.Agent**: AI agent for chatbot interactions.
- **phi.model.google.Gemini**: AI model for chat-based responses.
- **phi.embedder.google.GeminiEmbedder**: AI embedding model for knowledge retrieval.
- **phi.vectordb.qdrant.Qdrant**: Vector database for efficient knowledge searches.
- **phi.memory components**: Memory management tools for personalized responses.
- **phi.knowledge sources**: PDF, website, and combined knowledge bases for market research.
- **phi.tools**: Includes OpenBBTools, Google Search, web crawling, and website data extraction.

## Configuration

### MongoDB Setup

The system connects to MongoDB for storing user interactions and chat history:

```python
self.client = MongoClient(storage_db_uri)
self.db = self.client["socksai-db"]
```

### Qdrant Setup

Qdrant is used as a vector database for storing and retrieving relevant stock market data:

```python
self.vector_db = Qdrant(
    embedder=self.embedder,
    collection="socksai-knowledge",
    url=qdrant_url,
    api_key=api_key,
)
```

### Knowledge Base Setup

The chatbot integrates multiple knowledge sources:

- **Website Knowledge Base**: Retrieves relevant stock and financial market data.
- **PDF Knowledge Base**: Extracts insights from financial reports.
- **PDF URL Knowledge Base**: Processes financial documents from external URLs.

These sources are combined into a `CombinedKnowledgeBase` for structured retrieval.

## Workflow

### 1. Chatbot Initialization

The chatbot initializes with an AI model, vector database, and knowledge management system.

### 2. User Query Processing

- The chatbot retrieves historical user interactions.
- It searches the knowledge base before using external tools.
- It uses real-time stock data, technical indicators, and sentiment analysis.

### 3. Real-Time Stock Insights

- Uses `OpenBBTools` to fetch stock price trends, analyst ratings, and company reports.
- Conducts technical and fundamental analysis.
- Provides trade recommendations based on risk assessments.

### 4. Personalized Memory and Learning

- Stores and retrieves user-specific preferences, tracked stocks, and past queries.
- Updates user memory after interactions to refine recommendations.

## Example Usage

### Initialize the Chatbot Agent

```python
agent = StockChatbotAgent(
    storage_db_uri="mongodb://localhost:27017",
    qdrant_url="http://localhost:6333",
    api_key="your-api-key",
    session_id="session_123",
    run_id="run_001",
    user_id="user_456",
    model=Gemini(id="gemini-2.0-flash-exp"),
    embedder=GeminiEmbedder(id="gemini-embedder"),
)
```

### Ask the Chatbot a Stock Market Question

```python
response = agent.chat("What is the current market trend for AAPL?")
for chunk in response:
    print(chunk.content)
```

### Add a Website to the Knowledge Base

```python
agent.add_knowledge("https://www.nasdaq.com", source_type="website")
```

## Conclusion

The `StockChatbotAgent` combines AI-driven chat capabilities, real-time stock market analysis, and knowledge management to provide traders and investors with valuable financial insights. It ensures informed decision-making through structured data retrieval, sentiment analysis, and personalized memory tracking.
