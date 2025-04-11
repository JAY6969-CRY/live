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
        
        # Extract key entities for more targeted answers
        entity_matches = self._extract_entities_from_question(processed_question)
        
        # Find relevant context from scraped data
        context = self._get_relevant_context(processed_question)
        
        # Get relevant sources based on the query
        relevant_sources = self._get_relevant_sources(processed_question, entity_matches)
        
        # Store the current source files
        source_files = getattr(self, 'current_source_files', [])
        
        # Generate answer using LLM if available
        if self.qa_chain:
            try:
                answer = self.qa_chain.run(question=processed_question, context=context)
                return answer.strip(), source_files, relevant_sources
            except Exception as e:
                print(f"Error generating answer with Gemini: {str(e)}")
                answer = self._get_enhanced_answer(processed_question, context, entity_matches)
                return answer, source_files, relevant_sources
        else:
            # Fallback to a simulated response if Gemini API is not available
            answer = self._get_enhanced_answer(processed_question, context, entity_matches)
            return answer, source_files, relevant_sources
    
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
        
        # Track source files for user visibility
        source_files = set()
        
        # Match based on companies
        for company in entity_matches.get("companies", []):
            for article in self.news_articles:
                if "processed" in article:
                    if company in article["processed"]["entities"].get("companies", []):
                        relevant_articles.append(article)
                        # Track source file if available
                        if "source_file" in article:
                            source_files.add(article["source_file"])
        
        # Match based on indices
        for index in entity_matches.get("indices", []):
            for article in self.news_articles:
                if "processed" in article:
                    if index in article["processed"]["entities"].get("indices", []):
                        relevant_articles.append(article)
                        # Track source file if available
                        if "source_file" in article:
                            source_files.add(article["source_file"])
        
        # Match based on sectors
        for sector in entity_matches.get("sectors", []):
            for article in self.news_articles:
                if "processed" in article:
                    if sector in article["processed"]["entities"].get("sectors", []):
                        relevant_articles.append(article)
                        # Track source file if available
                        if "source_file" in article:
                            source_files.add(article["source_file"])
        
        # If no direct entity matches, try keyword matching
        if not relevant_articles:
            keywords = question.lower().split()
            keywords = [k for k in keywords if len(k) > 3 and k not in ["what", "when", "where", "which", "whose", "whom", "how", "why", "does", "did", "will", "would", "could", "should", "have", "has", "had", "been", "being", "with", "this", "that", "these", "those", "from", "about", "because"]]
            
            for article in self.news_articles:
                title = article.get("title", "").lower()
                content = article.get("content", "").lower()
                
                # Check if any keyword appears in title or content
                if any(keyword in title or keyword in content for keyword in keywords):
                    relevant_articles.append(article)
                    # Track source file if available
                    if "source_file" in article:
                        source_files.add(article["source_file"])
        
        # Create context string from relevant articles
        context_parts = []
        
        # Add article information
        for i, article in enumerate(relevant_articles[:5]):  # Limit to 5 most relevant articles
            title = article.get("title", "Unknown Title")
            source = article.get("source", "Unknown Source")
            date = article.get("date", "Unknown Date")
            content = article.get("content", "")
            
            if isinstance(date, datetime.datetime):
                date = date.strftime("%Y-%m-%d")
            
            # Add article metadata
            context_parts.append(f"Article {i+1}: '{title}' from {source} on {date}")
            
            # Add article content (truncated if too long)
            if len(content) > 1000:
                context_parts.append(content[:1000] + "...")
            else:
                context_parts.append(content)
        
        # Add financial data context if available
        financial_context = self._get_financial_data_context(entity_matches)
        if financial_context:
            context_parts.append(financial_context)
        
        # Create the full context string
        if context_parts:
            context = "\n\n".join(context_parts)
        else:
            context = "No specific information found relevant to the query."
        
        # Store the source files for reference in the answer
        if hasattr(self, 'current_source_files'):
            self.current_source_files = list(source_files)
        else:
            self.current_source_files = list(source_files)
        
        return context
    
    def _extract_entities_from_question(self, question: str) -> Dict[str, List[str]]:
        """
        Extract entities from a question using enhanced NLP techniques.
        
        Args:
            question: Question to extract entities from
            
        Returns:
            Dictionary with entity types and values
        """
        entities = {
            "companies": [],
            "sectors": [],
            "indices": [],
            "keywords": []
        }
        
        # Load financial entities (should refactor this to share with NewsProcessor)
        financial_entities = {
            "companies": [
                "Reliance Industries", "TCS", "HDFC Bank", "Infosys", "HUL", "ITC",
                "Bharti Airtel", "ICICI Bank", "Kotak Mahindra Bank", "Axis Bank",
                "State Bank of India", "SBI", "Bajaj Finance", "Asian Paints", "Maruti Suzuki",
                "Jyothy Labs", "Swiggy", "Wipro", "L&T", "Tata Motors", "JSW Steel", 
                "Adani Enterprises", "Adani Ports", "Sun Pharma", "Airtel", "Tata Steel"
            ],
            "sectors": [
                "Banking", "IT", "Pharma", "FMCG", "Auto", "Oil & Gas", "Telecom",
                "Metals", "Power", "Infrastructure", "Real Estate", "Financial Services",
                "Technology", "Healthcare", "Consumer Goods", "Retail", "Energy", 
                "Manufacturing", "Electric Vehicles", "EV", "Renewable Energy"
            ],
            "indices": [
                "Nifty", "Sensex", "Nifty Bank", "Nifty IT", "Nifty Pharma", "Nifty FMCG",
                "Nifty Auto", "Dow Jones", "S&P 500", "Nasdaq", "FTSE", "Nikkei"
            ]
        }
        
        # Common stock symbols (shortened versions of company names)
        stock_symbols = {
            "RELIANCE": "Reliance Industries", 
            "TCS": "TCS", 
            "HDFCBANK": "HDFC Bank",
            "INFY": "Infosys", 
            "HINDUNILVR": "HUL", 
            "ITC": "ITC",
            "BHARTIARTL": "Bharti Airtel", 
            "ICICIBANK": "ICICI Bank", 
            "KOTAKBANK": "Kotak Mahindra Bank",
            "AXISBANK": "Axis Bank", 
            "SBIN": "State Bank of India", 
            "BAJFINANCE": "Bajaj Finance",
            "ASIANPAINT": "Asian Paints", 
            "MARUTI": "Maruti Suzuki", 
            "JYOTHYLAB": "Jyothy Labs",
            "WIPRO": "Wipro",
            "LT": "L&T",
            "TATAMOTORS": "Tata Motors",
            "JSWSTEEL": "JSW Steel",
            "ADANIENT": "Adani Enterprises",
            "ADANIPORTS": "Adani Ports",
            "SUNPHARMA": "Sun Pharma",
            "TATASTEEL": "Tata Steel"
        }
        
        question_lower = question.lower()
        words = question_lower.split()
        
        # Check for stock symbols (uppercase in question)
        for word in question.split():
            if word.isupper() and word in stock_symbols:
                company = stock_symbols[word]
                if company not in entities["companies"]:
                    entities["companies"].append(company)
        
        # Check for companies - use complete matching for more accurate detection
        for company in financial_entities["companies"]:
            # Try different variations of company name
            variations = [
                company.lower(),
                company.lower().replace(" ", ""),
                company.lower().replace("industries", "").strip(),
                company.lower().replace("limited", "").strip(),
                company.lower().replace("ltd", "").strip()
            ]
            
            # Check if any variation is in the question
            for variation in variations:
                if variation in question_lower:
                    if company not in entities["companies"]:
                        entities["companies"].append(company)
                    break
        
        # Check for sectors
        for sector in financial_entities["sectors"]:
            if sector.lower() in question_lower:
                if sector not in entities["sectors"]:
                    entities["sectors"].append(sector)
        
        # Check for indices
        for index in financial_entities["indices"]:
            if index.lower() in question_lower:
                if index not in entities["indices"]:
                    entities["indices"].append(index)
        
        # Extract meaningful keywords (excluding stopwords)
        stopwords = ["what", "when", "where", "which", "why", "how", "is", "are", "was", "were", 
                     "am", "do", "does", "did", "has", "have", "had", "about", "above", "after", 
                     "again", "against", "all", "and", "any", "because", "been", "before", "being", 
                     "below", "between", "both", "but", "by", "could", "did", "does", "doing", 
                     "down", "during", "each", "few", "for", "from", "further", "had", "has", 
                     "have", "having", "her", "here", "hers", "herself", "him", "himself", "his", 
                     "how", "into", "its", "itself", "just", "me", "more", "most", "my", "myself", 
                     "no", "nor", "not", "now", "of", "off", "on", "once", "only", "or", "other", 
                     "our", "ours", "ourselves", "out", "over", "own", "same", "she", "should", 
                     "so", "some", "such", "than", "that", "the", "their", "theirs", "them", 
                     "themselves", "then", "there", "these", "they", "this", "those", "through", 
                     "to", "too", "under", "until", "up", "very", "was", "we", "were", "what", 
                     "when", "where", "which", "while", "who", "whom", "why", "will", "with", 
                     "would", "you", "your", "yours", "yourself", "yourselves"]
        
        important_financial_terms = ["price", "stock", "market", "share", "investing", "growth", 
                                    "profit", "loss", "earnings", "quarter", "revenue", "financial", 
                                    "trend", "performance", "investment", "dividend", "bullish", 
                                    "bearish", "rise", "fall", "increase", "decrease", "up", "down",
                                    "outlook", "forecast", "analysis", "report", "trading", "volume"]
        
        for word in words:
            if word not in stopwords and len(word) > 3:
                # Add financial terms and other potentially important words
                if word in important_financial_terms or not any(word in entity_list for entity_list in [
                    [e.lower() for e in entities["companies"]], 
                    [e.lower() for e in entities["sectors"]], 
                    [e.lower() for e in entities["indices"]]
                ]):
                    entities["keywords"].append(word)
        
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
        Load news articles from processed data.
        
        Returns:
            List of news article dictionaries
        """
        articles = []
        
        # Try to load processed news articles
        news_dir = os.path.join(self.data_dir, "news")
        if os.path.exists(news_dir):
            for filename in os.listdir(news_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(news_dir, filename)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            file_data = json.load(f)
                            # Add source_file to each article for traceability
                            for article in file_data:
                                article["source_file"] = filename
                            articles.extend(file_data)
                    except Exception as e:
                        print(f"Error loading news file {filename}: {str(e)}")
        
        # If no processed articles are found, use a default dataset
        if not articles:
            default_file = os.path.join(os.path.dirname(__file__), "../../data/default/news_sample.json")
            if os.path.exists(default_file):
                try:
                    with open(default_file, "r", encoding="utf-8") as f:
                        file_data = json.load(f)
                        # Add source_file to each article for traceability
                        for article in file_data:
                            article["source_file"] = "news_sample.json"
                        articles.extend(file_data)
                except Exception as e:
                    print(f"Error loading default news file: {str(e)}")
        
        # Sort by date (newest first)
        articles.sort(key=lambda x: x.get("date", ""), reverse=True)
        
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
    
    def _get_relevant_sources(self, question: str, entity_matches: Dict[str, List[str]]) -> List[Dict]:
        """
        Get relevant sources based on user query using advanced NLP matching.
        
        Args:
            question: User question
            entity_matches: Extracted entities from the question
            
        Returns:
            List of relevant sources
        """
        relevant_sources = []
        query_terms = set()
        exact_matches = set()
        
        # Process question for exact matching
        question_lower = question.lower()
        
        # First, identify exact phrases to prioritize exact matches
        # Stock symbols and company names get highest priority
        for entity_type, entities in entity_matches.items():
            for entity in entities:
                entity_lower = entity.lower()
                if entity_type == "companies":
                    # Give exact company names the highest priority
                    if entity_lower in question_lower:
                        exact_matches.add(entity_lower)
                        # Also add alternate forms
                        if "industries" in entity_lower:
                            exact_matches.add(entity_lower.replace("industries", "").strip())
                        if "ltd" in entity_lower or "limited" in entity_lower:
                            exact_matches.add(entity_lower.replace("ltd", "").replace("limited", "").strip())
        
        # Add all entities to query terms with higher priority
        entity_weights = {
            "companies": 10,  # Highest priority
            "indices": 8,
            "sectors": 6,
            "keywords": 2    # Lowest priority
        }
        
        # Track priorities for ranking
        term_weights = {}
        
        # Add extracted entities to query terms with appropriate weights
        for entity_type, entities in entity_matches.items():
            weight = entity_weights.get(entity_type, 1)
            for entity in entities:
                entity_lower = entity.lower()
                query_terms.add(entity_lower)
                term_weights[entity_lower] = weight
        
        # Add important contextual keywords from the question
        important_terms = ['nifty', 'sensex', 'market', 'stock', 'share', 'price', 
                          'bank', 'finance', 'tech', 'pharma', 'auto', 'oil', 'gas',
                          'energy', 'retail', 'consumer', 'it', 'technology', 'earnings',
                          'quarter', 'result', 'profit', 'loss', 'revenue', 'growth',
                          'up', 'down', 'increase', 'decrease', 'rise', 'fall', 'rally',
                          'slump', 'crash', 'surge', 'plunge', 'jump', 'drop']
        
        for term in important_terms:
            if term in question_lower and term not in query_terms:
                query_terms.add(term)
                term_weights[term] = 3  # Medium priority for these terms
        
        # Extract key phrases that may be exact matches (2-3 word phrases)
        words = question_lower.split()
        phrases = []
        for i in range(len(words)-1):
            phrases.append(f"{words[i]} {words[i+1]}")
        for i in range(len(words)-2):
            phrases.append(f"{words[i]} {words[i+1]} {words[i+2]}")
        
        # Add important phrases if they appear to be significant
        for phrase in phrases:
            if any(term in phrase for term in important_terms) and len(phrase) > 5:
                query_terms.add(phrase)
                term_weights[phrase] = 4  # Higher priority for specific phrases
        
        # Find articles that match any of the query terms
        for article in self.news_articles:
            title = article.get("title", "").lower()
            source = article.get("source", "")
            date = article.get("date", "")
            content = article.get("content", "").lower() if article.get("content") else ""
            
            # Format date
            if isinstance(date, datetime.datetime):
                date = date.strftime("%Y-%m-%d")
            
            # Check for exact matches first (highest priority)
            has_exact_match = False
            exact_match_terms = []
            for term in exact_matches:
                if term in title:
                    has_exact_match = True
                    exact_match_terms.append(term)
            
            # Check if any query term appears in the title or content
            matches = []
            relevance_score = 0
            
            # Calculate relevance score based on matching terms
            for term in query_terms:
                # Check title (higher weight)
                if term in title:
                    matches.append(term)
                    # Exact match in title gets highest score
                    if term in exact_matches:
                        relevance_score += term_weights.get(term, 1) * 5
                    else:
                        # Regular match in title gets high score
                        relevance_score += term_weights.get(term, 1) * 3
                
                # Check content (lower weight)
                elif term in content:
                    matches.append(term)
                    if term in exact_matches:
                        relevance_score += term_weights.get(term, 1) * 2
                    else:
                        relevance_score += term_weights.get(term, 1)
            
            # Boost articles with exact matches in title
            if has_exact_match:
                relevance_score += 20
                matches = exact_match_terms + [m for m in matches if m not in exact_match_terms]
            
            # Boost very recent articles (within 7 days)
            try:
                article_date = datetime.datetime.fromisoformat(date.replace('Z', '+00:00'))
                days_old = (datetime.datetime.now() - article_date).days
                if days_old <= 7:
                    relevance_score += (7 - days_old)  # More recent = higher boost
            except:
                pass
            
            if matches:
                # Create source entry with all relevant information
                relevant_sources.append({
                    "title": article.get("title", ""),
                    "source": source,
                    "date": date,
                    "matches": matches,
                    "relevance_score": relevance_score,
                    "exact_match": has_exact_match
                })
        
        # Sort sources by relevance score (highest first) and date (newest first)
        relevant_sources.sort(key=lambda x: (x.get("exact_match", False), x.get("relevance_score", 0), x.get("date", "")), reverse=True)
        
        # Only return sources that are truly relevant (have at least one exact match or high relevance)
        filtered_sources = [s for s in relevant_sources if s.get("exact_match", False) or s.get("relevance_score", 0) >= 5]
        
        # If we have exact matches, prioritize those. Otherwise use best available
        if any(s.get("exact_match", False) for s in filtered_sources):
            final_sources = [s for s in filtered_sources if s.get("exact_match", False)]
            # Add a few non-exact matches that are still highly relevant
            additional_sources = [s for s in filtered_sources if not s.get("exact_match", False)][:2]
            final_sources.extend(additional_sources)
        else:
            final_sources = filtered_sources
        
        # Return the top 5 most relevant sources
        return final_sources[:5]


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
        answer, source_files, relevant_sources = qa_system.answer_question(question)
        print(f"Answer: {answer}")
        print(f"Source Files: {', '.join(source_files) if source_files else 'None'}")
        print(f"Relevant Sources: {', '.join([f'{source["title"]} from {source["source"]} on {source["date"]}' for source in relevant_sources]) if relevant_sources else 'None'}")
        print()
