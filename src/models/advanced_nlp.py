"""
Advanced NLP module for NewsSense.
Extends the existing NLP capabilities with more sophisticated models and techniques.
"""
import os
import json
import datetime
import re
from typing import Dict, List, Optional, Any, Tuple, Set
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter
import numpy as np

# Optional imports for more advanced features if available
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

class AdvancedNLP:
    """Advanced NLP capabilities for news analysis and query processing."""
    
    def __init__(self, use_transformers: bool = False):
        """
        Initialize advanced NLP processor.
        
        Args:
            use_transformers: Whether to use Hugging Face transformers if available
        """
        self.use_transformers = use_transformers and TRANSFORMERS_AVAILABLE
        
        # Download NLTK data if needed
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('punkt')
            nltk.download('stopwords')
            nltk.download('wordnet')
        
        # Initialize basic NLP tools
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
        # Regex patterns
        self.url_pattern = re.compile(r'https?://\S+|www\.\S+')
        self.html_pattern = re.compile(r'<.*?>')
        self.punctuation_pattern = re.compile(r'[^\w\s]')
        
        # Financial-specific stopwords (terms too common in financial news)
        self.financial_stopwords = {
            'stock', 'stocks', 'market', 'markets', 'company', 'companies',
            'share', 'shares', 'investor', 'investors', 'trading', 'price',
            'prices', 'report', 'reports', 'reported', 'quarter', 'quarterly',
            'financial', 'finance', 'investment', 'investments', 'year',
            'years', 'month', 'months', 'day', 'days', 'week', 'weeks',
            'percent', 'percentage'
        }
        
        # Load financial entities with enhanced stock symbols
        self.financial_entities = self._load_financial_entities()
        
        # Domain-specific term weighting
        self.domain_weights = {
            # Earnings-related terms
            'earnings': 2.0, 'profit': 2.0, 'revenue': 2.0, 'eps': 2.0, 
            'loss': 2.0, 'guidance': 2.0, 'outlook': 1.5, 'forecast': 1.5,
            
            # Corporate actions
            'acquisition': 2.5, 'merger': 2.5, 'takeover': 2.5, 'spinoff': 2.5,
            'buyback': 2.0, 'dividend': 2.0, 'split': 1.5, 'ipo': 2.5,
            
            # Market events
            'downgrade': 2.0, 'upgrade': 2.0, 'overweight': 1.5, 'underweight': 1.5,
            'rally': 1.5, 'crash': 2.0, 'correction': 1.5, 'bearish': 1.5, 'bullish': 1.5,
            
            # Corporate issues
            'scandal': 2.5, 'lawsuit': 2.0, 'investigation': 2.0, 'fine': 2.0,
            'regulation': 1.5, 'compliance': 1.5, 'patent': 2.0, 'approval': 2.0,
            
            # Economic indicators
            'inflation': 1.5, 'interest': 1.5, 'recession': 2.0, 'gdp': 1.5,
            'unemployment': 1.5, 'policy': 1.5, 'fed': 1.5, 'rbi': 1.5
        }
        
        # Initialize transformers models if available and requested
        if self.use_transformers:
            self._initialize_transformers()
    
    def _initialize_transformers(self):
        """Initialize transformer-based models for NER and classification."""
        if TRANSFORMERS_AVAILABLE:
            # Initialize NER pipeline
            self.ner_model = pipeline(
                "ner",
                model="Jean-Baptiste/roberta-large-ner-english",
                aggregation_strategy="simple"
            )
            
            # Initialize sentiment analysis pipeline
            self.sentiment_model = pipeline(
                "sentiment-analysis",
                model="ProsusAI/finbert"
            )
        else:
            print("Warning: Transformers library not available. Using basic NLP techniques only.")
    
    def extract_entities(self, text: str, title: str = "") -> Dict[str, List[str]]:
        """
        Extract named entities from text with enhanced financial entity recognition.
        
        Args:
            text: Text to extract entities from
            title: Title text for additional context
            
        Returns:
            Dictionary with entity types and values
        """
        combined_text = f"{title} {text}"
        
        entities = {
            "companies": [],
            "sectors": [],
            "indices": [],
            "persons": [],
            "locations": [],
            "keywords": []
        }
        
        # Try transformer-based NER if available
        if self.use_transformers and TRANSFORMERS_AVAILABLE:
            try:
                # Use pre-trained NER model
                ner_results = self.ner_model(combined_text)
                
                # Process NER results
                for entity in ner_results:
                    entity_text = entity['word']
                    entity_type = entity['entity_group']
                    
                    if entity_type == 'ORG' and entity_text not in entities["companies"]:
                        # Check if this matches any known company
                        if self._matches_known_company(entity_text):
                            entities["companies"].append(entity_text)
                    
                    elif entity_type == 'PER' and entity_text not in entities["persons"]:
                        entities["persons"].append(entity_text)
                    
                    elif entity_type == 'LOC' and entity_text not in entities["locations"]:
                        entities["locations"].append(entity_text)
            
            except Exception as e:
                print(f"Error using transformer NER: {str(e)}")
        
        # Always perform rule-based entity extraction as backup or enhancement
        self._rule_based_entity_extraction(combined_text, entities)
        
        # Extract keywords
        entities["keywords"] = self.extract_keywords(combined_text)
        
        return entities
    
    def _rule_based_entity_extraction(self, text: str, entities: Dict[str, List[str]]):
        """
        Apply rule-based entity extraction techniques.
        
        Args:
            text: Text to extract entities from
            entities: Entity dictionary to update
        """
        text_lower = text.lower()
        
        # Check for companies
        for company in self.financial_entities.get("companies", []):
            # Try different variations of company name
            variations = [
                company.lower(),
                company.lower().replace(" ", ""),
                company.lower().replace("industries", "").strip(),
                company.lower().replace("limited", "").strip(),
                company.lower().replace("ltd", "").strip()
            ]
            
            # Check if any variation is in the text
            for variation in variations:
                if variation in text_lower:
                    if company not in entities["companies"]:
                        entities["companies"].append(company)
                    break
        
        # Check for stock symbols (uppercase words)
        for symbol, company in self.financial_entities.get("symbols", {}).items():
            # Look for exact symbol matches with word boundaries
            if re.search(r'\b' + re.escape(symbol) + r'\b', text):
                if company not in entities["companies"]:
                    entities["companies"].append(company)
        
        # Check for sectors
        for sector in self.financial_entities.get("sectors", []):
            if sector.lower() in text_lower:
                if sector not in entities["sectors"]:
                    entities["sectors"].append(sector)
        
        # Check for indices
        for index in self.financial_entities.get("indices", []):
            if index.lower() in text_lower:
                if index not in entities["indices"]:
                    entities["indices"].append(index)
    
    def _matches_known_company(self, entity_text: str) -> bool:
        """
        Check if extracted entity matches any known company.
        
        Args:
            entity_text: Entity text to check
            
        Returns:
            True if matches known company, False otherwise
        """
        entity_lower = entity_text.lower()
        
        # Check against known companies
        for company in self.financial_entities.get("companies", []):
            company_lower = company.lower()
            
            # Check direct match
            if entity_lower == company_lower:
                return True
            
            # Check if entity is part of company name
            if (len(entity_text) > 4 and 
                entity_lower in company_lower and 
                len(entity_lower) / len(company_lower) > 0.5):
                return True
            
            # Check common company name patterns
            if company_lower.startswith(entity_lower) and len(entity_lower) > 4:
                return True
        
        # Check against stock symbols
        for symbol, company in self.financial_entities.get("symbols", {}).items():
            if entity_text.upper() == symbol:
                return True
        
        return False
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """
        Extract keywords from text using TF-IDF and domain-specific weighting.
        
        Args:
            text: Text to extract keywords from
            top_n: Number of top keywords to extract
            
        Returns:
            List of keywords
        """
        if not text or len(text.split()) < 3:
            return []
        
        # Clean text
        cleaned_text = self._clean_text(text)
        
        # Tokenize and remove stopwords
        tokens = word_tokenize(cleaned_text.lower())
        tokens = [
            token for token in tokens 
            if token not in self.stop_words 
            and token not in self.financial_stopwords
            and not self.punctuation_pattern.match(token)
            and len(token) > 2
        ]
        
        # Use TF-IDF to extract keywords
        tfidf = TfidfVectorizer(max_features=top_n*2)
        try:
            # Create document from tokens
            doc = " ".join(tokens)
            tfidf_matrix = tfidf.fit_transform([doc])
            feature_names = tfidf.get_feature_names_out()
            
            # Get keywords with scores
            dense = tfidf_matrix.todense()
            scores = dense[0].tolist()[0]
            keyword_scores = [(feature_names[i], scores[i]) for i in range(len(feature_names))]
            
            # Apply domain-specific weighting
            weighted_keywords = []
            for keyword, score in keyword_scores:
                # Apply domain weight if available
                domain_weight = self.domain_weights.get(keyword.lower(), 1.0)
                weighted_keywords.append((keyword, score * domain_weight))
            
            # Sort by weighted score
            weighted_keywords.sort(key=lambda x: x[1], reverse=True)
            
            # Return top keywords
            return [keyword for keyword, _ in weighted_keywords[:top_n]]
        except Exception as e:
            print(f"Error extracting keywords: {e}")
            
            # Fallback: Use frequency-based approach
            counter = Counter(tokens)
            return [word for word, _ in counter.most_common(top_n)]
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process user query to extract entities, intent, and keywords.
        
        Args:
            query: User query
            
        Returns:
            Dictionary with processed query information
        """
        # Clean and normalize query
        cleaned_query = self._clean_text(query)
        
        # Extract entities
        entities = self.extract_entities(cleaned_query)
        
        # Extract intent (simple rule-based approach)
        intent = self._extract_intent(cleaned_query)
        
        # Extract phrases (2-3 word phrases that might be meaningful)
        phrases = self._extract_phrases(cleaned_query)
        
        # Identify key terms for relevance ranking
        key_terms = self._identify_key_terms(cleaned_query, entities)
        
        return {
            "original_query": query,
            "cleaned_query": cleaned_query,
            "entities": entities,
            "intent": intent,
            "phrases": phrases,
            "key_terms": key_terms
        }
    
    def _extract_intent(self, query: str) -> str:
        """
        Extract simple intent from query.
        
        Args:
            query: User query
            
        Returns:
            Intent classification
        """
        query_lower = query.lower()
        
        # Simple rule-based intent classification
        if any(word in query_lower for word in ["what is", "tell me about", "describe", "explain"]):
            return "information"
            
        elif any(word in query_lower for word in ["why", "reason", "cause"]):
            return "explanation"
            
        elif any(word in query_lower for word in ["how", "trend", "movement", "performance"]):
            return "analysis"
            
        elif any(word in query_lower for word in ["up", "down", "increase", "decrease", "rise", "fall"]):
            return "movement"
            
        elif any(word in query_lower for word in ["prediction", "forecast", "future", "will", "expect"]):
            return "prediction"
            
        elif any(word in query_lower for word in ["compare", "versus", "vs", "difference", "between"]):
            return "comparison"
            
        else:
            return "general"
    
    def _extract_phrases(self, query: str) -> List[str]:
        """
        Extract potentially meaningful phrases from query.
        
        Args:
            query: User query
            
        Returns:
            List of phrases
        """
        words = query.lower().split()
        phrases = []
        
        # Extract 2-word phrases
        for i in range(len(words)-1):
            phrase = f"{words[i]} {words[i+1]}"
            if (
                not any(word in self.stop_words for word in [words[i], words[i+1]]) and
                len(words[i]) > 2 and len(words[i+1]) > 2
            ):
                phrases.append(phrase)
        
        # Extract 3-word phrases
        for i in range(len(words)-2):
            phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
            # Middle word can be a stopword, but not first and last
            if (
                words[i] not in self.stop_words and
                words[i+2] not in self.stop_words and
                len(words[i]) > 2 and len(words[i+2]) > 2
            ):
                phrases.append(phrase)
        
        return phrases
    
    def _identify_key_terms(self, query: str, entities: Dict[str, List[str]]) -> Dict[str, float]:
        """
        Identify key terms in query for relevance ranking with weights.
        
        Args:
            query: User query
            entities: Extracted entities
            
        Returns:
            Dictionary of terms with weights
        """
        term_weights = {}
        
        # Assign weights to entities
        entity_types = {
            "companies": 10.0,  # Highest priority
            "indices": 8.0,
            "sectors": 6.0,
            "keywords": 2.0    # Lowest priority
        }
        
        # Add extracted entities to term weights
        for entity_type, items in entities.items():
            if entity_type in entity_types:
                for item in items:
                    term_weights[item.lower()] = entity_types[entity_type]
        
        # Add domain-specific terms from query
        query_tokens = word_tokenize(query.lower())
        for token in query_tokens:
            if token in self.domain_weights and token not in term_weights:
                term_weights[token] = self.domain_weights[token]
        
        return term_weights
    
    def score_article_relevance(self, article: Dict, query_info: Dict) -> Tuple[float, List[str], bool]:
        """
        Score article relevance to a processed query.
        
        Args:
            article: Article dictionary
            query_info: Processed query information
            
        Returns:
            Tuple of (relevance score, matched terms, has exact match)
        """
        title = article.get("title", "").lower()
        content = article.get("content", "").lower() if article.get("content") else ""
        date_str = article.get("date", "")
        
        # Initialize score and tracking
        relevance_score = 0.0
        matched_terms = []
        has_exact_match = False
        
        # Get entities and key terms from query
        query_entities = query_info.get("entities", {})
        key_terms = query_info.get("key_terms", {})
        phrases = query_info.get("phrases", [])
        
        # Check for company exact matches (highest priority)
        for company in query_entities.get("companies", []):
            company_lower = company.lower()
            
            # Check for exact match in title (highest score)
            if company_lower in title:
                has_exact_match = True
                matched_terms.append(company)
                relevance_score += 20.0  # Highest boost for company in title
            
            # Check for exact match in content
            elif company_lower in content:
                matched_terms.append(company)
                relevance_score += 10.0  # High boost for company in content
        
        # Check for index and sector matches
        for idx in query_entities.get("indices", []):
            idx_lower = idx.lower()
            if idx_lower in title:
                matched_terms.append(idx)
                relevance_score += 15.0
            elif idx_lower in content:
                matched_terms.append(idx)
                relevance_score += 7.5
        
        for sector in query_entities.get("sectors", []):
            sector_lower = sector.lower()
            if sector_lower in title:
                matched_terms.append(sector)
                relevance_score += 12.0
            elif sector_lower in content:
                matched_terms.append(sector)
                relevance_score += 6.0
        
        # Check for phrase matches (higher weight than individual terms)
        for phrase in phrases:
            if phrase in title:
                matched_terms.append(phrase)
                relevance_score += 8.0
            elif phrase in content:
                matched_terms.append(phrase)
                relevance_score += 4.0
        
        # Check for keyword matches with term weights
        for term, weight in key_terms.items():
            # Check title (higher weight)
            if term in title:
                matched_terms.append(term)
                relevance_score += weight * 3.0
            # Check content (lower weight)
            elif term in content:
                matched_terms.append(term)
                relevance_score += weight
        
        # Boost recent articles (within last 7 days)
        try:
            # Convert date string to datetime
            if isinstance(date_str, str):
                article_date = datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                days_old = (datetime.datetime.now() - article_date).days
                
                # Apply recency boost with decay
                if days_old <= 1:
                    relevance_score *= 1.5  # Very recent (same day or yesterday)
                elif days_old <= 3:
                    relevance_score *= 1.3  # Recent (2-3 days)
                elif days_old <= 7:
                    relevance_score *= 1.1  # Somewhat recent (4-7 days)
        except:
            # If date parsing fails, don't apply recency boost
            pass
        
        # Apply intent-specific boosts
        intent = query_info.get("intent", "general")
        if intent == "movement" and any(term in title.lower() for term in ["up", "down", "rise", "fall", "gain", "loss"]):
            relevance_score *= 1.2
        elif intent == "explanation" and any(term in title.lower() for term in ["why", "because", "reason", "due to"]):
            relevance_score *= 1.2
        
        # Remove duplicates from matched terms
        matched_terms = list(set(matched_terms))
        
        return (relevance_score, matched_terms, has_exact_match)
    
    def get_relevant_sources(self, articles: List[Dict], query: str, top_n: int = 5) -> List[Dict]:
        """
        Get relevant sources based on user query using advanced NLP matching.
        
        Args:
            articles: List of article dictionaries
            query: User query
            top_n: Number of top sources to return
            
        Returns:
            List of relevant sources
        """
        # Process the query
        query_info = self.process_query(query)
        
        # Score and rank articles
        scored_articles = []
        for article in articles:
            score, matches, has_exact_match = self.score_article_relevance(article, query_info)
            
            if matches:  # Only include if there's at least one match
                scored_articles.append({
                    "title": article.get("title", ""),
                    "source": article.get("source", ""),
                    "date": article.get("date", ""),
                    "matches": matches,
                    "relevance_score": score,
                    "exact_match": has_exact_match
                })
        
        # Sort by relevance score (highest first)
        scored_articles.sort(key=lambda x: (x.get("exact_match", False), x.get("relevance_score", 0), x.get("date", "")), reverse=True)
        
        # Two-tier approach: prioritize exact matches if available
        if any(article.get("exact_match", False) for article in scored_articles):
            # Get exact matches
            exact_matches = [a for a in scored_articles if a.get("exact_match", False)]
            # Add some high-scoring non-exact matches
            other_relevant = [a for a in scored_articles if not a.get("exact_match", False)][:2]
            
            # Combine and limit to top_n
            return (exact_matches + other_relevant)[:top_n]
        else:
            # Just return top scored articles
            return scored_articles[:top_n]
    
    def _clean_text(self, text: str) -> str:
        """
        Clean text by removing URLs, HTML tags, and normalizing.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove URLs
        text = self.url_pattern.sub('', text)
        
        # Remove HTML tags
        text = self.html_pattern.sub('', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def _load_financial_entities(self) -> Dict[str, Any]:
        """
        Load financial entities for entity extraction.
        
        Returns:
            Dictionary with financial entity information
        """
        # In a real implementation, this would load from a more comprehensive source
        # or database, possibly with regular updates
        
        # Enhanced symbols dict with symbol to company name mapping
        symbols = {
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
            "TATASTEEL": "Tata Steel",
            "ADANIENT": "Adani Enterprises",
            "ADANIPORTS": "Adani Ports",
            "SUNPHARMA": "Sun Pharma"
        }
        
        return {
            "companies": [
                "Reliance Industries", "TCS", "HDFC Bank", "Infosys", "HUL", "ITC",
                "Bharti Airtel", "ICICI Bank", "Kotak Mahindra Bank", "Axis Bank",
                "State Bank of India", "Bajaj Finance", "Asian Paints", "Maruti Suzuki",
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
            ],
            "symbols": symbols
        } 