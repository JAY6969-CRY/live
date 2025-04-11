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
    """Get answer to question from API with enhanced NLP context."""
    if OFFLINE_MODE:
        # Return mock data in offline mode with improved NLP context awareness
        question_lower = question.lower()
        mock_sources = []
        mock_response = ""
        
        # Extract potential stock symbols (uppercase words)
        potential_stocks = [word for word in question.split() if word.isupper() and len(word) >= 2]
        
        # Stock-specific responses
        if any(stock in question for stock in ["TCS", "Tata Consultancy", "tcs"]):
            mock_sources = [
                {
                    "title": "TCS shares up 2% on market optimism",
                    "source": "Economic Times",
                    "date": datetime.datetime.now().isoformat(),
                    "matches": ["tcs", "market"],
                    "relevance_score": 15
                },
                {
                    "title": "TCS announces new AI initiative for banking sector",
                    "source": "Business Standard",
                    "date": (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat(),
                    "matches": ["tcs", "banking", "ai"],
                    "relevance_score": 12
                },
                {
                    "title": "IT sector shows resilience amid market volatility",
                    "source": "Mint",
                    "date": (datetime.datetime.now() - datetime.timedelta(days=2)).isoformat(),
                    "matches": ["it", "market"],
                    "relevance_score": 8
                }
            ]
            mock_response = "TCS stock has shown positive movement recently due to overall market optimism and the company's new initiatives in AI and cloud services. Their recent announcement about expanding services for the banking sector has been received well by investors, contributing to the upward trend. Analysts remain bullish on TCS due to strong order books and business momentum in key markets."
        
        elif any(stock in question for stock in ["RELIANCE", "Reliance", "reliance"]):
            mock_sources = [
                {
                    "title": "Reliance Industries expands retail footprint with new acquisition",
                    "source": "Economic Times",
                    "date": datetime.datetime.now().isoformat(),
                    "matches": ["reliance", "retail"],
                    "relevance_score": 15
                },
                {
                    "title": "Oil prices impact Reliance's refining margins positively",
                    "source": "Financial Express",
                    "date": (datetime.datetime.now() - datetime.timedelta(days=2)).isoformat(),
                    "matches": ["reliance", "oil", "refining"],
                    "relevance_score": 13
                },
                {
                    "title": "Reliance Jio adds 4.2 million subscribers in Q1",
                    "source": "Mint",
                    "date": (datetime.datetime.now() - datetime.timedelta(days=4)).isoformat(),
                    "matches": ["reliance", "jio"],
                    "relevance_score": 11
                }
            ]
            mock_response = "Reliance Industries has been showing strength across its diverse business segments. The retail division continues to expand with strategic acquisitions, while favorable oil price movements have positively impacted their refining margins. Additionally, Reliance Jio continues to gain market share with strong subscriber additions, contributing to the overall positive sentiment around the stock."
        
        elif any(stock in question for stock in ["INFY", "Infosys", "infosys"]):
            mock_sources = [
                {
                    "title": "Infosys wins major deal with European client",
                    "source": "Business Standard",
                    "date": datetime.datetime.now().isoformat(),
                    "matches": ["infosys", "deal", "european"],
                    "relevance_score": 15
                },
                {
                    "title": "Infosys revises guidance upward after strong Q1 results",
                    "source": "Economic Times",
                    "date": (datetime.datetime.now() - datetime.timedelta(days=3)).isoformat(),
                    "matches": ["infosys", "results", "guidance"],
                    "relevance_score": 13
                }
            ]
            mock_response = "Infosys has been performing well recently, supported by strong deal wins including a major contract with a European client. Their Q1 results exceeded market expectations, allowing them to revise guidance upward for the fiscal year. The company's focus on digital transformation services and AI solutions has positioned them favorably in the current business environment."
        
        # Nifty responses
        elif "nifty" in question_lower:
            mock_sources = [
                {
                    "title": "Nifty hits new high on positive global cues",
                    "source": "Economic Times",
                    "date": datetime.datetime.now().isoformat(),
                    "matches": ["nifty", "market", "global"],
                    "relevance_score": 15
                },
                {
                    "title": "Nifty stocks that drove the rally this week",
                    "source": "Moneycontrol",
                    "date": (datetime.datetime.now() - datetime.timedelta(days=2)).isoformat(),
                    "matches": ["nifty", "stock", "rally"],
                    "relevance_score": 13
                },
                {
                    "title": "FII inflows push Nifty to record levels",
                    "source": "Business Standard",
                    "date": (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat(),
                    "matches": ["nifty", "fii", "inflows"],
                    "relevance_score": 12
                }
            ]
            mock_response = "Nifty has shown strong performance recently, reaching new highs driven by positive global market sentiment and significant foreign institutional investor (FII) inflows. Key sectors contributing to this rally include IT, banking, and energy stocks. Favorable macroeconomic indicators and better-than-expected corporate earnings have also supported the upward momentum."
        
        # Sensex responses
        elif "sensex" in question_lower:
            mock_sources = [
                {
                    "title": "Sensex surges 500 points on bank rally",
                    "source": "Business Standard",
                    "date": datetime.datetime.now().isoformat(),
                    "matches": ["sensex", "bank", "rally"],
                    "relevance_score": 15
                },
                {
                    "title": "Sensex hits 75,000 mark for first time",
                    "source": "Economic Times",
                    "date": (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat(),
                    "matches": ["sensex", "mark"],
                    "relevance_score": 14
                }
            ]
            mock_response = "Sensex has demonstrated remarkable strength, recently crossing the 75,000 mark for the first time. This rally has been primarily led by banking stocks, with HDFC Bank, ICICI Bank, and SBI being major contributors. Positive global cues and strong domestic institutional buying have supported this upward trend despite some concerns about valuations."
        
        # Bank/Financial sector responses
        elif any(term in question_lower for term in ["bank", "banking", "financial", "hdfc", "icici", "sbi"]):
            mock_sources = [
                {
                    "title": "Bank stocks gain on improved outlook",
                    "source": "Mint",
                    "date": datetime.datetime.now().isoformat(),
                    "matches": ["bank", "stock"],
                    "relevance_score": 15
                },
                {
                    "title": "RBI policy boosts banking sector sentiment",
                    "source": "Financial Express",
                    "date": (datetime.datetime.now() - datetime.timedelta(days=3)).isoformat(),
                    "matches": ["banking", "rbi", "policy"],
                    "relevance_score": 13
                },
                {
                    "title": "HDFC Bank reports strong credit growth in retail segment",
                    "source": "Economic Times",
                    "date": (datetime.datetime.now() - datetime.timedelta(days=4)).isoformat(),
                    "matches": ["hdfc", "bank", "credit", "retail"],
                    "relevance_score": 12
                }
            ]
            mock_response = "The banking sector has been performing well recently, supported by favorable RBI policy measures and improving asset quality metrics. Major banks like HDFC Bank, ICICI Bank, and SBI have reported strong credit growth, particularly in the retail segment. The overall outlook for the sector remains positive with expectations of continued improvement in net interest margins."
        
        # Tech/IT sector responses
        elif any(term in question_lower for term in ["tech", "it sector", "technology", "software"]):
            mock_sources = [
                {
                    "title": "Tech stocks rebound after recent slump",
                    "source": "Financial Express",
                    "date": datetime.datetime.now().isoformat(),
                    "matches": ["tech", "stock", "rebound"],
                    "relevance_score": 15
                },
                {
                    "title": "Indian IT firms see increased deal momentum",
                    "source": "Economic Times",
                    "date": (datetime.datetime.now() - datetime.timedelta(days=2)).isoformat(),
                    "matches": ["it", "deal", "momentum"],
                    "relevance_score": 13
                },
                {
                    "title": "AI adoption driving growth for technology companies",
                    "source": "Mint",
                    "date": (datetime.datetime.now() - datetime.timedelta(days=5)).isoformat(),
                    "matches": ["technology", "ai", "growth"],
                    "relevance_score": 11
                }
            ]
            mock_response = "The IT sector has shown signs of recovery after a period of consolidation. Recent earnings reports from major IT companies indicate improved deal momentum and increasing client spending on digital transformation initiatives. The adoption of AI technologies is creating new growth opportunities, though concerns about global economic conditions continue to create some volatility in the sector."
        
        # Default response for other queries
        else:
            # Check for any stock symbols in the question
            for stock in potential_stocks:
                mock_sources.append({
                    "title": f"{stock} shares show movement on recent developments",
                    "source": "Economic Times",
                    "date": datetime.datetime.now().isoformat(),
                    "matches": [stock.lower(), "shares", "developments"],
                    "relevance_score": 14
                })
                
                mock_sources.append({
                    "title": f"Analysts revise outlook for {stock}",
                    "source": "Moneycontrol",
                    "date": (datetime.datetime.now() - datetime.timedelta(days=2)).isoformat(),
                    "matches": [stock.lower(), "outlook", "analysts"],
                    "relevance_score": 12
                })
                
                mock_response = f"Recent market movements for {stock} appear to be driven by a combination of company-specific developments and broader market trends. Analysts have noted changes in the outlook based on latest quarterly results and industry dynamics. Institutional investor activity also suggests shifting sentiment around this stock."
            
            # If no specific stock was found, provide a general market response
            if not mock_sources:
                mock_sources = [
                    {
                        "title": "Markets end higher for third day",
                        "source": "Economic Times",
                        "date": datetime.datetime.now().isoformat(),
                        "matches": ["market", "higher"],
                        "relevance_score": 10
                    },
                    {
                        "title": "Global factors influencing Indian markets",
                        "source": "Business Standard",
                        "date": (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat(),
                        "matches": ["global", "market", "indian"],
                        "relevance_score": 9
                    }
                ]
                mock_response = "Based on recent market trends, there has been generally positive sentiment driven by a combination of domestic economic indicators and global market cues. Specific sectors showing strength include banking, IT, and pharmaceuticals, while some consumer sectors have faced challenges. Investor focus remains on upcoming economic data and corporate earnings."
            
        return {
            "question": question,
            "answer": mock_response,
            "sources": mock_sources,
            "source_files": ["mock_data_file.json"],
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
            "source_files": [],
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
    """Generate analysis for a stock based on recent news with enhanced NLP context."""
    if OFFLINE_MODE:
        # Return mock data in offline mode with stock-specific analysis
        mock_sources = []
        mock_analysis = ""
        
        # Define specific responses for popular stocks
        stock_responses = {
            "TCS": {
                "analysis": "TCS has demonstrated consistent performance in recent quarters, maintaining its position as a leader in the IT services sector. The company's focus on digital transformation initiatives and cloud services has been well-received by clients, contributing to a healthy order book. Recent deals, particularly in the banking and financial services vertical, indicate continued business momentum. Market sentiment around TCS remains positive due to its strong execution capabilities and resilient business model.",
            "sources": [
                {
                        "title": "TCS reports 8% growth in Q1 revenue",
                        "source": "Economic Times",
                        "date": datetime.datetime.now().isoformat(),
                        "matches": ["tcs", "revenue", "growth", "quarter"],
                        "relevance_score": 15
                    },
                    {
                        "title": "TCS wins $200 million cloud transformation deal",
                        "source": "Business Standard",
                        "date": (datetime.datetime.now() - datetime.timedelta(days=5)).isoformat(),
                        "matches": ["tcs", "deal", "cloud", "transformation"],
                        "relevance_score": 14
                    },
                    {
                        "title": "IT sector outlook improving; TCS, Infosys top picks",
                        "source": "Mint",
                        "date": (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat(),
                        "matches": ["tcs", "it", "outlook"],
                        "relevance_score": 10
                    }
                ]
            },
            "RELIANCE": {
                "analysis": "Reliance Industries continues to execute well across its diverse business segments. The retail division is showing strong growth through both organic expansion and strategic acquisitions. In the telecom segment, Jio maintains its subscriber growth momentum while expanding its 5G footprint. The traditional O2C (oil-to-chemicals) business benefits from favorable refining margins. Recent initiatives in renewable energy signal the company's long-term strategic shift, which has been viewed positively by investors and analysts.",
                "sources": [
                    {
                        "title": "Reliance Retail acquires logistics startup to strengthen e-commerce",
                        "source": "Economic Times",
                        "date": datetime.datetime.now().isoformat(),
                        "matches": ["reliance", "retail", "acquisition", "ecommerce"],
                        "relevance_score": 15
                    },
                    {
                        "title": "Reliance Jio 5G now available in 200 cities",
                        "source": "Financial Express",
                        "date": (datetime.datetime.now() - datetime.timedelta(days=3)).isoformat(),
                        "matches": ["reliance", "jio", "5g"],
                        "relevance_score": 13
                    },
                    {
                        "title": "Reliance Industries invests $10 billion in clean energy",
                        "source": "Business Standard",
                        "date": (datetime.datetime.now() - datetime.timedelta(days=10)).isoformat(),
                        "matches": ["reliance", "energy", "clean", "investment"],
                        "relevance_score": 12
                    }
                ]
            },
            "INFY": {
                "analysis": "Infosys has been showing improved performance, supported by large deal wins and expanded digital offerings. The company's investments in AI and cloud capabilities are starting to yield results through higher-value contracts. While there are some concerns about margins due to increased hiring and compensation costs, the overall growth trajectory remains positive. The management's upward revision of revenue guidance reflects confidence in the demand environment despite macroeconomic uncertainties.",
                "sources": [
                    {
                        "title": "Infosys bags $1.5 billion deal from global client",
                        "source": "Economic Times",
                        "date": datetime.datetime.now().isoformat(),
                        "matches": ["infosys", "deal", "global", "client"],
                        "relevance_score": 15
                    },
                    {
                        "title": "Infosys Q1: Revenue growth beats estimates, margin pressure continues",
                        "source": "Mint",
                        "date": (datetime.datetime.now() - datetime.timedelta(days=4)).isoformat(),
                        "matches": ["infosys", "revenue", "growth", "margin"],
                        "relevance_score": 14
                    },
                    {
                        "title": "Infosys launches new AI platform for enterprise clients",
                        "source": "Business Standard",
                        "date": (datetime.datetime.now() - datetime.timedelta(days=6)).isoformat(),
                        "matches": ["infosys", "ai", "platform", "enterprise"],
                        "relevance_score": 11
                    }
                ]
            },
            "HDFCBANK": {
                "analysis": "HDFC Bank continues to deliver strong performance with robust loan growth, particularly in the retail segment. The successful merger with HDFC Ltd has created a financial powerhouse with expanded capabilities. While there was some short-term impact on margins due to the integration, the long-term benefits of the merger are expected to drive sustainable growth. The bank's digital initiatives and expansion into smaller cities are supporting its market share gains across various product segments.",
                "sources": [
                    {
                        "title": "HDFC Bank reports 20% growth in retail loans",
                        "source": "Economic Times",
                        "date": datetime.datetime.now().isoformat(),
                        "matches": ["hdfc", "bank", "loan", "retail", "growth"],
                        "relevance_score": 15
                    },
                    {
                        "title": "HDFC Bank-HDFC merger synergies starting to show results",
                        "source": "Financial Express",
                        "date": (datetime.datetime.now() - datetime.timedelta(days=5)).isoformat(),
                        "matches": ["hdfc", "bank", "merger", "synergies"],
                        "relevance_score": 14
                    },
                    {
                        "title": "HDFC Bank expands rural banking initiative to 5,000 villages",
                        "source": "Business Standard",
                        "date": (datetime.datetime.now() - datetime.timedelta(days=8)).isoformat(),
                        "matches": ["hdfc", "bank", "rural", "expansion"],
                        "relevance_score": 10
                    }
                ]
            },
            "ICICIBANK": {
                "analysis": "ICICI Bank has emerged as one of the top performers in the banking sector, delivering consistent growth in advances and deposits. The bank's focus on digital banking and operational efficiency has resulted in improved return ratios and asset quality metrics. The retail lending business remains strong, while the corporate book is showing signs of healthy growth. Management's execution capability and the bank's robust risk management framework have been key factors in its outperformance relative to peers.",
                "sources": [
                    {
                        "title": "ICICI Bank Q1 profit rises 35%, asset quality improves",
                        "source": "Economic Times",
                        "date": datetime.datetime.now().isoformat(),
                        "matches": ["icici", "bank", "profit", "asset", "quality"],
                        "relevance_score": 15
                    },
                    {
                        "title": "ICICI Bank digital transactions grow 40% year-on-year",
                        "source": "Business Standard",
                        "date": (datetime.datetime.now() - datetime.timedelta(days=6)).isoformat(),
                        "matches": ["icici", "bank", "digital", "transactions"],
                        "relevance_score": 12
                    },
                    {
                        "title": "Banking sector outlook positive; ICICI Bank top pick: Analysts",
                        "source": "Mint",
                        "date": (datetime.datetime.now() - datetime.timedelta(days=3)).isoformat(),
                        "matches": ["icici", "bank", "outlook", "analyst"],
                        "relevance_score": 11
                    }
                ]
            },
            "JYOTHYLAB": {
                "analysis": "Jyothy Labs has been showing improved performance driven by its focus on premium personal care and home care products. The company's rural expansion strategy is yielding results, with increased market penetration across key categories. Recent product innovations and effective marketing campaigns have helped in gaining market share from larger competitors. While input cost inflation remains a concern, the company has managed to partially offset it through price increases and operational efficiencies.",
                "sources": [
                    {
                        "title": "Jyothy Labs reports double-digit volume growth in Q1",
                        "source": "Economic Times",
                        "date": datetime.datetime.now().isoformat(),
                        "matches": ["jyothy", "labs", "volume", "growth"],
                        "relevance_score": 15
                    },
                    {
                        "title": "Jyothy Labs expands premium home care portfolio",
                        "source": "Business Standard",
                        "date": (datetime.datetime.now() - datetime.timedelta(days=5)).isoformat(),
                        "matches": ["jyothy", "labs", "premium", "home", "care"],
                        "relevance_score": 13
                    },
                    {
                        "title": "Rural demand improving for FMCG companies: Report",
                        "source": "Mint",
                        "date": (datetime.datetime.now() - datetime.timedelta(days=2)).isoformat(),
                        "matches": ["rural", "demand", "fmcg"],
                        "relevance_score": 8
                    }
                ]
            }
        }
        
        # Get stock-specific response if available
        if symbol in stock_responses:
            mock_analysis = stock_responses[symbol]["analysis"]
            mock_sources = stock_responses[symbol]["sources"]
        else:
            # Create generic response for other stocks
            mock_analysis = f"Based on recent market trends and news, {symbol} has been showing movement influenced by both sector-specific factors and broader market sentiment. Analysts have mixed views on the stock's near-term prospects, with some pointing to potential growth opportunities while others express concerns about valuation. Recent developments in the company's business operations and financial results have been key factors driving investor sentiment."
            
            # Generate generic sources
            mock_sources = [
                {
                    "title": f"{symbol} Q1 results: Mixed performance amid challenging environment",
                    "source": "Economic Times",
                    "date": datetime.datetime.now().isoformat(),
                    "matches": [symbol.lower(), "results", "performance"],
                    "relevance_score": 15
                },
                {
                    "title": f"Analysts remain cautious on {symbol} after recent rally",
                    "source": "Moneycontrol",
                    "date": (datetime.datetime.now() - datetime.timedelta(days=3)).isoformat(),
                    "matches": [symbol.lower(), "analysts", "cautious", "rally"],
                    "relevance_score": 12
                },
                {
                    "title": f"{symbol} announces expansion plans to boost growth",
                    "source": "Business Standard",
                    "date": (datetime.datetime.now() - datetime.timedelta(days=5)).isoformat(),
                    "matches": [symbol.lower(), "expansion", "growth"],
                    "relevance_score": 10
                }
            ]
        
        # Customize question if provided
        question_text = question if question else f"Why is {symbol} stock price moving? What are the recent developments?"
        
        return {
            "symbol": symbol,
            "company_name": f"{symbol}",
            "question": question_text,
            "answer": mock_analysis,
            "sources": mock_sources,
            "source_files": ["stock_data.csv", f"{symbol}_analysis.json"],
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
            "source_files": [],
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
            "source_files": [],
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
    
    # More intuitive prompts
    st.markdown("""
    Ask questions about stocks, market indices, or specific sectors. Try to include specific names for better results:
    
    - About stocks: "Why is **TCS** stock up today?" or "What's happening with **RELIANCE**?"
    - About indices: "Why did **Nifty** fall yesterday?" or "What caused the **Sensex** movement?"
    - About sectors: "How is the **Banking** sector performing?" or "Latest news in **Pharma** sector?"
    """)
    
    question = st.text_input("Enter your question:", placeholder="E.g., Why is Nifty down today? What's happening with TCS stock?")
    
    if st.button("Get Answer", type="primary"):
        if question:
            with st.spinner("Finding answer..."):
                result = answer_question(question)
                
                if result:
                    st.markdown(f"### Answer")
                    st.markdown(result["answer"])
                    
                    # Create tabs for sources and data
                    source_tabs = st.tabs(["News Sources", "Data Sources"])
                    
                    with source_tabs[0]:
                        # Display source articles with better formatting
                        if result.get("sources") and len(result["sources"]) > 0:
                            for i, source in enumerate(result["sources"]):
                                with st.container():
                                    col1, col2 = st.columns([5, 1])
                                    with col1:
                                        st.subheader(source.get('title', ''))
                                        st.caption(f"{source.get('source', '')} - {format_date(str(source.get('date', '')))}")
                                        
                                        # Display relevance information
                                        if "relevance_score" in source:
                                            relevance = source["relevance_score"]
                                            # Show stars based on relevance
                                            stars = "⭐" * min(5, max(1, int(relevance / 5)))
                                            st.caption(f"Relevance: {stars}")
                                        
                                        # Display matching terms if available
                                        if "matches" in source and source["matches"]:
                                            matches = ", ".join(source["matches"])
                                            st.caption(f"Matched terms: {matches}")
                                    
                                    if i < len(result["sources"]) - 1:
                                        st.divider()
                        else:
                            st.info("No relevant news sources found for this query.")
                    
                    with source_tabs[1]:
                        # Display source files
                        if result.get("source_files") and len(result.get("source_files")) > 0:
                            for source_file in result["source_files"]:
                                st.markdown(f"- `{source_file}`")
                        else:
                            st.info("No data source files available.")
        else:
            st.warning("Please enter a question")
    
    st.divider()
    
    # Better example questions with clearer categories
    st.subheader("Example Questions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Stock-specific**")
        stock_questions = [
            "Why did Reliance Industries stock move today?",
            "What's happening with TCS shares?",
            "Latest news about HDFC Bank",
            "Why is Jyothy Labs up today?"
        ]
        
        for q in stock_questions:
            if st.button(q, key=f"stock_q_{q}"):
                st.session_state.question = q
                st.rerun()
    
    with col2:
        st.markdown("**Market & Sector**")
        market_questions = [
        "What happened to Nifty this week?",
            "Why is the Banking sector down?",
            "Any news affecting IT stocks?",
            "What's driving Sensex today?"
    ]
        for q in market_questions:
            if st.button(q, key=f"market_q_{q}"):
                st.session_state.question = q
                st.rerun()
        st.header("Stock Symbol Lookup & Analysis")
    # More intuitive description
    st.markdown("Enter a stock symbol to get detailed analysis and relevant news specifically about that company.")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        stock_symbol = st.text_input("Enter stock symbol:", placeholder="E.g., RELIANCE, INFY, TCS")
    
    with col2:
        lookup_button = st.button("Lookup Stock", type="primary")
    
    # Example symbols with better layout
    st.caption("Quick access to popular stocks:")
    
    # Group stocks by sectors for better organization
    stock_sectors = {
        "Technology": ["TCS", "INFY", "WIPRO"],
        "Banking": ["HDFCBANK", "ICICIBANK", "SBIN"],
        "Energy & Conglomerates": ["RELIANCE", "ADANIENT"],
        "Consumer": ["JYOTHYLAB", "ITC", "HINDUNILVR"]
    }
    
    # Create tabs for sectors
    sector_tabs = st.tabs(list(stock_sectors.keys()))
    
    for i, (sector, stocks) in enumerate(stock_sectors.items()):
        with sector_tabs[i]:
            cols = st.columns(len(stocks))
            for j, symbol in enumerate(stocks):
                    with cols[j]:
                            if st.button(symbol, key=f\"example_symbol_{symbol}\"): # type: ignore
                                    st.session_state.stock_symbol = symbol
                                    st.rerun()
    custom_question = st.text_input(
        "Ask a specific question about this stock (optional):", 
        placeholder="E.g., Why is this stock price changing? What are the recent developments?"
    )
    
    if lookup_button or ('stock_symbol' in st.session_state and st.session_state.stock_symbol == stock_symbol):
        if stock_symbol:
            # Store current symbol in session state
            st.session_state.stock_symbol = stock_symbol
            
            # Display stock information & news with improved layout
            with st.spinner("Loading stock information..."):
                # Display stock information & news
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    with st.spinner("Loading stock news..."):
                        news_data = get_stock_news(stock_symbol)
                    
                    if "error" in news_data:
                        st.error(news_data["error"])
                    else:
                            # Display news with better formatting
                        st.markdown(f"### Recent News for {news_data.get('company_name', stock_symbol)}")
                        
                        if 'news' in news_data and news_data['news']:
                            # Create tabs for different news sources if available
                            news_sources = list(set([article.get('source', 'Unknown') for article in news_data['news']]))
                            
                            if len(news_sources) > 1:
                                news_tabs = st.tabs(["All"] + news_sources)
                                
                                # All news tab
                                with news_tabs[0]:
                                    for article in news_data['news']:
                                            with st.container():
                                                st.subheader(article.get('title', ''))
                                                st.caption(f"{article.get('source', '')} - {format_date(article.get('date', ''))}")
                                                # Show snippet of content if available
                                                content = article.get('content', '')
                                                if content:
                                                    st.markdown(content[:300] + ('...' if len(content) > 300 else ''))
                                                st.divider()
                                
                                # Source-specific tabs
                                for i, source in enumerate(news_sources):
                                    with news_tabs[i+1]:
                                        source_news = [article for article in news_data['news'] if article.get('source') == source]
                                        for article in source_news:
                                                with st.container():
                                                    st.subheader(article.get('title', ''))
                                                    st.caption(f"{format_date(article.get('date', ''))}")
                                                    # Show snippet of content if available
                                                    content = article.get('content', '')
                                                    if content:
                                                        st.markdown(content[:300] + ('...' if len(content) > 300 else ''))
                                                    st.divider()
                            else:
                                    # Just show all news with better formatting
                                for article in news_data['news']:
                                        with st.container():
                                            st.subheader(article.get('title', ''))
                                            st.caption(f"{article.get('source', '')} - {format_date(article.get('date', ''))}")
                                            # Show snippet of content if available
                                            content = article.get('content', '')
                                            if content:
                                                st.markdown(content[:300] + ('...' if len(content) > 300 else ''))
                                            st.divider()
                        else:
                            st.info("No recent news found for this stock symbol")
            
            with col2:
                with st.spinner("Loading stock data..."):
                        # Get basic stock information with improved display
                    stocks = search_stocks(stock_symbol)
                    
                    if stocks:
                        stock = stocks[0]
                        # Use a card-like display
                        with st.container():
                            st.markdown(f"### {stock.get('name', '')}")
                            
                            # Display basic info in a more organized way
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("**Symbol**")
                                st.markdown(stock.get('symbol', ''))
                                st.markdown("**Sector**")
                                st.markdown(stock.get('sector', 'Unknown'))
                                
                                with col2:
                                    st.markdown("**ISIN**")
                                    st.markdown(stock.get('isin', ''))
                                    # Add a placeholder for market cap or other info
                                    st.markdown("**Exchange**")
                                    st.markdown("NSE/BSE")
                                
                            # Display price chart with better title
                        st.markdown("### Price Trend")
                        
                            # Create a simple placeholder chart with better styling
                        dates = pd.date_range(start='2023-01-01', periods=30, freq='D')
                        prices = np.random.normal(loc=0.1, scale=0.02, size=30).cumsum() + 100
                        
                        df = pd.DataFrame({
                            'Date': dates,
                            'Price': prices
                        })
                        
                        st.line_chart(df.set_index('Date'))
                    else:
                        st.warning("Stock information not found")
            
            # Improved stock analysis section
            st.markdown("### Stock Analysis")
            
            # Use expander for analysis to save space
            with st.spinner("Generating stock analysis..."):
                analysis = analyze_stock(stock_symbol, custom_question)
                
                if "error" in analysis:
                    st.error(analysis["error"])
                else:
                    # Display analysis with better formatting
                    question_display = analysis.get('question')
                    answer_display = analysis.get('answer', 'No analysis available')
                    
                    # Create a card-like container for the analysis
                    with st.container():
                        st.markdown(f"**Question:** {question_display}")
                        st.markdown(f"**Analysis:** {answer_display}")
                    
                    # Create tabs for sources
                    if analysis.get("sources") or analysis.get("source_files"):
                        source_tabs = st.tabs(["News Sources", "Data Sources"])
                        with source_tabs[0]:
                            if analysis.get("sources"):
                                for source in analysis["sources"]:
                                    with st.container():
                                        st.markdown(f"**{source.get('title', '')}**")
                                        st.caption(f"{source.get('source', '')} - {format_date(str(source.get('date', '')))}")
                                        
                                        # Display matching terms if available
                                        if "matches" in source and source["matches"]:
                                            matches = ", ".join(source["matches"])
                                            st.caption(f"Matched terms: {matches}")
                                        
                                        # Display relevance score if available
                                        if "relevance_score" in source:
                                            relevance = source["relevance_score"]
                                            # Show stars based on relevance
                                            stars = "⭐" * min(5, max(1, int(relevance / 5)))
                                            st.caption(f"Relevance: {stars}")
                                            st.divider()
                                        else:
                                            st.info("No relevant news sources found.")
                                            
                                            with source_tabs[1]:
                                                if analysis.get("source_files") and len(analysis["source_files"]) > 0:
                                                    for source_file in analysis["source_files"]:
                                                        st.markdown(f"- `{source_file}`")
                                                else:
                                                    st.info("No data source files available.")
                        st.info("Note: This analysis uses pattern matching and simulated data. For higher quality analysis, connect to the API backend.")
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

st.markdown("---")
st.markdown("© 2023 NewsSense | Built for MyFi Hackathon Challenge | All rights reserved.", unsafe_allow_html=True)