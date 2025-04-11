#!/usr/bin/env python
"""
Simplified offline version of NewsSense for demonstration.
This script provides a minimal Streamlit UI with mock data.
"""
import streamlit as st
import pandas as pd
import datetime
import random

# Mock data generation
def get_mock_headlines(num=20):
    """Generate mock headlines."""
    companies = ["Reliance", "TCS", "HDFC Bank", "Infosys", "ITC", "SBI", "Airtel", "Wipro", "ICICI Bank", "HUL"]
    sources = ["Economic Times", "Business Standard", "Moneycontrol", "Financial Express", "Mint"]
    dates = [(datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(10)]
    headlines = []
    
    templates = [
        "{company} reports {change} in quarterly profits",
        "{company} announces new {initiative} initiative",
        "{company} shares {direction} on market optimism",
        "Analysts remain {sentiment} on {company} outlook",
        "{company} plans expansion in {area} sector",
        "{company} CEO discusses future growth strategy",
        "{company} stock sees {movement} volume trading",
        "{company} partners with {partner} for new venture"
    ]
    
    changes = ["5% increase", "10% growth", "slight decline", "steady growth", "record growth"]
    initiatives = ["tech", "green", "digital", "expansion", "cost-cutting"]
    directions = ["up 2%", "down 1.5%", "rally 3%", "slip marginally", "surge 4%"]
    sentiments = ["bullish", "cautious", "optimistic", "neutral", "positive"]
    areas = ["technology", "healthcare", "retail", "finance", "manufacturing"]
    movements = ["high", "increased", "record", "lower", "volatile"]
    partners = ["Google", "Microsoft", "Amazon", "IBM", "local startups"]
    
    for i in range(num):
        template = random.choice(templates)
        company = random.choice(companies)
        headline = {
            "title": template.format(
                company=company,
                change=random.choice(changes),
                initiative=random.choice(initiatives),
                direction=random.choice(directions),
                sentiment=random.choice(sentiments),
                area=random.choice(areas),
                movement=random.choice(movements),
                partner=random.choice(partners)
            ),
            "source": random.choice(sources),
            "date": random.choice(dates),
            "url": "#",
            "relevance_score": random.randint(1, 10)
        }
        headlines.append(headline)
    
    return headlines

def answer_financial_question(question):
    """Generate mock answers to financial questions."""
    # Basic patterns for different question types
    answers = {
        "market": "The markets have been showing mixed trends recently, with some volatility due to global factors and domestic economic indicators. Several key stocks in the technology and banking sectors have reported quarterly results above expectations.",
        "stock": "This stock has been influenced by its recent quarterly performance and broader sector trends. Analyst recommendations remain mixed, with some pointing to potential growth opportunities while others caution about market headwinds.",
        "sector": "The sector has been performing in line with broader market trends, though with some company-specific variations. Recent policy announcements have created both opportunities and challenges for companies in this space.",
        "nifty": "Nifty has been experiencing some volatility influenced by global market cues, foreign institutional investor activity, and domestic economic data. Key sectors contributing to recent movements include banking, IT, and energy.",
        "sensex": "Sensex movements have been driven by a mix of global factors and domestic developments. Recent earnings reports from index heavyweights have influenced investor sentiment, along with macroeconomic indicators and policy announcements.",
        "reliance": "Reliance has been focusing on its digital and retail segments, which are showing strong growth potential. The company's energy business continues to generate consistent cash flow, supporting its expansion plans in new areas.",
        "tcs": "TCS has been performing steadily with strong order books and client additions. The company's focus on digital transformation services and cloud adoption is aligned with current market demands.",
        "hdfc": "HDFC Bank has shown resilience in its asset quality metrics compared to peers. The retail lending segment continues to be a strong performer, while the bank is also expanding its digital offerings.",
        "why": "The movement is attributable to a combination of company-specific developments, sector trends, and broader market conditions. Recent announcements regarding business strategy and quarterly performance have influenced investor sentiment."
    }
    
    # Find the most relevant answer based on keywords in the question
    for key, answer in answers.items():
        if key.lower() in question.lower():
            return answer
    
    # Default answer if no pattern matches
    return "Based on recent market data and news, there appear to be multiple factors influencing this financial situation. Company-specific developments, sector trends, and broader market conditions all play a role in the current scenario."

# Streamlit App
def main():
    """Run the simplified Streamlit app."""
    st.set_page_config(
        page_title="NewsSense Demo",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Sidebar
    with st.sidebar:
        st.title("NewsSense")
        st.subheader("Demo Mode")
        
        st.warning("⚠️ Running in demo mode with simulated data")
        
        st.markdown("""
        This is a simplified demo version of NewsSense.
        
        The complete version:
        1. Scrapes financial news from multiple sources
        2. Processes them with advanced NLP
        3. Uses Gemini AI to generate insights
        4. Provides stock-specific analysis
        """)
    
    # Main content area
    st.title("Financial News Analysis")
    
    # Create tabs
    tab1, tab2 = st.tabs(["💬 Ask Question", "🔍 Stock Analysis"])
    
    # Tab 1: General financial questions
    with tab1:
        st.header("Ask a financial question")
        
        # Question input
        question = st.text_input("Enter your question:", 
                               placeholder="E.g., Why is Nifty down today?")
        
        if st.button("Get Answer", type="primary", key="ask_btn"):
            if question:
                with st.spinner("Analyzing your question..."):
                    answer = answer_financial_question(question)
                    
                    # Display the answer
                    st.markdown("### Answer")
                    st.write(answer)
                    
                    # Display some mock sources
                    st.markdown("### News Sources")
                    mock_sources = get_mock_headlines(5)
                    for source in mock_sources:
                        st.markdown(f"- **{source.get('title', '')}** - {source.get('source', '')} ({source.get('date', '')})")
            else:
                st.warning("Please enter a question first.")
        
        # Example questions
        st.markdown("### Example Questions")
        example_questions = [
            "Why is Reliance stock price changing?",
            "What factors are affecting the IT sector?",
            "How is the banking sector performing?",
            "What is happening with Nifty today?"
        ]
        
        cols = st.columns(2)
        for i, q in enumerate(example_questions):
            with cols[i % 2]:
                if st.button(q, key=f"example_{i}"):
                    # Use st.experimental_set_query_params to set the URL parameter
                    st.experimental_set_query_params(question=q)
                    st.rerun()
    
    # Tab 2: Stock-specific analysis
    with tab2:
        st.header("Stock Analysis")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            stock_symbol = st.text_input("Enter stock symbol:", 
                                       placeholder="E.g., RELIANCE, TCS, HDFC")
        with col2:
            analyze_btn = st.button("Analyze", type="primary")
        
        # Optional custom question
        custom_q = st.text_input("Custom question (optional):",
                               placeholder="E.g., Why did this stock drop recently?")
        
        # Example stock symbols
        st.caption("Try these examples:")
        example_symbols = ["RELIANCE", "TCS", "INFY", "HDFC", "ITC"]
        symbol_cols = st.columns(len(example_symbols))
        
        for i, symbol in enumerate(example_symbols):
            with symbol_cols[i]:
                if st.button(symbol, key=f"sym_{symbol}"):
                    st.session_state.selected_symbol = symbol
                    st.rerun()
        
        # If symbol is selected via button or manually entered
        if 'selected_symbol' in st.session_state:
            stock_symbol = st.session_state.selected_symbol
        
        # Perform analysis when requested
        if analyze_btn and stock_symbol:
            with st.spinner(f"Analyzing {stock_symbol}..."):
                # Mock stock information
                stocks = {
                    "RELIANCE": "Reliance Industries Ltd",
                    "TCS": "Tata Consultancy Services Ltd",
                    "HDFC": "HDFC Bank Ltd",
                    "INFY": "Infosys Ltd",
                    "ITC": "ITC Ltd"
                }
                company_name = stocks.get(stock_symbol.upper(), stock_symbol)
                
                # Generate mock question and answer
                question = custom_q or f"Why is {stock_symbol} stock price changing recently?"
                answer = answer_financial_question(question)
                
                # Generate mock news related to the stock
                mock_news = get_mock_headlines(10)
                # Filter to include company name in some headlines
                for i in range(min(5, len(mock_news))):
                    mock_news[i]["title"] = mock_news[i]["title"].replace(
                        mock_news[i]["title"].split()[0], company_name)
                    mock_news[i]["relevance_score"] = random.randint(5, 10)
                
                # Sort by relevance
                mock_news.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
                
                # Display analysis
                st.markdown(f"## Analysis for {company_name} ({stock_symbol})")
                
                col1, col2 = st.columns([3, 2])
                
                with col1:
                    st.markdown("### Key Insights")
                    st.markdown(f"**Question**: {question}")
                    st.markdown(f"**Answer**: {answer}")
                
                with col2:
                    st.markdown("### Recent News")
                    for article in mock_news[:5]:
                        st.markdown(f"**{article.get('title', '')}**")
                        st.caption(f"{article.get('source', '')} - {article.get('date', '')}")
                        st.markdown("---")
                
                # Show news in a dataframe
                if mock_news:
                    st.markdown("### All Relevant News")
                    news_df = pd.DataFrame([{
                        "Title": n.get("title", ""),
                        "Source": n.get("source", ""),
                        "Date": n.get("date", ""),
                        "Relevance": n.get("relevance_score", 0)
                    } for n in mock_news])
                    
                    st.dataframe(news_df, use_container_width=True)

if __name__ == "__main__":
    main() 