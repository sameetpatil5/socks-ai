import streamlit as st

st.title("SocksAI Home")

navigation, details = st.columns([1, 2])

with navigation.container(border=True):
    st.subheader("Navigation")
    st.page_link("socks_home.py", label="Socks Home", icon="🏠")
    st.page_link("socks_chatbot.py", label="SocksAI Chatbot", icon="🤖")
    st.page_link("socks_chart.py", label="Socks Chart", icon="📈")
    st.page_link("daily_socks.py", label="Daily Socks", icon="📊")

with navigation.container(border=True):
    st.subheader("Contact")
    st.link_button(
        "LinkedIn",
        "https://www.linkedin.com/in/sameetpatil5/",
        type="tertiary",
    )
    st.link_button("GitHub", "https://github.com/sameetpatil5", type="tertiary")

with navigation.container(border=True):
    st.subheader("Support")
    st.link_button("Buy Me a Coffee", "", icon="☕️", disabled=True)


with details.container(border=True):
    about, how_to, privacy = st.tabs(["About SocksAI", "How to Use", "Privicy Note"])
    with about:
        st.markdown(
            """
        ### SocksAI: Your Stock Trading Assistant  

        **SocksAI** is a powerful stock trading assistant designed to help traders conduct research, analyze market trends, and make informed decisions—all in one place.  

        Developed and maintained by [Sameet Patil](https://www.github.com/sameetpatil5), SocksAI is built using the **PhiData/Ango Agentic Framework** to provide intelligent insights and enhance trading efficiency.  

        #### Features  
        - 🤖 **Chatbot** - Get stock-related insights and perform expert analysis using large language models (LLMs).  
        - 📈 **Stock Charts & Indicators** - Visualize stock charts with various technical indicators.  
        - 📊 **Daily Stock Insights** - Track market trends and get daily updates on your watchlisted stocks.  
        - 🗨️ **Train Models for Stock Prediction** - Develop and use AI models to predict stock trends.  

        #### What You Can Do with SocksAI  
        ✅ **Interact with the chatbot** to get expert stock market analysis and insights.  
        ✅ **Analyze stock charts** directly in the app, using a variety of technical indicators.  
        ✅ **Watchlist stocks** and receive **daily stock insights** to stay ahead of the market.  
        ✅ **Train AI models** for specific stocks and get predictive analytics on future trends.  
        ✅ **View stock predictions** directly within the stock charts interface.  

        SocksAI simplifies stock market analysis, making trading more data-driven and efficient. 🚀  
        """
        )

    with how_to:
        # st.subheader("How to Use")
        st.markdown(
            """
        ### How to Use SocksAI  

        SocksAI provides traders with a streamlined interface for market analysis, research, and stock predictions. Follow these steps to make the most of SocksAI:  

        #### Step 1: Add your Environment `KEYs`  
        Add your environment keys to access the SocksAI platform.
        Environment Keys:
        - Gemini API Key
        - MongoDB cluster URL
        - Qdrant URL
        - OpenAI API Key
        These keys are required to make the app work at your end rather than mine. Also none of these keys are stored in the app.  

        #### Step 2: Explore Features  
        Once inside, you can:  
        - **Chat with the AI Assistant** - Ask stock-related questions and get insights powered by AI.  
        - **Analyze Stock Charts** - Select a stock and visualize real-time charts with multiple indicators.  
        - **Get Daily Insights** - Track market trends and receive insights on your watchlisted stocks.  
        - **Train Prediction Models** - Select a stock, train a model, and generate AI-driven forecasts.  

        #### Step 3: Watchlist & Alerts  
        - Add stocks to your **watchlist** to track their performance over time.  
        - Get **daily insights** and alerts on your watchlisted stocks.  

        #### Step 4: Train AI Models for Stock Predictions  
        - Choose a stock, configure model parameters, and train an AI model to predict price movements.  
        - View **predictions directly on stock charts** to make data-driven decisions.  

        #### Step 5: Stay Updated  
        - Regularly check **market insights** and **AI-driven predictions** to refine your trading strategy.  
        - Keep an eye on real-time stock performance through the **SocksAI dashboard**.  

        SocksAI is designed to empower traders by simplifying stock analysis and enhancing decision-making with AI-driven insights. 🚀  
        """
        )

    with privacy:
        st.markdown(
            """
        ### Privacy Note  


        SocksAI is designed to be **privacy-friendly** and respects your data. Since this project was primarily built for exploratory purposes, I have not focused on a full-scale deployment. However, I still wanted to make it available to end users. This is why SocksAI requires you to provide your own API keys. That said, I have ensured that **your API keys, personal information, and trading data are never stored anywhere**.  


        #### 🔒 How SocksAI Handles Your Data  
        - **No data is stored** - Everything runs either **locally on your device** or through the **API services you provide**.  
        - **API keys are never saved** - They are only used during the session and not logged or retained.  
        - **No third-party tracking** - SocksAI does not send your data anywhere.  

        #### 🔍 Open-Source & Transparent  
        - SocksAI is **open-source**, meaning you can check the entire codebase on [GitHub](https://www.github.com/sameetpatil5).  
        - If you're concerned about privacy, you're free to **review the code yourself** and confirm that nothing is stored or misused.  

        #### ✅ Your Data, Your Control  
        - Since SocksAI does not store anything, **your data stays with you**.  
        - If you're using an API, it only connects when you run the app and does not save anything after you close it.  

        I've built SocksAI with a lot of passion and effort, and I'm committed to keeping it safe and secure. I understand the importance of privacy, so you can use it with confidence, knowing that **your information is safe and always under your control**. 🚀  
        """
        )
