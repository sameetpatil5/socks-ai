# Project Pre-Plan for SocksAI

## This document serves as a pre-plan to understand and proceed with the project outlining the possible tech stack and features

### **AI Name**: 🧦SocksAI

---

### **AI Agent Features**

1. **AI Agent Libraries**:
   - **LangGraph**: Used for the prediction and training pipeline, including further inference of selected stocks for prediction.
   - **PhiData**: Utilized for Multi-Agent stock sentiment analysis.
   - **Pydantic AI**: Powers the generative AI LLM for stock-related chatbot functionalities (RAG model).
   - **AutoGen**: Currently not being utilized but may be used incase other framework has performance issues.

---

### **Database**

- **Primary Database**: **MongoDB**
  - Efficient for storing both structured (e.g., stock prices) and unstructured (e.g., news articles, summaries) data.
  - Supports time-series collections for periodic stock data.

- **Secondary Database**: **AstraDB** (Optional)
  - Could be used for storing prediction results or for handling high-frequency time-series data. AstraDB may be used if scalability for time-series data becomes a significant requirement.

---

### **AI Models**

1. **Gemini**: For most of the sentiment analysis and LLM predictions and features requiring LLM.
2. **Ollama (Offline)**: Alternative to Gemini for local use.
3. **Prediction Models**: Prediction models for individual stocks trained on demand.

---

### **APIs/ Tools for the Agents**

1. **YFinance**: For fetching real-time stock data and historical prices.
2. **DuckDuckGo API**: For additional stock-related information.
3. **Brave API/ Google API**: Alternative to DuckDuckGo if the search results are not up to the mark.
4. **Google AI API**: For integrating Gemini LLM in the project.

---

### **Dashboard**

#### **Dashboard UI**

![SocksAI Dashboard UI/ Interface](/assests/socksai_dashboard.png)

#### **Dashboard Features**

1. **Display Stocks Graph**:
   - View current stock prices and historical data plotted in graph.
   - Ability to select the stocks which can be displayed.
   - Multiple Stocks graph overlapping for comparative analysis
   - Ability to display continuous predicted market graph for particular stocks
  
2. **Get Daily Stocks Insights**:
   - Get daily AI-driven sentiment analysis for selected stocks.
   - A periodic 5min Stock Price & 60min News related to the stock is stored and a analysis/ summary is presented or emailed the next day saving time.

3. **Stock Prediction**:
   - Train a model to predict the future performance of chosen stocks.
   - This model will fetch the required data, preprocess it and train the prediction model on demand.
   - This model can be later used to predict the stock prices and even plot graph with the current stock price.

4. **Chatbot for chat based Stock analysis**:
   - AI-powered chatbot with stock market understanding.
   - Can provide real-time insights, sentiment analysis, and crude-level predictions for stocked asked in the prompts.

---

### **Documentation Links**

1. [LangChain Introduction](https://python.langchain.com/docs/introduction/)
2. [LangGraph Tutorials](https://langchain-ai.github.io/langgraph/tutorials/introduction/)
3. [PhiData Documentation](https://docs.phidata.com/introduction)
4. [Pydantic AI Documentation](https://ai.pydantic.dev/)
5. [AutoGen Documentation](https://microsoft.github.io/autogen/stable/)
6. [MongoDB Python Driver (PyMongo)](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/)
7. [AstraDB Documentation](https://docs.datastax.com/en/astra-db-serverless/index.html)
8. [YFinance Documentation](https://ranaroussi.github.io/yfinance/index.html)
9. [DuckDuckGo Search Python](https://pypi.org/project/duckduckgo-search/) (Most agents already have this search method built-in)
10. [Google Search Python Library](https://python-googlesearch.readthedocs.io/en/latest/)
11. [Brave Search API Documentation](https://api.search.brave.com/app/documentation/web-search/get-started) (Alternative)

---

### **References**

1. **Indian Stock Market Analysis with YFinance**:
   - [LinkedIn Article](https://www.linkedin.com/pulse/master-indian-stock-market-analysis-pythons-yfinance-library-mujmule-wt0zf/)

2. **Pydantic AI for Chatbot Development**:
   - [YouTube Tutorial](https://www.youtube.com/watch?v=zf_D2Eafvk0)

3. **Stock Sentiment Analysis**:
   - [YouTube Tutorial](https://www.youtube.com/watch?v=4jA3bhBRM8M)

4. **AI Agents for Stocks**:
   - [DeepCharts GitHub Project](https://github.com/deepcharts/projects/tree/main)

5. **Stock Price Prediction Using Technical Indicators**:
   - [YouTube Tutorial](https://www.youtube.com/watch?v=gtk8k8G-_3k)

6. **Stock Prediction/Analysis Dashboard**:
   - [YouTube Tutorial](https://www.youtube.com/watch?v=N3ttsxgcP9I)

7. **Periodic Stock Analysis and Emailing**:
   - [YouTube Tutorial](https://www.youtube.com/watch?v=DDvdMEEaLTE)

---
