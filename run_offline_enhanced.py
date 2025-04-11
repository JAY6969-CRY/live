#!/usr/bin/env python
"""
Run NewsSense in offline mode with enhanced NLP capabilities.
This version uses the advanced NLP model for better query processing and
more accurate news source filtering.
"""
import os
import sys
import subprocess
import webbrowser
import time
from dotenv import load_dotenv
import datetime
import random
import requests

# Load environment variables from .env file if it exists
print("Loading environment variables from .env file...")
load_dotenv()

def run_streamlit_offline_enhanced():
    """Run the Streamlit frontend in offline mode with enhanced NLP."""
    print("\nStarting Streamlit UI in OFFLINE MODE with ENHANCED NLP...")
    # Add the current directory to the Python path
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd() + os.pathsep + env.get("PYTHONPATH", "")
    
    # Set environment variables for Streamlit
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    # Enable enhanced NLP mode
    env["USE_ENHANCED_NLP"] = "true"
    
    # Create a simplified app file
    with open("temp_offline_enhanced_app.py", "w", encoding="utf-8") as f:
        f.write('''
# Import required libraries
import os
import sys
import streamlit as st
import datetime
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
import random

# Add the current directory to path
sys.path.append(os.getcwd())

# Set offline mode
OFFLINE_MODE = True

# Import enhanced NLP model
try:
    from src.models.financial_qa_upgrade import EnhancedFinancialQA
    USE_ENHANCED_NLP = os.environ.get('USE_ENHANCED_NLP', 'false').lower() == 'true'
    print("Enhanced NLP capabilities are ENABLED")
except ImportError:
    USE_ENHANCED_NLP = False
    print("Enhanced NLP capabilities are NOT available")

# API configuration (for non-offline mode)
API_URL = "http://localhost:8000" 
FLASK_API_URL = "http://localhost:5000"

# Page configuration
st.set_page_config(
    page_title="NewsSense Enhanced",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown("""
<style>
    .stock-up {
        color: #0ecb81;
        font-weight: bold;
    }
    .stock-down {
        color: #f6465d;
        font-weight: bold;
    }
    .stock-neutral {
        color: #767c89;
        font-weight: bold;
    }
    .source-box {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .source-title {
        font-weight: bold;
        font-size: 16px;
    }
    .relevance-badge {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 2px 8px;
        font-size: 12px;
    }
    .stock-data-card {
        background-color: #f7f7f7;
        border-radius: 5px;
        padding: 15px;
        margin-top: 10px;
    }
    .stock-price {
        font-size: 20px;
        font-weight: bold;
    }
    .stock-change {
        font-size: 16px;
        margin-left: 10px;
    }
    .stock-details {
        display: flex;
        justify-content: space-between;
        margin-top: 10px;
    }
    .stock-detail-item {
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# Stock data cache
STOCK_DATA = {
    "TCS": {
        "name": "Tata Consultancy Services Ltd.",
        "ticker": "TCS.NS",
        "isin": "INE467B01029",
        "sector": "Information Technology",
        "price": 3754.25,
        "prev_price": 3720.15,
        "change": 34.10,
        "change_pct": 0.92,
        "volume": 1254879,
        "day_high": 3765.80,
        "day_low": 3718.55,
        "52w_high": 3965.00,
        "52w_low": 3175.20,
        "pe_ratio": 27.8,
        "market_cap": 13757.90  # in billion INR
    },
    "RELIANCE": {
        "name": "Reliance Industries Ltd.",
        "ticker": "RELIANCE.NS",
        "isin": "INE002A01018",
        "sector": "Conglomerate",
        "price": 2865.75,
        "prev_price": 2879.95,
        "change": -14.20,
        "change_pct": -0.49,
        "volume": 3568942,
        "day_high": 2895.00,
        "day_low": 2862.10,
        "52w_high": 2950.00,
        "52w_low": 2365.00,
        "pe_ratio": 31.2,
        "market_cap": 19357.45  # in billion INR
    },
    "HDFC": {
        "name": "HDFC Bank Ltd.",
        "ticker": "HDFCBANK.NS",
        "isin": "INE040A01034",
        "sector": "Banking",
        "price": 1643.50,
        "prev_price": 1629.80,
        "change": 13.70,
        "change_pct": 0.84,
        "volume": 7895621,
        "day_high": 1648.00,
        "day_low": 1628.30,
        "52w_high": 1725.00,
        "52w_low": 1363.45,
        "pe_ratio": 22.5,
        "market_cap": 9156.30  # in billion INR
    },
    "INFY": {
        "name": "Infosys Ltd.",
        "ticker": "INFY.NS",
        "isin": "INE009A01021",
        "sector": "Information Technology",
        "price": 1475.90,
        "prev_price": 1464.25,
        "change": 11.65,
        "change_pct": 0.80,
        "volume": 3654210,
        "day_high": 1480.00,
        "day_low": 1463.00,
        "52w_high": 1620.00,
        "52w_low": 1215.45,
        "pe_ratio": 25.1,
        "market_cap": 6124.80  # in billion INR
    },
    "NIFTY": {
        "name": "Nifty 50 Index",
        "ticker": "^NSEI",
        "type": "Index",
        "price": 22456.80,
        "prev_price": 22402.40,
        "change": 54.40,
        "change_pct": 0.24,
        "day_high": 22498.65,
        "day_low": 22389.75,
        "52w_high": 22526.00,
        "52w_low": 17961.90
    }
}

# Source links for redirects
SOURCE_LINKS = {
    "Economic Times": "https://economictimes.indiatimes.com/",
    "Business Standard": "https://www.business-standard.com/",
    "Mint": "https://www.livemint.com/",
    "Money Control": "https://www.moneycontrol.com/",
    "Financial Express": "https://www.financialexpress.com/",
    "Reuters": "https://www.reuters.com/",
    "Bloomberg": "https://www.bloomberg.com/"
}

# Utility functions
def format_date(date_str):
    """Format date string for display."""
    try:
        dt = datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%d %b %Y, %H:%M")
    except:
        return date_str

def get_source_link(source_name):
    """Get link for a given source."""
    return SOURCE_LINKS.get(source_name, "#")

def get_stock_data(ticker):
    """Get stock data for a given ticker."""
    # In offline mode, return mock data from our cache
    stock = None
    if ticker in STOCK_DATA:
        stock = STOCK_DATA[ticker]
    elif ticker == "tcs":
        stock = STOCK_DATA["TCS"]
    elif ticker == "reliance":
        stock = STOCK_DATA["RELIANCE"]
    elif ticker == "hdfc":
        stock = STOCK_DATA["HDFC"]
    elif ticker == "infosys":
        stock = STOCK_DATA["INFY"]
    elif ticker in ["nifty", "nifty50"]:
        stock = STOCK_DATA["NIFTY"]
    
    # If stock not found, return None
    if not stock:
        return None
    
    return stock

def render_stock_performance(stock_data):
    """Render stock performance data."""
    if not stock_data:
        return st.write("No stock data available")
    
    # Determine change class (up, down, neutral)
    change_class = "stock-neutral"
    change_icon = "—"
    if stock_data["change"] > 0:
        change_class = "stock-up"
        change_icon = "▲"
    elif stock_data["change"] < 0:
        change_class = "stock-down"
        change_icon = "▼"
    
    # Format change percentage
    change_pct_str = f"{abs(stock_data['change_pct']):.2f}%"
    
    # Render stock card
    st.markdown(f"""
    <div class="stock-data-card">
        <div>
            <span>{stock_data['name']}</span>
            <span style="float:right;font-size:12px;">{stock_data.get('ticker', '')}</span>
        </div>
        <div style="margin-top:10px;">
            <span class="stock-price">₹{stock_data['price']:,.2f}</span>
            <span class="{change_class} stock-change">{change_icon} {abs(stock_data['change']):,.2f} ({change_pct_str})</span>
        </div>
        <div class="stock-details">
            <div class="stock-detail-item">
                <div style="color:#767c89;">Previous Close</div>
                <div>₹{stock_data['prev_price']:,.2f}</div>
            </div>
            <div class="stock-detail-item">
                <div style="color:#767c89;">Day Range</div>
                <div>₹{stock_data['day_low']:,.2f} - ₹{stock_data['day_high']:,.2f}</div>
            </div>
            <div class="stock-detail-item">
                <div style="color:#767c89;">52 Week Range</div>
                <div>₹{stock_data['52w_low']:,.2f} - ₹{stock_data['52w_high']:,.2f}</div>
            </div>
        </div>
        <div style="margin-top:10px;font-size:12px;color:#767c89;">
            {stock_data.get('sector', '')} | ISIN: {stock_data.get('isin', 'N/A')}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show a simple chart
    if 'prev_price' in stock_data:
        # Generate some fake historical data
        dates = pd.date_range(end=datetime.datetime.now(), periods=30).tolist()
        base_price = min(stock_data['price'], stock_data['prev_price']) * 0.9
        price_range = abs(stock_data['price'] - stock_data['prev_price']) * 2
        
        # Create random walk with trend towards current price
        np.random.seed(hash(stock_data['ticker']) % 10000)  # Consistent seed per ticker
        prices = [base_price]
        for i in range(29):
            movement = np.random.normal(0, price_range/30)
            trend_factor = (stock_data['price'] - prices[-1]) / (29-i) * 0.3
            prices.append(max(prices[-1] + movement + trend_factor, base_price * 0.9))
        
        # Create dataframe
        df = pd.DataFrame({
            'Date': dates,
            'Price': prices
        })
        
        # Plot
        fig, ax = plt.subplots(figsize=(10, 3))
        ax.plot(df['Date'], df['Price'])
        ax.set_title(f"{stock_data['name']} - 30 Day Price Chart")
        ax.set_ylabel('Price (₹)')
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)

def find_stock_ticker_in_source(source):
    """Find stock ticker mentioned in a source."""
    # First check if any known ticker is in the matches
    matches = source.get('matches', [])
    for match in matches:
        match_upper = match.upper()
        if match_upper in STOCK_DATA:
            return match_upper
    
    # Check if ticker is in title
    title = source.get('title', '').upper()
    for ticker in STOCK_DATA:
        if ticker in title:
            return ticker
    
    # Check if company name is in title
    title_lower = title.lower()
    if "tcs" in title_lower or "tata consultancy" in title_lower:
        return "TCS"
    elif "reliance" in title_lower:
        return "RELIANCE"
    elif "hdfc" in title_lower:
        return "HDFC"
    elif "infosys" in title_lower:
        return "INFY"
    elif "nifty" in title_lower:
        return "NIFTY"
    
    return None

# QA processing function
def answer_question(question):
    """Get answer to question with advanced NLP capabilities."""
    if OFFLINE_MODE:
        # Use enhanced NLP if available and enabled
        if USE_ENHANCED_NLP:
            try:
                # Create enhanced QA system if not already created
                if 'enhanced_qa_system' not in st.session_state:
                    st.session_state.enhanced_qa_system = EnhancedFinancialQA(use_transformers=False)
                
                # Always process the current question
                answer, _, sources = st.session_state.enhanced_qa_system.answer_question(question)
                
                # Store the current question to ensure we're not reusing old entities
                st.session_state.last_question = question
                
                return {
                    "question": question,
                    "answer": answer,
                    "sources": sources,
                    "entities": st.session_state.enhanced_qa_system.current_entity_matches,
                    "is_simulated": True,
                    "uses_advanced_nlp": True
                }
            except Exception as e:
                st.error(f"Error using enhanced NLP: {str(e)}")
                # Fall back to basic simulation
                pass
        
        # Fall back to original offline mode answer code
        question_lower = question.lower()
        mock_sources = []
        mock_response = ""
        
        # Check the current question for specific stocks or topics
        if any(stock in question for stock in ["TCS", "Tata Consultancy", "tcs"]):
            mock_sources = [
                {
                    "title": "TCS shares up 2% on market optimism",
                    "source": "Economic Times",
                    "date": "2023-04-11T09:30:00",
                    "matches": ["tcs", "market"],
                    "relevance_score": 15
                },
                {
                    "title": "TCS announces new AI initiative for banking sector",
                    "source": "Business Standard",
                    "date": "2023-04-10T14:15:00",
                    "matches": ["tcs", "banking", "ai"],
                    "relevance_score": 12
                }
            ]
            mock_response = "TCS stock has shown positive movement recently due to overall market optimism and the company's new initiatives in AI and cloud services."
        
        elif any(stock in question for stock in ["RELIANCE", "Reliance", "reliance"]):
            mock_sources = [
                {
                    "title": "Reliance Industries expands retail footprint with new acquisition",
                    "source": "Economic Times",
                    "date": "2023-04-11T10:45:00",
                    "matches": ["reliance", "retail"],
                    "relevance_score": 15
                },
                {
                    "title": "Oil prices impact Reliance's refining margins positively",
                    "source": "Financial Express",
                    "date": "2023-04-09T16:30:00",
                    "matches": ["reliance", "oil", "refining"],
                    "relevance_score": 13
                }
            ]
            mock_response = "Reliance Industries has been showing strength across its diverse business segments. The retail division continues to expand with strategic acquisitions."
        
        elif "HDFC" in question or "hdfc" in question_lower:
            mock_sources = [
                {
                    "title": "HDFC Bank reports strong Q4 results, NPAs stable",
                    "source": "Economic Times",
                    "date": "2023-04-10T09:15:00",
                    "matches": ["hdfc", "bank", "results"],
                    "relevance_score": 16
                },
                {
                    "title": "HDFC-HDFC Bank merger on track for completion",
                    "source": "Business Standard",
                    "date": "2023-04-09T11:30:00",
                    "matches": ["hdfc", "merger"],
                    "relevance_score": 14
                }
            ]
            mock_response = "HDFC Bank has shown strong performance in the recent quarter with stable asset quality. The merger with parent HDFC is progressing as planned and expected to boost growth prospects."
        
        elif "Infosys" in question or "INFY" in question or "infosys" in question_lower:
            mock_sources = [
                {
                    "title": "Infosys wins major digital transformation deal",
                    "source": "Mint",
                    "date": "2023-04-11T10:20:00",
                    "matches": ["infosys", "digital"],
                    "relevance_score": 14
                },
                {
                    "title": "Infosys Q4 preview: Analysts expect margin pressure",
                    "source": "Financial Express",
                    "date": "2023-04-10T09:45:00",
                    "matches": ["infosys", "margin", "q4"],
                    "relevance_score": 13
                }
            ]
            mock_response = "Infosys has recently secured a significant digital transformation deal, though analysts anticipate some margin pressure in the upcoming quarterly results due to wage hikes and investments in new capabilities."
        
        elif "Nifty" in question or "nifty" in question_lower:
            mock_sources = [
                {
                    "title": "Nifty scales new high on foreign investor inflows",
                    "source": "Economic Times",
                    "date": "2023-04-11T16:30:00",
                    "matches": ["nifty", "high"],
                    "relevance_score": 15
                },
                {
                    "title": "Nifty technical analysis: Support and resistance levels",
                    "source": "Money Control",
                    "date": "2023-04-11T08:45:00",
                    "matches": ["nifty", "technical", "support"],
                    "relevance_score": 12
                }
            ]
            mock_response = "Nifty has been showing positive momentum driven by sustained foreign institutional investor inflows and positive global cues. Technical indicators suggest short-term support around 19,500 levels."
        
        else:
            mock_sources = [
                {
                    "title": "Market update: Nifty ends higher amid global optimism",
                    "source": "Money Control",
                    "date": "2023-04-11T16:00:00",
                    "matches": ["market", "nifty"],
                    "relevance_score": 10
                },
                {
                    "title": "Banking stocks lead rally as inflation concerns ease",
                    "source": "Economic Times",
                    "date": "2023-04-11T15:30:00",
                    "matches": ["banking", "stocks"],
                    "relevance_score": 8
                }
            ]
            mock_response = "Based on the latest market trends and news analysis, the markets have shown positive momentum with banking and IT sectors leading the gains."
        
        return {
            "question": question,
            "answer": mock_response,
            "sources": mock_sources,
            "is_simulated": True
        }
    
    # Use API in non-offline mode
    try:
        response = requests.post(f"{API_URL}/qa/answer", json={"question": question})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching answer: {str(e)}")
        return {"question": question, "answer": "Sorry, I couldn't get an answer at this time."}

# Main app
def main():
    """Main Streamlit app."""
    st.markdown("<h1 class='main-title'>NewsSense Enhanced</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Financial News Analysis with Advanced NLP</p>", unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("NewsSense")
    st.sidebar.write("Enhanced with Advanced NLP")
    
    # Add options
    option = st.sidebar.selectbox(
        "Select a feature",
        ["Financial Q&A", "Market Overview", "Stock Analysis"]
    )
    
    # Display the selected feature
    if option == "Financial Q&A":
        qa_section()
    elif option == "Market Overview":
        st.write("## Market Overview")
        st.write("This section would show market trends and news, but is not implemented in this demo.")
    elif option == "Stock Analysis":
        st.write("## Stock Analysis")
        st.write("This section would provide stock-specific analysis, but is not implemented in this demo.")

def qa_section():
    """Enhanced Q&A section with better refresh handling."""
    st.write("### Financial Q&A")
    st.write("Ask a question about financial news, stocks, or market trends:")
    
    # Get the question
    question = st.text_input("Your question:", key="qa_question")
    
    # Add a submit button to trigger explicit interaction
    submit = st.button("Submit Question")
    
    if submit and question:
        # Clear any previous results
        if 'qa_results' in st.session_state:
            del st.session_state.qa_results
        
        # Force re-analysis of the current question
        with st.spinner("Processing your question..."):
            st.session_state.qa_results = answer_question(question)
    
    # Display the results if available
    if 'qa_results' in st.session_state and st.session_state.qa_results:
        result = st.session_state.qa_results
        
        # Display answer
        st.markdown("#### Answer:")
        st.markdown(f"{result.get('answer', 'No answer available')}")
        
        # Show relevant sources
        st.markdown("#### Sources:")
        sources = result.get('sources', [])
        if sources:
            for i, source in enumerate(sources):
                with st.expander(f"{source.get('title', 'Untitled')}"):
                    # Source info
                    source_name = source.get('source', 'Unknown')
                    source_link = get_source_link(source_name)
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**Source:** [{source_name}]({source_link})")
                        st.markdown(f"**Date:** {format_date(source.get('date', 'Unknown'))}")
                    with col2:
                        if 'relevance_score' in source:
                            relevance = source.get('relevance_score', 0)
                            stars = "⭐" * min(5, max(1, int(relevance / 5)))
                            st.markdown(f"**Relevance:** {stars} ({relevance:.1f})")
                    
                    if 'matches' in source and source['matches']:
                        st.markdown(f"**Matched terms:** {', '.join(source['matches'])}")
                    
                    # Find stock ticker in source
                    ticker = find_stock_ticker_in_source(source)
                    if ticker:
                        st.markdown("#### Stock Performance")
                        stock_data = get_stock_data(ticker)
                        if stock_data:
                            render_stock_performance(stock_data)
                        else:
                            st.write("No stock data available for this source.")
        else:
            st.write("No relevant sources found.")
        
        # Show entities if available
        if 'entities' in result and any(result['entities'].values()):
            with st.expander("Entity Detection Details"):
                entities = result['entities']
                
                if entities.get('companies'):
                    st.markdown(f"**Companies:** {', '.join(entities['companies'])}")
                
                if entities.get('indices'):
                    st.markdown(f"**Indices:** {', '.join(entities['indices'])}")
                
                if entities.get('sectors'):
                    st.markdown(f"**Sectors:** {', '.join(entities['sectors'])}")
        
        # Show simulation notice
        if result.get('is_simulated', False):
            st.info("Note: This response is simulated for demonstration purposes.")
            if result.get('uses_advanced_nlp', False):
                st.success("✓ Advanced NLP processing enabled")

def analyze_stock(symbol, question=None):
    """Generate analysis for a stock based on recent news with enhanced NLP context."""
    if OFFLINE_MODE:
        # Return mock data in offline mode with stock-specific analysis
        mock_sources = []
        mock_analysis = ""
        mock_question = question if question else f"What's happening with {symbol}?"
        
        # Define specific responses for popular stocks
        stock_responses = {
            "TCS": {
                "analysis": "TCS has demonstrated consistent performance in recent quarters, maintaining its position as a leader in the IT services sector. The company's focus on digital transformation initiatives and cloud services has been well-received by clients, contributing to a healthy order book.",
                "sources": [
                    {
                        "title": "TCS reports 8% growth in Q1 revenue",
                        "source": "Economic Times",
                        "date": datetime.datetime.now().isoformat(),
                        "matches": ["tcs", "revenue", "growth", "quarter"],
                        "relevance_score": 15,
                        "ticker": "TCS"
                    },
                    {
                        "title": "TCS wins $200 million cloud transformation deal",
                        "source": "Business Standard",
                        "date": (datetime.datetime.now() - datetime.timedelta(days=5)).isoformat(),
                        "matches": ["tcs", "deal", "cloud", "transformation"],
                        "relevance_score": 14,
                        "ticker": "TCS"
                    }
                ]
            },
            "RELIANCE": {
                "analysis": "Reliance Industries continues to execute well across its diverse business segments. The retail division is showing strong growth through both organic expansion and strategic acquisitions. In the telecom segment, Jio maintains its subscriber growth momentum.",
                "sources": [
                    {
                        "title": "Reliance Retail acquires logistics startup to strengthen e-commerce",
                        "source": "Economic Times",
                        "date": datetime.datetime.now().isoformat(),
                        "matches": ["reliance", "retail", "acquisition", "ecommerce"],
                        "relevance_score": 15,
                        "ticker": "RELIANCE"
                    },
                    {
                        "title": "Reliance Jio 5G now available in 200 cities",
                        "source": "Financial Express",
                        "date": (datetime.datetime.now() - datetime.timedelta(days=3)).isoformat(),
                        "matches": ["reliance", "jio", "5g"],
                        "relevance_score": 13,
                        "ticker": "RELIANCE"
                    }
                ]
            }
        }
        
        # Get stock-specific response if available
        if symbol.upper() in stock_responses:
            mock_analysis = stock_responses[symbol.upper()]["analysis"]
            mock_sources = stock_responses[symbol.upper()]["sources"]
        else:
            # Create generic response for other stocks
            mock_analysis = f"Based on recent market trends and news, {symbol} has been showing movement influenced by both sector-specific factors and broader market sentiment. Analysts have mixed views on the stock's near-term prospects."
            
            # Generate generic sources with ticker information
            mock_sources = [
                {
                    "title": f"{symbol} Q1 results: Mixed performance amid challenging environment",
                    "source": "Economic Times",
                    "date": datetime.datetime.now().isoformat(),
                    "matches": [symbol.lower(), "results", "performance"],
                    "relevance_score": 15,
                    "ticker": symbol.upper()
                },
                {
                    "title": f"Analysts remain cautious on {symbol} after recent rally",
                    "source": "Moneycontrol",
                    "date": (datetime.datetime.now() - datetime.timedelta(days=3)).isoformat(),
                    "matches": [symbol.lower(), "analysts", "cautious", "rally"],
                    "relevance_score": 12,
                    "ticker": symbol.upper()
                }
            ]
        
        # Customize analysis based on the question if provided
        if question:
            # For demonstration, provide simple responses to common question types
            if "why" in question.lower() and "price" in question.lower():
                mock_analysis = f"The price movement in {symbol} is primarily due to recent quarterly results and broader market sentiment. Analyst expectations were {random.choice(['exceeded', 'met', 'missed'])}, causing the stock to react accordingly."
            elif "compare" in question.lower():
                mock_analysis = f"{symbol} has {random.choice(['outperformed', 'underperformed'])} peers in the sector over the past quarter, with stronger metrics in {random.choice(['revenue growth', 'profit margins', 'return on equity'])}."
            elif "outlook" in question.lower() or "future" in question.lower():
                mock_analysis = f"The outlook for {symbol} appears {random.choice(['positive', 'cautiously optimistic', 'mixed'])} based on current business momentum and sector trends. Most analysts have maintained their ratings with target prices suggesting a {random.choice(['8-10%', '5-7%', '10-15%'])} potential upside."
        
        # Return the analysis with question, sources, and stock performance data
        response = {
            "question": mock_question,
            "answer": mock_analysis,
            "sources": mock_sources,
            "is_simulated": True
        }
        
        return response
    else:
        # For non-offline mode, call the API
        try:
            params = {"symbol": symbol}
            if question:
                params["question"] = question
                
            response = requests.get(f"{API_URL}/analyze-stock", params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"API error: {response.status_code}"
                }
        except Exception as e:
            return {
                "error": f"Error analyzing stock: {str(e)}"
            }

# Run the main app
if __name__ == "__main__":
    main()
''')
    
    # Start the process with offline enhanced mode
    process = subprocess.Popen(
        ["streamlit", "run", "temp_offline_enhanced_app.py", "--server.port=8501"],
        env=env
    )
    
    # Wait a moment for Streamlit to start
    time.sleep(3)
    
    # Open the browser
    print("Opening web browser to http://localhost:8501")
    webbrowser.open("http://localhost:8501")
    
    print("\nStreamlit UI is running in OFFLINE MODE with ENHANCED NLP capabilities.")
    print("This means all data is simulated using advanced NLP for better query understanding.")
    print("No API connections are required.")
    print("Press Ctrl+C to stop.")
    
    # Keep the script running until Ctrl+C
    try:
        process.wait()
    except KeyboardInterrupt:
        print("\nStopping Streamlit...")
        process.terminate()
        process.wait()
        
        # Clean up the temp file
        if os.path.exists("temp_offline_enhanced_app.py"):
            os.remove("temp_offline_enhanced_app.py")
        
        print("Streamlit stopped.")

if __name__ == "__main__":
    run_streamlit_offline_enhanced() 