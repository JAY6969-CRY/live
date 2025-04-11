 #!/usr/bin/env python
"""
Direct integration script for NewsSense to connect NLP with scraped data.
"""
import os
import sys
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import necessary components
from src.data.scrapers.scraper_manager import ScraperManager
from src.data.financial.stock_data import StockDataRetriever
from src.models.news_processor import NewsProcessor
from src.models.financial_qa import FinancialQA

# Direct integration with NLP and scrapers
class DirectNewsSense:
    def __init__(self):
        """Initialize all components directly."""
        print("Initializing NewsSense components...")
        
        # Initialize scrapers
        self.scraper_manager = ScraperManager()
        self.stock_data = StockDataRetriever()
        self.news_processor = NewsProcessor()
        
        # Initialize QA system with Gemini API key
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            print(f"Using Gemini API key: {api_key[:5]}...{api_key[-4:]}")
            self.qa_system = FinancialQA(api_key=api_key)
        else:
            print("No Gemini API key found. Will use pattern matching for analysis.")
            self.qa_system = FinancialQA()
    
    def answer_question(self, question):
        """Process a user question using the NLP system."""
        # Get the answer
        answer = self.qa_system.answer_question(question)
        
        # Get relevant context and entities
        entity_matches = self.qa_system._extract_entities_from_question(question)
        
        # Get relevant news sources
        sources = []
        for article in self.qa_system.news_articles[:5]:
            # Check if article mentions any entity from the question
            if any(entity in article.get("title", "") 
                  for entity in entity_matches.get("companies", []) + 
                              entity_matches.get("indices", []) + 
                              entity_matches.get("sectors", [])):
                sources.append({
                    "title": article.get("title", ""),
                    "source": article.get("source", ""),
                    "date": article.get("date", "")
                })
        
        return {
            "question": question,
            "answer": answer,
            "sources": sources,
            "entities": entity_matches,
            "is_simulated": self.qa_system.llm is None
        }
    
    def analyze_stock(self, symbol, custom_question=None):
        """Analyze a specific stock with optional custom question."""
        # Get stock information
        stock_info = self.stock_data.search_stocks(symbol)
        company_name = stock_info[0]["name"] if stock_info else symbol
        
        # Formulate the question
        question = custom_question or f"Why is {symbol} stock price changing recently?"
        if company_name not in question and symbol not in question:
            question = f"{question} for {company_name} ({symbol})"
        
        # Get the analysis
        answer = self.qa_system.answer_question(question)
        
        # Get stock-specific news
        news = []
        headlines = self.scraper_manager.scrape_all_headlines(limit=20)
        
        for headline in headlines:
            # Process headline to extract entities
            processed = self.news_processor.process_headline(headline)
            
            # Check if company is mentioned in headline or entities
            if (company_name in headline.get("title", "") or 
                symbol.upper() in headline.get("title", "") or
                company_name in processed.get("entities", {}).get("companies", [])):
                
                # Calculate relevance score
                score = 0
                if company_name in headline.get("title", ""):
                    score += 5
                if symbol.upper() in headline.get("title", ""):
                    score += 3
                
                # Add keyword matching scores
                keywords = ["result", "profit", "loss", "quarterly", "earning", "announce", 
                           "dividend", "growth", "target", "update"]
                for keyword in keywords:
                    if keyword in headline.get("title", "").lower():
                        score += 1
                
                # Add to news with score
                headline["relevance_score"] = score
                news.append(headline)
        
        # Sort by relevance score
        news.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        return {
            "symbol": symbol,
            "company_name": company_name,
            "question": question,
            "answer": answer,
            "news": news[:10],  # Top 10 most relevant news
            "is_simulated": self.qa_system.llm is None
        }


# Streamlit App
def main():
    """Run the Streamlit app with direct integration."""
    st.set_page_config(
        page_title="NewsSense Direct",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize or reuse the system
    if 'system' not in st.session_state:
        with st.spinner("Initializing NewsSense system..."):
            st.session_state.system = DirectNewsSense()
    
    system = st.session_state.system
    
    # Sidebar
    with st.sidebar:
        st.title("NewsSense")
        st.subheader("Direct Integration")
        
        # Gemini API status
        if system.qa_system.llm:
            st.success("✓ Using Gemini API for enhanced NLP")
        else:
            st.warning("⚠️ Using pattern matching (Gemini API key not set)")
        
        st.markdown("""
        This version directly connects NLP with scraped data.
        
        How it works:
        1. We scrape financial news from sources
        2. Process them with NLP to extract entities and insights
        3. Match your query to relevant articles
        4. Generate answers based on the matched data
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
                    result = system.answer_question(question)
                    
                    # Display the answer
                    st.markdown("### Answer")
                    st.write(result["answer"])
                    
                    # Display the sources
                    if result["sources"]:
                        st.markdown("### News Sources")
                        for source in result["sources"]:
                            st.markdown(f"- **{source.get('title', '')}** - {source.get('source', '')} ({source.get('date', '')})")
                    
                    # Show entities detected
                    entities = result["entities"]
                    if any(entities.values()):
                        st.markdown("### Detected Entities")
                        entity_text = []
                        if entities.get("companies"):
                            entity_text.append(f"**Companies**: {', '.join(entities['companies'])}")
                        if entities.get("indices"):
                            entity_text.append(f"**Indices**: {', '.join(entities['indices'])}")
                        if entities.get("sectors"):
                            entity_text.append(f"**Sectors**: {', '.join(entities['sectors'])}")
                        
                        st.markdown(" | ".join(entity_text))
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
                    # This is a way to "fill" the text input with the example question
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
        example_symbols = ["RELIANCE", "TCS", "INFY", "HDFC", "JYOTHYLAB"]
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
                analysis = system.analyze_stock(stock_symbol, custom_q)
                
                # Display analysis
                st.markdown(f"## Analysis for {analysis['company_name']} ({analysis['symbol']})")
                
                col1, col2 = st.columns([3, 2])
                
                with col1:
                    st.markdown("### Key Insights")
                    st.markdown(f"**Question**: {analysis['question']}")
                    st.markdown(f"**Answer**: {analysis['answer']}")
                
                with col2:
                    if analysis["news"]:
                        st.markdown("### Recent News")
                        for article in analysis["news"][:5]:
                            st.markdown(f"**{article.get('title', '')}**")
                            st.caption(f"{article.get('source', '')} - {article.get('date', '')}")
                            st.markdown("---")
                
                # Additional data visualization could be added here
                
                # Show news in a more detailed view
                if analysis["news"]:
                    st.markdown("### All Relevant News")
                    news_df = pd.DataFrame([{
                        "Title": n.get("title", ""),
                        "Source": n.get("source", ""),
                        "Date": n.get("date", ""),
                        "Relevance": n.get("relevance_score", 0)
                    } for n in analysis["news"]])
                    
                    st.dataframe(news_df, use_container_width=True)


if __name__ == "__main__":
    import pandas as pd
    main()