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

# Utility functions
def format_date(date_str):
    """Format date string for display."""
    try:
        dt = datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%d %b %Y, %H:%M")
    except:
        return date_str

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
                    st.markdown(f"**Source:** {source.get('source', 'Unknown')}")
                    st.markdown(f"**Date:** {format_date(source.get('date', 'Unknown'))}")
                    
                    # Show relevance score and matches if available
                    if 'relevance_score' in source:
                        relevance = source.get('relevance_score', 0)
                        stars = "⭐" * min(5, max(1, int(relevance / 5)))
                        st.markdown(f"**Relevance:** {stars} ({relevance:.1f})")
                    
                    if 'matches' in source and source['matches']:
                        st.markdown(f"**Matched terms:** {', '.join(source['matches'])}")
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