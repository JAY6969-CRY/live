"""
Module for LLM-powered financial QA system.
"""
import os
import json
import datetime
from typing import Dict, List, Optional, Union, Any
import re
import pandas as pd
# Remove OpenAI imports
# from langchain.llms import OpenAI
# import openai
# Add Gemini imports
import google.generativeai as genai
from langchain_core.language_models.llms import LLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from pydantic import Field


# Add Gemini LLM wrapper class for LangChain
class GeminiLLM(LLM):
    """Wrapper around Google's Gemini models."""
    
    model_name: str = "gemini-pro"
    temperature: float = 0.1
    api_key: Optional[str] = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set API key
        if kwargs.get("api_key"):
            self.api_key = kwargs.get("api_key")
            genai.configure(api_key=self.api_key)
        elif "GEMINI_API_KEY" in os.environ:
            genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        else:
            raise ValueError("Gemini API key must be provided as an argument or set as environment variable GEMINI_API_KEY")
        
        # Configure the model
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={"temperature": self.temperature}
        )
    
    def _call(self, prompt: str, **kwargs) -> str:
        """Call the Gemini API and return the response."""
        response = self.model.generate_content(prompt)
        return response.text
    
    @property
    def _llm_type(self) -> str:
        """Return type of LLM."""
        return "gemini"


class FinancialQA:
    """Class for LLM-powered financial QA system."""
    
    def __init__(self, 
                 data_dir: str = "./data/processed",
                 api_key: Optional[str] = None,
                 model: str = "gemini-pro"):
        """
        Initialize financial QA system.
        
        Args:
            data_dir: Directory with processed data
            api_key: Gemini API key (default: uses GEMINI_API_KEY env var)
            model: Gemini model to use
        """
        self.data_dir = data_dir
        
        # Set API key for Gemini
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        
        # Initialize LangChain components with Gemini
        try:
            if self.api_key:
                self.llm = GeminiLLM(model_name=model, api_key=self.api_key)
                
                # Define prompt templates
                self.qa_template = PromptTemplate(
                    input_variables=["question", "context"],
                    template="""
                    You are a financial news analyst and advisor. Answer the following question based on the provided context.
                    
                    Question: {question}
                    
                    Context:
                    {context}
                    
                    Answer the question concisely and accurately based solely on the information in the context.
                    If the context doesn't contain enough information to answer the question definitively, say so.
                    
                    Answer:
                    """
                )
                
                self.qa_chain = LLMChain(llm=self.llm, prompt=self.qa_template)
            else:
                print("No Gemini API key found. Using simulated responses.")
                self.llm = None
                self.qa_chain = None
        except Exception as e:
            print(f"Error initializing Gemini model: {str(e)}")
            print("Falling back to simulated responses")
            self.llm = None
            self.qa_chain = None
        
        # Load processed news articles
        self.news_articles = self._load_news_articles()
        
        # Load financial data
        self.stock_data = self._load_stock_data()
        self.fund_data = self._load_fund_data()
    
    def answer_question(self, question: str) -> str:
        """
        Answer a financial question using news and financial data.
        
        Args:
            question: Question to answer
            
        Returns:
            Answer to the question
        """
        # Preprocess the question
        processed_question = question.strip()
        
        # Find relevant context from scraped data
        context = self._get_relevant_context(processed_question)
        
        # Extract key entities for more targeted answers
        entity_matches = self._extract_entities_from_question(processed_question)
        
        # Generate answer using LLM if available
        if self.qa_chain:
            try:
                answer = self.qa_chain.run(question=processed_question, context=context)
                return answer.strip()
            except Exception as e:
                print(f"Error generating answer with Gemini: {str(e)}")
                return self._get_enhanced_answer(processed_question, context, entity_matches)
        else:
            # Fallback to a simulated response if Gemini API is not available
            return self._get_enhanced_answer(processed_question, context, entity_matches)
    
    def _get_enhanced_answer(self, question: str, context: str, entity_matches: Dict[str, List[str]]) -> str:
        """
        Generate an enhanced answer based on scraped data when API is not available.
        
        Args:
            question: Question to answer
            context: Context for the question
            entity_matches: Extracted entities from the question
            
        Returns:
            Enhanced answer based on scraped data
        """
        # Check if we have relevant articles
        if "No specific information found" in context:
            return f"I couldn't find specific information about {', '.join(entity_matches.get('companies', []) or entity_matches.get('indices', []) or ['this topic'])} in the recent news data. Consider checking for more recent updates or refining your question."
        
        # Find the most relevant article snippets
        snippets = []
        for line in context.split('\n'):
            if line.startswith('Article'):
                # Extract article metadata
                try:
                    article_parts = line.split("'")
                    title = article_parts[1] if len(article_parts) > 1 else ""
                    snippets.append(f"According to '{title}'")
                except:
                    pass
            elif line and not line.startswith('Financial Data'):
                snippets.append(line)
        
        # Build a more informative response using the data we have
        answer = ""
        
        # Add company-specific information if available
        if entity_matches.get("companies"):
            company = entity_matches["companies"][0]
            answer += f"Regarding {company}, based on the available news: "
            
            # Check if we have stock data
            if f"Financial Data for {company}" in context:
                # Extract financial data
                for line in context.split('\n'):
                    if line.startswith(f"Financial Data for {company}") or "Price Change" in line or "Latest Close Price" in line:
                        answer += line.replace("Financial Data for", "").strip() + ". "
        
        # Add index-specific information if available
        elif entity_matches.get("indices"):
            index = entity_matches["indices"][0]
            answer += f"Regarding {index}, based on the available news: "
        
        # Add sector-specific information if available
        elif entity_matches.get("sectors"):
            sector = entity_matches["sectors"][0]
            answer += f"Regarding the {sector} sector, based on the available news: "
        
        # Generate answer from snippets (up to 5)
        used_snippets = set()
        for snippet in snippets[:10]:
            # Avoid duplicates and empty lines
            if snippet and len(snippet) > 20 and snippet not in used_snippets:
                answer += snippet + ". "
                used_snippets.add(snippet)
                if len(used_snippets) >= 5:
                    break
        
        # If we couldn't extract good snippets, provide a general response
        if not used_snippets:
            if "stock" in question.lower() or "price" in question.lower():
                answer = "Based on recent news, market sentiment for this stock appears mixed. There are signs of sector-wide challenges but company-specific factors may be providing support to the stock price."
            elif "market" in question.lower() or "index" in question.lower() or any(index in question.lower() for index in ["nifty", "sensex"]):
                answer = "Market indices have been volatile due to a combination of global factors and domestic economic indicators. Recent policy announcements and earning reports from major companies are key drivers of the current trend."
            elif "why" in question.lower() and ("up" in question.lower() or "down" in question.lower()):
                answer = "The price movement appears to be influenced by recent corporate developments, broader market trends, and sector-specific news. Analyst recommendations and trading volumes also suggest changing investor sentiment."
            else:
                answer = "Based on available information, there appear to be multiple factors influencing this financial situation. Market trends, company-specific news, and broader economic indicators all play a role in the current scenario."
        
        return answer
    
    def _get_relevant_context(self, question: str) -> str:
        """
        Get relevant context for a question.
        
        Args:
            question: Question to get context for
            
        Returns:
            Relevant context as a string
        """
        # Extract entities and keywords from the question
        entity_matches = self._extract_entities_from_question(question)
        
        # Find related articles
        relevant_articles = []
        
        # Match based on companies
        for company in entity_matches.get("companies", []):
            for article in self.news_articles:
                if "processed" in article:
                    if company in article["processed"]["entities"].get("companies", []):
                        relevant_articles.append(article)
        
        # Match based on indices
        for index in entity_matches.get("indices", []):
            for article in self.news_articles:
                if "processed" in article:
                    if index in article["processed"]["entities"].get("indices", []):
                        relevant_articles.append(article)
        
        # Match based on sectors
        for sector in entity_matches.get("sectors", []):
            for article in self.news_articles:
                if "processed" in article:
                    if sector in article["processed"]["entities"].get("sectors", []):
                        relevant_articles.append(article)
        
        # Remove duplicates while preserving order
        unique_articles = []
        seen_urls = set()
        for article in relevant_articles:
            url = article.get("url", "")
            if url not in seen_urls:
                unique_articles.append(article)
                seen_urls.add(url)
        
        # Sort by date (newest first)
        unique_articles.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        # Limit to most recent articles
        unique_articles = unique_articles[:5]
        
        # Generate context string
        context_parts = []
        
        # Add financial data context if relevant
        financial_context = self._get_financial_data_context(entity_matches)
        if financial_context:
            context_parts.append(financial_context)
        
        # Add article contexts
        for i, article in enumerate(unique_articles):
            title = article.get("title", "")
            source = article.get("source", "")
            date = article.get("date", "")
            content = article.get("content", "")
            
            if isinstance(date, str):
                date_str = date[:10]  # Extract YYYY-MM-DD part
            else:
                date_str = date.strftime("%Y-%m-%d")
            
            article_context = f"Article {i+1} - '{title}' from {source} on {date_str}:\n{content}\n"
            context_parts.append(article_context)
        
        # Combine context
        full_context = "\n".join(context_parts)
        
        # If no relevant context found, provide a general message
        if not full_context:
            return "No specific information found in the database about this query."
        
        return full_context
    
    def _extract_entities_from_question(self, question: str) -> Dict[str, List[str]]:
        """
        Extract entities from a question.
        
        Args:
            question: Question to extract entities from
            
        Returns:
            Dictionary with entity types and values
        """
        entities = {
            "companies": [],
            "sectors": [],
            "indices": []
        }
        
        # Load financial entities (should refactor this to share with NewsProcessor)
        financial_entities = {
            "companies": [
                "Reliance Industries", "TCS", "HDFC Bank", "Infosys", "HUL", "ITC",
                "Bharti Airtel", "ICICI Bank", "Kotak Mahindra Bank", "Axis Bank",
                "State Bank of India", "Bajaj Finance", "Asian Paints", "Maruti Suzuki",
                "Jyothy Labs", "Swiggy"
            ],
            "sectors": [
                "Banking", "IT", "Pharma", "FMCG", "Auto", "Oil & Gas", "Telecom",
                "Metals", "Power", "Infrastructure", "Real Estate", "Financial Services",
                "Technology", "Healthcare", "Consumer Goods"
            ],
            "indices": [
                "Nifty", "Sensex", "Nifty Bank", "Nifty IT", "Nifty Pharma", "Nifty FMCG",
                "Nifty Auto", "Dow Jones", "S&P 500", "Nasdaq", "FTSE", "Nikkei"
            ]
        }
        
        question_lower = question.lower()
        
        # Check for companies
        for company in financial_entities["companies"]:
            if company.lower() in question_lower:
                entities["companies"].append(company)
        
        # Check for sectors
        for sector in financial_entities["sectors"]:
            if sector.lower() in question_lower:
                entities["sectors"].append(sector)
        
        # Check for indices
        for index in financial_entities["indices"]:
            if index.lower() in question_lower:
                entities["indices"].append(index)
        
        return entities
    
    def _get_financial_data_context(self, entity_matches: Dict[str, List[str]]) -> str:
        """
        Get financial data context for entities.
        
        Args:
            entity_matches: Dictionary with entity matches
            
        Returns:
            Financial data context as a string
        """
        context_parts = []
        
        # Add company stock data
        for company in entity_matches.get("companies", []):
            if company in self.stock_data:
                stock_df = self.stock_data[company]
                if not stock_df.empty:
                    # Get recent price changes
                    recent_data = stock_df.tail(5)
                    price_change = ((recent_data.iloc[-1]["Close"] / recent_data.iloc[0]["Close"]) - 1) * 100
                    
                    context = f"Financial Data for {company}:\n"
                    context += f"Latest Close Price: {recent_data.iloc[-1]['Close']:.2f}\n"
                    context += f"5-Day Price Change: {price_change:.2f}%\n"
                    context += f"Latest Trading Volume: {recent_data.iloc[-1]['Volume']}\n"
                    
                    context_parts.append(context)
        
        # Add index data
        for index in entity_matches.get("indices", []):
            if index in self.stock_data:  # Assuming index data is stored similar to stock data
                index_df = self.stock_data[index]
                if not index_df.empty:
                    # Get recent price changes
                    recent_data = index_df.tail(5)
                    price_change = ((recent_data.iloc[-1]["Close"] / recent_data.iloc[0]["Close"]) - 1) * 100
                    
                    context = f"Financial Data for {index}:\n"
                    context += f"Latest Close Value: {recent_data.iloc[-1]['Close']:.2f}\n"
                    context += f"5-Day Change: {price_change:.2f}%\n"
                    
                    context_parts.append(context)
        
        return "\n".join(context_parts)
    
    def _load_news_articles(self) -> List[Dict]:
        """
        Load processed news articles.
        
        Returns:
            List of processed article dictionaries
        """
        articles_dir = os.path.join(self.data_dir, "news")
        articles = []
        
        # Return empty list if directory doesn't exist
        if not os.path.exists(articles_dir):
            return articles
        
        # Load all processed article files
        for filename in os.listdir(articles_dir):
            if filename.startswith("processed_articles_") and filename.endswith(".json"):
                filepath = os.path.join(articles_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        file_articles = json.load(f)
                        articles.extend(file_articles)
                except Exception as e:
                    print(f"Error loading articles from {filepath}: {e}")
        
        # Convert date strings back to datetime objects
        for article in articles:
            if isinstance(article.get("date"), str):
                try:
                    article["date"] = datetime.datetime.fromisoformat(article["date"])
                except (ValueError, TypeError):
                    # Keep as string if conversion fails
                    pass
        
        return articles
    
    def _load_stock_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load stock data.
        
        Returns:
            Dictionary mapping stock symbols to DataFrames
        """
        stocks_dir = os.path.join(self.data_dir, "../financial/stocks")
        stock_data = {}
        
        # Return empty dict if directory doesn't exist
        if not os.path.exists(stocks_dir):
            return stock_data
        
        # This is a simplified implementation. In a real system, you would
        # have a more sophisticated data loading mechanism.
        for filename in os.listdir(stocks_dir):
            if filename.endswith(".csv") and not filename.startswith("stock_list"):
                # Extract symbol from filename
                symbol_match = re.match(r"([A-Z]+)_", filename)
                if symbol_match:
                    symbol = symbol_match.group(1)
                    filepath = os.path.join(stocks_dir, filename)
                    try:
                        df = pd.read_csv(filepath, parse_dates=["Date"])
                        stock_data[symbol] = df
                    except Exception as e:
                        print(f"Error loading stock data from {filepath}: {e}")
        
        return stock_data
    
    def _load_fund_data(self) -> Dict[str, Dict]:
        """
        Load mutual fund data.
        
        Returns:
            Dictionary mapping fund codes to data dictionaries
        """
        funds_dir = os.path.join(self.data_dir, "../financial/mutual_funds")
        fund_data = {}
        
        # Return empty dict if directory doesn't exist
        if not os.path.exists(funds_dir):
            return fund_data
        
        # Load fund NAV data
        for filename in os.listdir(funds_dir):
            if filename.startswith("nav_") and filename.endswith(".csv"):
                # Extract scheme code from filename
                code_match = re.match(r"nav_(\d+)\.csv", filename)
                if code_match:
                    scheme_code = code_match.group(1)
                    nav_filepath = os.path.join(funds_dir, filename)
                    
                    # Load holdings if available
                    holdings_filepath = os.path.join(funds_dir, f"holdings_{scheme_code}.json")
                    
                    try:
                        nav_df = pd.read_csv(nav_filepath, parse_dates=["Date"])
                        
                        fund_data[scheme_code] = {
                            "nav": nav_df
                        }
                        
                        if os.path.exists(holdings_filepath):
                            with open(holdings_filepath, 'r', encoding='utf-8') as f:
                                holdings = json.load(f)
                                fund_data[scheme_code]["holdings"] = holdings
                    except Exception as e:
                        print(f"Error loading fund data for {scheme_code}: {e}")
        
        return fund_data


if __name__ == "__main__":
    # Example usage
    qa_system = FinancialQA()
    
    # Example questions
    questions = [
        "Why did Jyothy Labs up today?",
        "What happened to Nifty this week?",
        "Any macro news impacting tech-focused funds?",
        "What does the last quarter say for the Swiggy?"
    ]
    
    for question in questions:
        print(f"Question: {question}")
        answer = qa_system.answer_question(question)
        print(f"Answer: {answer}\n")
