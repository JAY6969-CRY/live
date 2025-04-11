"""
FastAPI app for the NewsSense API.
"""
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Import necessary components
from src.data.scrapers.scraper_manager import ScraperManager
from src.data.financial.stock_data import StockDataRetriever
from src.data.financial.mutual_fund_data import MutualFundDataRetriever
from src.models.news_processor import NewsProcessor
from src.models.financial_qa import FinancialQA


# Define API models
class NewsArticle(BaseModel):
    title: str
    content: str
    source: str
    url: str
    date: str
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Reliance Industries Reports Q2 Results",
                "content": "Reliance Industries reported a 10% increase in profits...",
                "source": "Economic Times",
                "url": "https://economictimes.indiatimes.com/example",
                "date": "2023-10-15"
            }
        }


class QuestionRequest(BaseModel):
    question: str
    
    class Config:
        schema_extra = {
            "example": {
                "question": "Why is Nifty down today?"
            }
        }


class QuestionResponse(BaseModel):
    question: str
    answer: str
    sources: List[Dict]
    source_files: Optional[List[str]] = []
    is_simulated: Optional[bool] = False
    
    class Config:
        schema_extra = {
            "example": {
                "question": "Why is Nifty down today?",
                "answer": "Nifty is down today due to global market weakness and concerns about rising oil prices.",
                "sources": [
                    {
                        "title": "Market Wrap: Nifty falls amid global concerns",
                        "source": "Economic Times",
                        "date": "2023-10-15"
                    }
                ],
                "source_files": ["news_2023-10-15.json", "market_data.csv"],
                "is_simulated": False
            }
        }


class StockInfo(BaseModel):
    symbol: str
    name: str
    isin: str
    sector: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "symbol": "RELIANCE",
                "name": "Reliance Industries Ltd.",
                "isin": "INE002A01018",
                "sector": "Oil & Gas"
            }
        }


class MutualFundInfo(BaseModel):
    scheme_code: str
    scheme_name: str
    amc: str
    category: str
    
    class Config:
        schema_extra = {
            "example": {
                "scheme_code": "119240",
                "scheme_name": "SBI Blue Chip Fund-Direct Plan-Growth",
                "amc": "SBI",
                "category": "Large Cap"
            }
        }


# Initialize FastAPI app
app = FastAPI(
    title="NewsSense API",
    description="API for NewsSense - A financial news and explanation system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Initialize components on startup
@app.on_event("startup")
async def startup_event():
    # Initialize and store necessary components
    app.state.scraper_manager = ScraperManager()
    app.state.stock_data = StockDataRetriever()
    app.state.mutual_fund_data = MutualFundDataRetriever()
    app.state.news_processor = NewsProcessor()
    
    # Initialize QA system with Gemini API
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        print(f"Using Gemini API key: {api_key[:5]}...{api_key[-4:]} for enhanced responses")
        app.state.qa_system = FinancialQA(api_key=api_key)
    else:
        print("Warning: No Gemini API key found. QA system will use simulated responses.")
        app.state.qa_system = FinancialQA()  # Will use simulated responses if no API key is available


# Define dependency to get QA system
def get_qa_system():
    return app.state.qa_system


# API routes
@app.get("/")
async def root():
    return {"message": "Welcome to NewsSense API"}


@app.get("/news/headlines", response_model=List[NewsArticle])
async def get_headlines(
    category: Optional[str] = None,
    limit: int = Query(10, ge=1, le=50)
):
    """Get latest news headlines."""
    try:
        headlines = app.state.scraper_manager.scrape_all_headlines(category, limit)
        return headlines
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching headlines: {str(e)}")


@app.get("/news/article", response_model=NewsArticle)
async def get_article(url: str):
    """Get full article by URL."""
    try:
        articles = app.state.scraper_manager.scrape_articles([url])
        if not articles:
            raise HTTPException(status_code=404, detail="Article not found")
        return articles[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching article: {str(e)}")


@app.get("/stocks/search", response_model=List[StockInfo])
async def search_stocks(query: str, limit: int = Query(10, ge=1, le=50)):
    """Search for stocks by name, symbol, or ISIN."""
    try:
        stocks = app.state.stock_data.search_stocks(query)
        return stocks[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching stocks: {str(e)}")


@app.get("/mutualfunds/search", response_model=List[MutualFundInfo])
async def search_mutual_funds(query: str, limit: int = Query(10, ge=1, le=50)):
    """Search for mutual funds by name or AMC."""
    try:
        funds = app.state.mutual_fund_data.search_funds(query)
        return funds[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching mutual funds: {str(e)}")


@app.post("/qa/question", response_model=QuestionResponse)
async def answer_question(
    request: QuestionRequest,
    qa_system: FinancialQA = Depends(get_qa_system)
):
    """Answer a financial question based on news and financial data."""
    try:
        question = request.question
        answer, source_files, relevant_sources = qa_system.answer_question(question)
        
        # Get sources from the relevant sources
        sources = relevant_sources
        
        return {
            "question": question,
            "answer": answer,
            "sources": sources,
            "source_files": source_files,
            "is_simulated": qa_system.llm is None  # Flag to indicate if response is simulated
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error answering question: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 