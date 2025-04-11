 #!/usr/bin/env python
"""
Direct analysis script using NLP on the scraped data for NewsSense.

This script will process user queries, analyze them, and return results from scraped data.
No need for external API connections.
"""
import os
import sys
import json
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Make sure PYTHONPATH is set correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import necessary components
from src.data.scrapers.scraper_manager import ScraperManager
from src.data.financial.stock_data import StockDataRetriever
from src.models.news_processor import NewsProcessor
from src.models.financial_qa import FinancialQA

class DirectAnalysis:
    """Direct analysis using NLP on the scraped data."""
    
    def __init__(self):
        """Initialize the analysis components."""
        print("Initializing scraper components...")
        self.scraper_manager = ScraperManager()
        
        print("Initializing financial data retriever...")
        self.stock_data = StockDataRetriever()
        
        print("Initializing news processor...")
        self.news_processor = NewsProcessor()
        
        # Initialize QA system with API key if available
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            print(f"Initializing QA system with Gemini API key: {api_key[:5]}...{api_key[-4:]}")
            self.qa_system = FinancialQA(api_key=api_key)
        else:
            print("No Gemini API key found. Using pattern matching for analysis.")
            self.qa_system = FinancialQA()  # Will use simulated responses
        
        print("All components initialized!")
    
    def answer_question(self, question):
        """
        Answer a financial question using the processed news and data.
        
        Args:
            question: The question to answer
            
        Returns:
            Dictionary with the answer and sources
        """
        answer = self.qa_system.answer_question(question)
        
        # Get sources from relevant articles
        context = self.qa_system._get_relevant_context(question)
        entity_matches = self.qa_system._extract_entities_from_question(question)
        
        # Find related articles
        sources = []
        for article in self.qa_system.news_articles[:5]:
            # Match articles to entities in question
            if any(company in article.get("title", "") 
                  for company in entity_matches.get("companies", [])):
                sources.append({
                    "title": article.get("title", ""),
                    "source": article.get("source", ""),
                    "date": article.get("date", "")
                })
        
        return {
            "question": question,
            "answer": answer,
            "sources": sources,
            "is_simulated": self.qa_system.llm is None
        }
    
    def get_stock_analysis(self, symbol, question=None):
        """
        Get analysis for a specific stock symbol.
        
        Args:
            symbol: Stock symbol to analyze
            question: Optional specific question about the stock
            
        Returns:
            Dictionary with analysis and relevant news
        """
        # Get stock information
        stock_info = self.stock_data.search_stocks(symbol)
        company_name = stock_info[0]["name"] if stock_info else symbol
        
        # Create a specific question about this stock
        specific_question = question if question else f"Why is {symbol} stock price changing recently?"
        if company_name not in specific_question and symbol not in specific_question:
            specific_question = f"{specific_question} for {company_name} ({symbol})"
        
        # Get answer using the QA system
        answer = self.qa_system.answer_question(specific_question)
        
        # Get news specifically about this stock
        company_news = []
        
        # Scrape headlines with a broader scope
        headlines = self.scraper_manager.scrape_all_headlines(limit=20)
        
        # Process each headline to find relevant news
        for headline in headlines:
            # Process the headline to extract entities
            processed = self.news_processor.process_headline(headline)
            
            # Check for company name or symbol in headline or entities
            if (company_name in headline.get("title", "") or 
                symbol.upper() in headline.get("title", "") or
                company_name in processed.get("entities", {}).get("companies", [])):
                
                # Score based on relevance
                score = 0
                if company_name in headline.get("title", ""):
                    score += 5
                if symbol.upper() in headline.get("title", ""):
                    score += 3
                for keyword in ["results", "earnings", "profit", "loss", "announces", "acquisition"]:
                    if keyword in headline.get("title", "").lower():
                        score += 1
                
                # Add score to the news item
                headline["relevance_score"] = score
                company_news.append(headline)
        
        # Sort by relevance score
        company_news.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        # Clean up the sources for the response
        sources = []
        for article in company_news[:5]:
            sources.append({
                "title": article.get("title", ""),
                "source": article.get("source", ""),
                "date": article.get("date", ""),
                "relevance_score": article.get("relevance_score", 0)
            })
        
        return {
            "symbol": symbol,
            "company_name": company_name,
            "question": specific_question,
            "answer": answer,
            "sources": sources,
            "news": company_news[:10],  # Include top 10 relevant news items
            "is_simulated": self.qa_system.llm is None
        }


def main():
    """Main function to run Streamlit app directly connected to analysis engine."""
    st.set_page_config(
        page_title="NewsSense Direct Analysis",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize the analysis engine
    if 'analysis_engine' not in st.session_state:
        with st.spinner("Initializing analysis engine... This may take a moment."):
            st.session_state.analysis_engine = DirectAnalysis()
    
    analysis_engine = st.session_state.analysis_engine
    
    # Sidebar
    with st.sidebar:
        st.title("NewsSense")
        st.subheader("Direct Analysis Mode")
        
        st.markdown("""
        This mode connects directly to the analysis engine without requiring separate API services.
        
        Ask financial questions or analyze specific stocks using scraped news data.
        """)
    
    # Main content
    st.title("NewsSense Financial Analysis")
    
    # Create tabs
    tab1, tab2 = st.tabs(["💬 Ask Question", "🔍 Stock Analysis"])
    
    # Tab 1: General Questions
    with tab1:
        st.header("Ask a Financial Question")
        
        question = st.text_input("Enter your question:", placeholder="E.g., Why is Nifty down today?")
        
        if st.button("Get Answer", type="primary") or ('last_question' in st.session_state and st.session_state.last_question == question and question):
            if question:
                st.session_state.last_question = question
                
                with st.spinner("Analyzing..."):
                    result = analysis_engine.answer_question(question)
                    
                    st.subheader("Answer")
                    st.write(result["answer"])
                    
                    if result["sources"]:
                        st.subheader("Sources")
                        for source in result["sources"]:
                            st.markdown(f"- **{source.get('title', '')}** - {source.get('source', '')} ({source.get('date', '')})")
                    
                    if result["is_simulated"]:
                        st.info("Note: This answer is based on pattern matching. For advanced NLP analysis, set up the Gemini API key.")
            else:
                st.warning("Please enter a question.")
        
        # Example questions
        st.subheader("Example Questions")
        example_questions = [
            "Why did HDFC Bank stock drop yesterday?",
            "What is happening with the IT sector in India?",
            "How are oil prices affecting the market?",
            "What factors are influencing Nifty today?"
        ]
        
        for q in example_questions:
            if st.button(q, key=f"q_{q}"):
                st.session_state.last_question = q
                st.rerun()
    
    # Tab 2: Stock Analysis
    with tab2:
        st.header("Stock Symbol Analysis")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            stock_symbol = st.text_input("Enter stock symbol:", placeholder="E.g., RELIANCE, INFY, TCS")
        
        with col2:
            lookup_button = st.button("Analyze Stock", type="primary")
        
        # Custom question
        custom_question = st.text_input(
            "Ask a specific question (optional):",
            placeholder="E.g., Why is this stock price changing? What are the recent developments?"
        )
        
        # Example symbols
        st.caption("Try these examples:")
        example_symbols = ["RELIANCE", "TCS", "INFY", "ICICIBANK", "JYOTHYLAB"]
        
        cols = st.columns(len(example_symbols))
        for i, symbol in enumerate(example_symbols):
            with cols[i]:
                if st.button(symbol, key=f"sym_{symbol}"):
                    stock_symbol = symbol
                    st.session_state.last_symbol = symbol
                    st.rerun()
        
        if lookup_button or ('last_symbol' in st.session_state and st.session_state.last_symbol == stock_symbol and stock_symbol):
            if stock_symbol:
                st.session_state.last_symbol = stock_symbol
                
                with st.spinner(f"Analyzing {stock_symbol}..."):
                    result = analysis_engine.get_stock_analysis(stock_symbol, custom_question)
                    
                    st.subheader(f"Analysis for {result['company_name']} ({result['symbol']})")
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown("### Question")
                        st.write(result["question"])
                        
                        st.markdown("### Answer")
                        st.write(result["answer"])
                        
                        if result["sources"]:
                            st.markdown("### News Sources")
                            for source in result["sources"]:
                                st.markdown(f"- **{source.get('title', '')}** - {source.get('source', '')} ({source.get('date', '')})")
                    
                    with col2:
                        if result["news"]:
                            st.markdown("### Related News")
                            for article in result["news"][:5]:
                                st.markdown(f"**{article.get('title', '')}**")
                                st.markdown(f"*{article.get('source', '')}*")
                                st.markdown("---")
                    
                    if result["is_simulated"]:
                        st.info("Note: This analysis is based on pattern matching. For advanced NLP analysis, set up the Gemini API key.")
            else:
                st.warning("Please enter a stock symbol.")


if __name__ == "__main__":
    main()