"""
Flask API for NewsSense stock symbol lookup and news analysis.
"""
import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Import necessary components
from src.data.scrapers.scraper_manager import ScraperManager
from src.data.financial.stock_data import StockDataRetriever
from src.models.news_processor import NewsProcessor
from src.models.financial_qa import FinancialQA

app = Flask(__name__)
CORS(app)

# Initialize components
scraper_manager = ScraperManager()
stock_data = StockDataRetriever()
news_processor = NewsProcessor()

# Initialize QA system if API key is available
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    print(f"Using Gemini API key: {api_key[:5]}...{api_key[-4:]} for enhanced responses")
    qa_system = FinancialQA(api_key=api_key)
else:
    print("Warning: No Gemini API key found. QA system will use simulated responses.")
    qa_system = FinancialQA()  # Will use simulated responses if no API key is available

@app.route('/')
def home():
    return jsonify({"message": "NewsSense Stock API"})

@app.route('/api/stock/news', methods=['GET'])
def get_stock_news():
    """Get news related to a specific stock symbol."""
    symbol = request.args.get('symbol')
    
    if not symbol:
        return jsonify({"error": "Stock symbol is required"}), 400
    
    # Get stock information
    stock_info = stock_data.search_stocks(symbol)
    if not stock_info:
        return jsonify({"error": f"Stock not found for symbol: {symbol}"}), 404
    
    # Get company name from the stock info
    company_name = stock_info[0]["name"] if stock_info else symbol
    
    # Scrape news related to the company
    headlines = scraper_manager.scrape_all_headlines(limit=10)
    
    # Filter headlines related to the company
    related_news = []
    for headline in headlines:
        # Process headline to extract entities
        processed = news_processor.process_headline(headline)
        
        # Check if company is mentioned in the headline or if symbol is present
        if (company_name in processed["entities"].get("companies", []) or 
            symbol.upper() in processed["title"]):
            related_news.append(headline)
    
    return jsonify({
        "symbol": symbol,
        "company_name": company_name,
        "news": related_news[:5]  # Limit to top 5 most relevant
    })

@app.route('/api/stock/analysis', methods=['POST'])
def analyze_stock():
    """Generate analysis for a stock based on recent news."""
    data = request.json
    symbol = data.get('symbol')
    question = data.get('question', f"Why is {symbol} stock price changing?")
    
    if not symbol:
        return jsonify({"error": "Stock symbol is required"}), 400
    
    # Get stock information
    stock_info = stock_data.search_stocks(symbol)
    if not stock_info:
        return jsonify({"error": f"Stock not found for symbol: {symbol}"}), 404
    
    # Get company name from the stock info
    company_name = stock_info[0]["name"] if stock_info else symbol
    
    # Create a specific question about this stock
    specific_question = question
    if company_name not in question and symbol not in question:
        specific_question = f"{question} for {company_name} ({symbol})"
    
    # Get answer using the QA system
    answer = qa_system.answer_question(specific_question)
    
    # Get news specifically about this stock
    company_news = []
    
    # Scrape headlines with a broader scope
    headlines = scraper_manager.scrape_all_headlines(limit=20)
    
    # Process each headline to find relevant news
    for headline in headlines:
        # Process the headline to extract entities
        processed = news_processor.process_headline(headline)
        
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
    
    return jsonify({
        "symbol": symbol,
        "company_name": company_name,
        "question": specific_question,
        "answer": answer,
        "sources": sources,
        "is_simulated": qa_system.llm is None  # Flag to indicate if response is simulated
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)