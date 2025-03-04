# SocksAI Development Plan

## Overview

SocksAI is a stock market analysis tool designed to provide traders and investors with real-time insights, sentiment analysis, technical indicators, and AI-driven recommendations. The system integrates multiple AI agents and real-time data sources to deliver actionable insights through a user-friendly Streamlit dashboard and a FastAPI-powered backend.

## Core Objectives

1. **Real-time Stock Data & Analysis**
   - Fetch and display stock prices, trends, and financial news.
   - Provide technical analysis with various indicators.

2. **AI-Driven Sentiment Analysis**
   - Analyze stock-related news articles.
   - Compute sentiment scores to evaluate market trends.

3. **User Interaction & Customization**
   - Allow users to track specific stocks.
   - Offer chatbot-based financial assistance.

4. **Automated Daily Insights**
   - Schedule periodic stock updates and sentiment analysis.
   - Send summarized reports on stock performance.

## Technology Stack

### **Frontend: Streamlit**

- Provides an interactive UI for stock tracking, charting, and chatbot interactions.
- Uses custom components for enhanced visualization (e.g., `st_horizontal.py`, `st_vertical_divider.py`).
- Integrates with backend APIs for real-time data retrieval.

### **Backend: FastAPI**

- Handles API requests for stock data, news, and sentiment analysis.
- Manages task scheduling for automated stock insights.
- Implements AI models for stock recommendations and analysis.

### **Database & Storage**

- **MongoDB**: Stores stock data, user interactions, and chatbot knowledge base.
- **Qdrant**: Vector database for AI-driven knowledge retrieval.

### **External APIs & Tools**

- **Yahoo Finance (yfinance)**: Fetches real-time stock market data.
- **Google Search**: Retrieves stock-related news articles.
- **Gemini AI**: AI-powered chatbot for answering stock queries.

## System Components

### **1. Stock Data & Sentiment Analysis**

- **DailyStockSentimentAgent**: Gathers stock data, processes financial news, and computes sentiment scores.
- **StockChartAgent**: Generates and visualizes stock charts with technical indicators.
- **FindStockAgent**: Identifies and validates stock ticker symbols.

### **2. AI-Powered Chatbot**

- **StockChatbotAgent**: Interacts with users, providing stock insights and answering financial queries.
- **Knowledge Management**: Allows users to add external knowledge sources (PDFs, websites, etc.).

### **3. Task Scheduling & Automation**

- **DailyStockSchedulerAgent**: Schedules and automates daily stock data retrieval and sentiment analysis.
- Uses **APScheduler** for periodic execution.

### **4. API & Routing**

- **FastAPI with CORS Middleware**: Enables communication between frontend and backend.
- **Routes Management**: Defines endpoints for stock data retrieval, scheduling, and chatbot interactions.

## User Interface Design

1. **Home Page** (`socks_home.py`)
   - Overview of SocksAI’s functionality.
   - Navigation to chatbot, charts, and daily insights.

2. **Stock Analysis Page** (`socks_chart.py`)
   - Allows users to enter stock symbols and view price trends.
   - Supports indicators like SMA, EMA, Bollinger Bands, and VWAP.

3. **Daily Insights Page** (`daily_socks.py`)
   - Displays sentiment scores and analysis for tracked stocks.
   - Allows users to start/stop the sentiment analysis scheduler.

4. **Chatbot Page** (`socks_chatbot.py`)
   - AI-powered chatbot for answering stock-related queries.
   - Supports adding external knowledge sources.

## Development Roadmap

1. **Phase 1: Backend & Core Features**
   - Implement stock data retrieval using yfinance.
   - Develop sentiment analysis and chatbot modules.
   - Create FastAPI routes for backend communication.

2. **Phase 2: Frontend & UI Development**
   - Build Streamlit dashboard with interactive charts and chatbot.
   - Implement custom UI components for enhanced visualization.

3. **Phase 3: Automation & Scheduling**
   - Integrate APScheduler for daily stock sentiment updates.
   - Optimize task execution and API performance.

4. **Phase 4: Optimization & Deployment**
   - Improve response times and scalability.
   - Deploy the system with MongoDB Atlas and Qdrant for storage.

## Conclusion

SocksAI is designed to provide intelligent stock analysis using real-time data and AI-driven insights. This development plan outlines the structure and objectives, ensuring a well-coordinated implementation of features for a seamless user experience.
