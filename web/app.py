"""
Streamlit app for NewsSense.
"""
import os
import json
import datetime
import requests
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image


# API configuration
API_URL = "http://localhost:8000"  # Default FastAPI URL
FLASK_API_URL = "http://localhost:5000"  # Default Flask API URL

# Add offline mode flag
OFFLINE_MODE = False  # Set to True to use mock data instead of API calls

# Check if we need to switch to offline mode
if 'switch_to_offline' in st.session_state and st.session_state.switch_to_offline:
    OFFLINE_MODE = True
    st.session_state.switch_to_offline = False

# Page configuration
st.set_page_config(
    page_title="NewsSense",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown("""
<style>
    .main-title {
        font-size: 42px !important;
        color: #0E1117;
        text-align: center;
        margin-bottom: 0px;
    }
    .subtitle {
        font-size: 24px !important;
        color: #6E7681;
        text-align: center;
        margin-top: 0px;
        margin-bottom: 30px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #F2F3F5;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #E0F0FF !important;
        color: #0E66D0 !important;
    }
</style>
""", unsafe_allow_html=True)


# Helper functions
def format_date(date_str):
    """Format date string for display."""
    try:
        # Convert ISO format to datetime object
        dt = datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%d %b %Y, %H:%M")
    except:
        return date_str


def get_headlines(category=None, limit=20):
    """Get headlines from API."""
    try:
        params = {"limit": limit}
        if category:
            params["category"] = category
        
        response = requests.get(f"{API_URL}/news/headlines", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching headlines: {str(e)}")
        return []


def get_article(url):
    """Get article from API."""
    try:
        params = {"url": url}
        response = requests.get(f"{API_URL}/news/article", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching article: {str(e)}")
        return None


def search_stocks(query, limit=10):
    """Search stocks using API."""
    try:
        params = {"query": query, "limit": limit}
        response = requests.get(f"{API_URL}/stocks/search", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error searching stocks: {str(e)}")
        return []


def search_mutual_funds(query, limit=10):
    """Search mutual funds using API."""
    try:
        params = {"query": query, "limit": limit}
        response = requests.get(f"{API_URL}/mutualfunds/search", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error searching mutual funds: {str(e)}")
        return []


def answer_question(question):
    """Get answer to question from API."""
    if OFFLINE_MODE:
        # Return mock data in offline mode
        return {
            "question": question,
            "answer": "This is a mock response in offline mode. In actual deployment, this would be answered using financial news analysis.",
            "sources": [
                {
                    "title": "Sample Article 1",
                    "source": "Offline Mode",
                    "date": datetime.datetime.now().isoformat()
                }
            ],
            "is_simulated": True
        }
    
    try:
        data = {"question": question}
        response = requests.post(f"{API_URL}/qa/question", json=data, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {
            "question": question,
            "answer": "Unable to connect to the FastAPI backend. Please check if the service is running.",
            "sources": [],
            "is_simulated": True,
            "error": "connection_error"
        }
    except Exception as e:
        st.error(f"Error answering question: {str(e)}")
        return None


def get_stock_news(symbol):
    """Get news related to a specific stock symbol."""
    if OFFLINE_MODE:
        # Return mock data in offline mode
        return {
            "symbol": symbol,
            "company_name": f"{symbol} Corporation",
            "news": [
                {
                    "title": f"{symbol} Reports Strong Quarterly Results",
                    "source": "Offline Mode News",
                    "date": datetime.datetime.now().isoformat(),
                    "content": "This is mock content for demonstration purposes."
                },
                {
                    "title": f"Analysts Upgrade {symbol} Stock Rating",
                    "source": "Offline Mode News",
                    "date": (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat(),
                    "content": "This is mock content for demonstration purposes."
                }
            ]
        }
    
    try:
        params = {"symbol": symbol}
        response = requests.get(f"{FLASK_API_URL}/api/stock/news", params=params, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {
            "symbol": symbol,
            "company_name": symbol,
            "news": [],
            "error": "Unable to connect to the Flask API. Please check if the service is running."
        }
    except Exception as e:
        return {
            "symbol": symbol,
            "company_name": symbol,
            "news": [],
            "error": f"Error fetching stock news: {str(e)}"
        }


def analyze_stock(symbol, question=None):
    """Generate analysis for a stock based on recent news."""
    if OFFLINE_MODE:
        # Return mock data in offline mode
        return {
            "symbol": symbol,
            "company_name": f"{symbol} Corporation",
            "question": question if question else f"Why is {symbol} stock price changing recently?",
            "answer": f"This is a mock analysis of {symbol} in offline mode. In actual deployment, this would provide insights based on recent news and market data.",
            "sources": [
                {
                    "title": f"{symbol} Quarterly Earnings Call",
                    "source": "Offline Mode News",
                    "date": datetime.datetime.now().isoformat()
                }
            ],
            "is_simulated": True
        }
    
    try:
        data = {
            "symbol": symbol,
            "question": question if question else f"Why is {symbol} stock price changing recently?"
        }
        response = requests.post(f"{FLASK_API_URL}/api/stock/analysis", json=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {
            "symbol": symbol,
            "company_name": symbol,
            "question": question if question else f"Why is {symbol} stock price changing recently?",
            "answer": "Unable to connect to the Flask API. Please check if the service is running.",
            "sources": [],
            "is_simulated": True,
            "error": "connection_error"
        }
    except Exception as e:
        return {
            "symbol": symbol,
            "company_name": symbol,
            "question": question if question else f"Why is {symbol} stock price changing recently?",
            "answer": f"Error generating analysis: {str(e)}",
            "sources": [],
            "is_simulated": True,
            "error": "api_error"
        }


# Sidebar settings
with st.sidebar:
    st.title("NewsSense")
    
    # Show offline mode banner if enabled
    if OFFLINE_MODE:
        st.warning("⚠️ OFFLINE MODE")
        st.info("Running with simulated data. No API connections required.")
    
    st.subheader("Settings")
    
    # Only show API settings if not in offline mode
    if not OFFLINE_MODE:
        # Placeholder for API connection
        api_url = st.text_input("FastAPI URL", value=API_URL)
        flask_api_url = st.text_input("Flask API URL", value=FLASK_API_URL)
        
        # Settings saved in session state
        if "api_url" not in st.session_state:
            st.session_state.api_url = api_url
        elif st.session_state.api_url != api_url:
            st.session_state.api_url = api_url
            API_URL = api_url
            
        if "flask_api_url" not in st.session_state:
            st.session_state.flask_api_url = flask_api_url
        elif st.session_state.flask_api_url != flask_api_url:
            st.session_state.flask_api_url = flask_api_url
            FLASK_API_URL = flask_api_url
        
        st.divider()
    
    # About section
    st.subheader("About")
    st.markdown("""
    NewsSense helps investors understand why their investments are up or down by connecting financial news to market movements.
    
    Built for the MyFi Hackathon Challenge.
    """)
    
    # Only show API status if not in offline mode
    if not OFFLINE_MODE:
        st.divider()
        
        # API status indicator
        fastapi_status = "Unavailable"
        flask_status = "Unavailable"
        
        try:
            response = requests.get(f"{API_URL}", timeout=2)
            if response.status_code == 200:
                fastapi_status = "Connected"
        except:
            pass
            
        try:
            response = requests.get(f"{FLASK_API_URL}", timeout=2)
            if response.status_code == 200:
                flask_status = "Connected"
        except:
            pass
        
        st.subheader("API Status")
        col1, col2 = st.columns(2)
        with col1:
            if fastapi_status == "Connected":
                st.success("FastAPI: ✓")
            else:
                st.error("FastAPI: ✗")
        
        with col2:
            if flask_status == "Connected":
                st.success("Flask: ✓")
            else:
                st.error("Flask: ✗")
                
        if fastapi_status != "Connected" or flask_status != "Connected":
            st.warning("Some API services are not available. Some features may not work properly.")
            st.info("Make sure all services are running with `python start.py`")
            
            # Add option to run in offline mode
            if st.button("Switch to Offline Mode"):
                st.session_state.switch_to_offline = True
                st.rerun()


# Main app
st.markdown("<h1 class='main-title'>NewsSense</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Why Is My Investment Down?</p>", unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["💬 Ask", "🔍 Stock Lookup", "📰 News", "📈 Stocks", "📊 Mutual Funds"])

# Tab 1: Ask Questions
with tab1:
    st.header("Ask about your investments")
    
    question = st.text_input("Enter your question:", placeholder="E.g., Why is Nifty down today?")
    
    if st.button("Get Answer", type="primary"):
        if question:
            with st.spinner("Finding answer..."):
                result = answer_question(question)
                
                if result:
                    st.markdown(f"### Answer")
                    st.markdown(result["answer"])
                    
                    if result.get("sources") and len(result["sources"]) > 0:
                        st.markdown("### Sources")
                        for source in result["sources"]:
                            st.markdown(f"- **{source.get('title', '')}** - {source.get('source', '')} ({format_date(str(source.get('date', '')))})")
        else:
            st.warning("Please enter a question")
    
    st.divider()
    
    # Example questions
    st.subheader("Example Questions")
    example_questions = [
        "Why did Jyothy Labs up today?",
        "What happened to Nifty this week?",
        "Any macro news impacting tech-focused funds?",
        "What does the last quarter say for the Swiggy?"
    ]
    
    for q in example_questions:
        if st.button(q):
            st.session_state.question = q
            st.rerun()

# Tab 2: Stock Lookup (NEW)
with tab2:
    st.header("Stock Symbol Lookup & Analysis")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        stock_symbol = st.text_input("Enter stock symbol:", placeholder="E.g., RELIANCE, INFY, TCS")
    
    with col2:
        lookup_button = st.button("Lookup Stock", type="primary")
    
    # Example symbols
    example_symbols = ["RELIANCE", "TCS", "INFY", "ICICIBANK", "JYOTHYLAB"]
    st.caption("Try these examples:")
    
    cols = st.columns(len(example_symbols))
    for i, symbol in enumerate(example_symbols):
        with cols[i]:
            if st.button(symbol, key=f"example_symbol_{symbol}"):
                st.session_state.stock_symbol = symbol
                st.rerun()
    
    # Custom question option
    custom_question = st.text_input(
        "Ask a specific question (optional):", 
        placeholder="E.g., Why is this stock price changing? What are the recent developments?"
    )
    
    if lookup_button or ('stock_symbol' in st.session_state and st.session_state.stock_symbol == stock_symbol):
        if stock_symbol:
            # Store current symbol in session state
            st.session_state.stock_symbol = stock_symbol
            
            # Display stock information & news
            col1, col2 = st.columns([2, 1])
            
            with col1:
                with st.spinner("Loading stock news..."):
                    news_data = get_stock_news(stock_symbol)
                    
                    if "error" in news_data:
                        st.error(news_data["error"])
                    else:
                        # Display news
                        st.markdown(f"### Recent News for {news_data.get('company_name', stock_symbol)}")
                        
                        if 'news' in news_data and news_data['news']:
                            # Create tabs for different news sources if available
                            news_sources = list(set([article.get('source', 'Unknown') for article in news_data['news']]))
                            
                            if len(news_sources) > 1:
                                news_tabs = st.tabs(["All"] + news_sources)
                                
                                # All news tab
                                with news_tabs[0]:
                                    for article in news_data['news']:
                                        st.markdown(f"**{article.get('title', '')}**")
                                        st.markdown(f"*{article.get('source', '')} - {format_date(article.get('date', ''))}*")
                                        st.markdown("---")
                                
                                # Source-specific tabs
                                for i, source in enumerate(news_sources):
                                    with news_tabs[i+1]:
                                        source_news = [article for article in news_data['news'] if article.get('source') == source]
                                        for article in source_news:
                                            st.markdown(f"**{article.get('title', '')}**")
                                            st.markdown(f"*{format_date(article.get('date', ''))}*")
                                            st.markdown("---")
                            else:
                                # Just show all news
                                for article in news_data['news']:
                                    st.markdown(f"**{article.get('title', '')}**")
                                    st.markdown(f"*{article.get('source', '')} - {format_date(article.get('date', ''))}*")
                                    st.markdown("---")
                        else:
                            st.info("No recent news found for this stock symbol")
            
            with col2:
                with st.spinner("Loading stock data..."):
                    # Get basic stock information
                    stocks = search_stocks(stock_symbol)
                    
                    if stocks:
                        stock = stocks[0]
                        st.markdown(f"### {stock.get('name', '')}")
                        st.markdown(f"**Symbol:** {stock.get('symbol', '')}")
                        st.markdown(f"**ISIN:** {stock.get('isin', '')}")
                        st.markdown(f"**Sector:** {stock.get('sector', 'Unknown')}")
                        
                        # Add placeholder for stock price chart
                        st.markdown("### Price Trend")
                        
                        # Create a simple placeholder chart
                        dates = pd.date_range(start='2023-01-01', periods=30, freq='D')
                        prices = np.random.normal(loc=0.1, scale=0.02, size=30).cumsum() + 100
                        
                        df = pd.DataFrame({
                            'Date': dates,
                            'Price': prices
                        })
                        
                        st.line_chart(df.set_index('Date'))
                    else:
                        st.warning("Stock information not found")
            
            # Ask for analysis
            st.markdown("### Stock Analysis")
            analysis_placeholder = st.empty()
            
            with st.spinner("Generating stock analysis..."):
                analysis = analyze_stock(stock_symbol, custom_question)
                
                if "error" in analysis:
                    analysis_placeholder.error(analysis["error"])
                else:
                    # Display analysis
                    analysis_placeholder.markdown(f"**Question:** {analysis.get('question')}")
                    analysis_placeholder.markdown(f"**Answer:** {analysis.get('answer', 'No analysis available')}")
                    
                    # Display sources
                    if analysis.get("sources"):
                        st.markdown("#### News Sources")
                        sources_df = pd.DataFrame(analysis["sources"])
                        if not sources_df.empty:
                            if 'relevance_score' in sources_df.columns:
                                sources_df = sources_df.sort_values('relevance_score', ascending=False)
                            
                            for _, source in sources_df.iterrows():
                                st.markdown(f"- **{source.get('title', '')}** - {source.get('source', '')} ({format_date(str(source.get('date', '')))})")
                                
                    # Show if this is a simulated response
                    if analysis.get("is_simulated", False):
                        st.info("Note: This analysis is based on pattern matching rather than advanced NLP. For higher quality analysis, ensure the Gemini API key is configured correctly.")
        else:
            st.warning("Please enter a stock symbol")

# Tab 3: News
with tab3:
    st.header("Financial News")
    
    # News category selector
    categories = [None, "markets", "mutual_funds", "economy", "companies"]
    category_labels = ["All", "Markets", "Mutual Funds", "Economy", "Companies"]
    
    selected_category_index = st.selectbox(
        "Category:",
        range(len(categories)),
        format_func=lambda x: category_labels[x]
    )
    selected_category = categories[selected_category_index]
    
    # Get headlines
    with st.spinner("Loading headlines..."):
        headlines = get_headlines(category=selected_category)
    
    # Display headlines
    if headlines:
        for headline in headlines:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"### {headline.get('title', 'No Title')}")
                st.markdown(f"*{headline.get('source', 'Unknown')} - {format_date(headline.get('date', ''))}*")
                st.markdown(headline.get('summary', ''))
            with col2:
                if st.button("Read More", key=f"read_{headline.get('url')}"):
                    with st.spinner("Loading article..."):
                        article = get_article(headline.get('url'))
                        
                        if article:
                            st.markdown(f"## {article.get('title', 'No Title')}")
                            st.markdown(f"*{article.get('source', 'Unknown')} - {format_date(article.get('date', ''))}*")
                            st.markdown("---")
                            st.markdown(article.get('content', 'No content available.'))
            
            st.divider()
    else:
        st.info("No headlines available. Make sure the API is running.")

# Tab 4: Stocks
with tab4:
    st.header("Stock Search")
    
    stock_query = st.text_input("Search for stocks:", placeholder="E.g., Reliance, HDFC, INE002A01018")
    
    if st.button("Search Stocks", type="primary"):
        if stock_query:
            with st.spinner("Searching stocks..."):
                stocks = search_stocks(stock_query)
                
                if stocks:
                    # Convert to DataFrame for better display
                    df = pd.DataFrame(stocks)
                    st.dataframe(df, use_container_width=True)
                    
                    # Option to view more details about a selected stock
                    stock_symbols = df["symbol"].tolist()
                    selected_stock = st.selectbox("Select a stock for more details:", stock_symbols)
                    
                    if selected_stock:
                        st.markdown(f"### {selected_stock} Details")
                        # Placeholder for stock details and charts
                        st.info("Detailed stock information would be shown here.")
                        
                        # Placeholder chart
                        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
                        prices = np.random.normal(loc=100, scale=10, size=100).cumsum() + 1000
                        
                        fig, ax = plt.subplots(figsize=(10, 6))
                        ax.plot(dates, prices)
                        ax.set_title(f"{selected_stock} Price History")
                        ax.set_xlabel("Date")
                        ax.set_ylabel("Price")
                        ax.grid(True)
                        st.pyplot(fig)
                else:
                    st.warning("No stocks found matching your query.")
        else:
            st.warning("Please enter a search term")

# Tab 5: Mutual Funds
with tab5:
    st.header("Mutual Fund Search")
    
    fund_query = st.text_input("Search for mutual funds:", placeholder="E.g., SBI, HDFC, Blue Chip")
    
    if st.button("Search Funds", type="primary"):
        if fund_query:
            with st.spinner("Searching mutual funds..."):
                funds = search_mutual_funds(fund_query)
                
                if funds:
                    # Convert to DataFrame for better display
                    df = pd.DataFrame(funds)
                    st.dataframe(df, use_container_width=True)
                    
                    # Option to view more details about a selected fund
                    fund_codes = df["scheme_code"].tolist()
                    fund_names = df["scheme_name"].tolist()
                    fund_options = [f"{code} - {name}" for code, name in zip(fund_codes, fund_names)]
                    
                    selected_fund_option = st.selectbox("Select a fund for more details:", fund_options)
                    
                    if selected_fund_option:
                        selected_fund_code = selected_fund_option.split(" - ")[0]
                        st.markdown(f"### Fund Details")
                        # Placeholder for fund details and charts
                        st.info("Detailed fund information would be shown here.")
                        
                        # Placeholder chart - NAV history
                        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
                        nav_values = np.random.normal(loc=0.1, scale=0.02, size=100).cumsum() + 30
                        
                        fig, ax = plt.subplots(figsize=(10, 6))
                        ax.plot(dates, nav_values)
                        ax.set_title("NAV History")
                        ax.set_xlabel("Date")
                        ax.set_ylabel("NAV")
                        ax.grid(True)
                        st.pyplot(fig)
                        
                        # Placeholder for holdings
                        st.subheader("Top Holdings")
                        holdings = {
                            "HDFC Bank": 8.2,
                            "ICICI Bank": 7.5,
                            "Reliance Industries": 7.2,
                            "Infosys": 6.8,
                            "TCS": 6.3
                        }
                        
                        fig, ax = plt.subplots(figsize=(10, 6))
                        ax.bar(holdings.keys(), holdings.values())
                        ax.set_title("Top Holdings (%)")
                        ax.set_ylabel("Allocation (%)")
                        plt.xticks(rotation=45, ha='right')
                        plt.tight_layout()
                        st.pyplot(fig)
                else:
                    st.warning("No mutual funds found matching your query.")
        else:
            st.warning("Please enter a search term")


# Footer
st.markdown("---")
st.markdown("© 2023 NewsSense | Built for MyFi Hackathon Challenge") 