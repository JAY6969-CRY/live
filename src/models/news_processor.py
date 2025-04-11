"""
Module for processing news articles with NLP.
"""
import os
import json
import datetime
from typing import Dict, List, Optional, Union, Any
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.sentiment import SentimentIntensityAnalyzer
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


class NewsProcessor:
    """Class for processing news articles with NLP."""
    
    def __init__(self, data_dir: str = "./data/processed/news"):
        """
        Initialize news processor.
        
        Args:
            data_dir: Directory to store processed news data
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Download NLTK data if needed
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet')
        
        try:
            nltk.data.find('sentiment/vader_lexicon.zip')
        except LookupError:
            nltk.download('vader_lexicon')
        
        # Initialize NLTK tools
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        
        # Compile regex patterns
        self.url_pattern = re.compile(r'https?://\S+|www\.\S+')
        self.html_pattern = re.compile(r'<.*?>')
        self.punctuation_pattern = re.compile(r'[^\w\s]')
        
        # Load financial entities
        self.financial_entities = self._load_financial_entities()
    
    def process_article(self, article: Dict) -> Dict:
        """
        Process a news article with NLP.
        
        Args:
            article: Article dictionary
            
        Returns:
            Processed article dictionary
        """
        # Extract content
        content = article.get("content", "")
        title = article.get("title", "")
        
        # Clean text
        cleaned_content = self._clean_text(content)
        
        # Tokenize and lemmatize
        tokens = self._tokenize_and_lemmatize(cleaned_content)
        
        # Extract named entities
        entities = self._extract_entities(title, cleaned_content)
        
        # Extract keywords
        keywords = self._extract_keywords(cleaned_content)
        
        # Analyze sentiment
        sentiment = self._analyze_sentiment(cleaned_content)
        
        # Add processed data to article
        processed_article = article.copy()
        processed_article.update({
            "processed": {
                "cleaned_content": cleaned_content,
                "tokens": tokens,
                "entities": entities,
                "keywords": keywords,
                "sentiment": sentiment
            }
        })
        
        return processed_article
    
    def process_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Process multiple news articles with NLP.
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            List of processed article dictionaries
        """
        processed_articles = []
        
        for article in articles:
            try:
                processed_article = self.process_article(article)
                processed_articles.append(processed_article)
            except Exception as e:
                print(f"Error processing article {article.get('title', '')}: {e}")
                # Add the original article to maintain the list structure
                processed_articles.append(article)
        
        return processed_articles
    
    def save_processed_articles(self, articles: List[Dict], filename: Optional[str] = None):
        """
        Save processed articles to a JSON file.
        
        Args:
            articles: List of processed article dictionaries
            filename: Name of file to save to (default: processed_articles_YYYY-MM-DD.json)
        """
        if not filename:
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
            filename = f"processed_articles_{date_str}.json"
        
        # Convert datetime objects to strings
        articles_json = []
        for article in articles:
            article_copy = article.copy()
            if isinstance(article_copy.get("date"), datetime.datetime):
                article_copy["date"] = article_copy["date"].isoformat()
            articles_json.append(article_copy)
        
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(articles_json, f, ensure_ascii=False, indent=2)
        
        print(f"Saved {len(articles)} processed articles to {filepath}")
    
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
    
    def _tokenize_and_lemmatize(self, text: str) -> List[str]:
        """
        Tokenize and lemmatize text.
        
        Args:
            text: Text to tokenize and lemmatize
            
        Returns:
            List of lemmatized tokens
        """
        if not text:
            return []
        
        # Tokenize
        tokens = word_tokenize(text.lower())
        
        # Remove stopwords and punctuation
        tokens = [token for token in tokens if token not in self.stop_words and not self.punctuation_pattern.match(token)]
        
        # Lemmatize
        lemmatized_tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
        
        return lemmatized_tokens
    
    def _extract_entities(self, title: str, content: str) -> Dict[str, List[str]]:
        """
        Extract named entities from text.
        
        Args:
            title: Article title
            content: Article content
            
        Returns:
            Dictionary with entity types and values
        """
        # This is a simplified implementation. In a real scenario, you would use
        # a more sophisticated NER model like spaCy or BERT-based models
        
        # For now, we'll just look for financial entities in the text
        combined_text = f"{title} {content}"
        
        entities = {
            "companies": [],
            "sectors": [],
            "indices": [],
            "persons": []
        }
        
        for company in self.financial_entities.get("companies", []):
            if company.lower() in combined_text.lower():
                entities["companies"].append(company)
        
        for sector in self.financial_entities.get("sectors", []):
            if sector.lower() in combined_text.lower():
                entities["sectors"].append(sector)
        
        for index in self.financial_entities.get("indices", []):
            if index.lower() in combined_text.lower():
                entities["indices"].append(index)
        
        # Attempt to find person names (this is very basic and would need improvement)
        words = combined_text.split()
        for i in range(len(words) - 1):
            if (words[i][0].isupper() and words[i+1][0].isupper() and
                words[i] not in self.stop_words and words[i+1] not in self.stop_words):
                person = f"{words[i]} {words[i+1]}"
                if person not in entities["persons"]:
                    entities["persons"].append(person)
        
        return entities
    
    def _extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """
        Extract keywords from text using TF-IDF.
        
        Args:
            text: Text to extract keywords from
            top_n: Number of top keywords to extract
            
        Returns:
            List of keywords
        """
        if not text or len(text.split()) < 3:
            return []
        
        # Use TF-IDF to extract keywords
        tfidf = TfidfVectorizer(stop_words='english', max_features=top_n)
        try:
            tfidf_matrix = tfidf.fit_transform([text])
            feature_names = tfidf.get_feature_names_out()
            
            # Get top keywords
            keywords = [feature_names[i] for i in tfidf_matrix.toarray()[0].argsort()[-top_n:][::-1]]
            return keywords
        except Exception as e:
            print(f"Error extracting keywords: {e}")
            return []
    
    def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment scores
        """
        if not text:
            return {"compound": 0.0, "positive": 0.0, "negative": 0.0, "neutral": 0.0}
        
        # Get sentiment scores
        sentiment_scores = self.sentiment_analyzer.polarity_scores(text)
        
        return sentiment_scores
    
    def _load_financial_entities(self) -> Dict[str, List[str]]:
        """
        Load financial entities for entity extraction.
        
        Returns:
            Dictionary with financial entity lists
        """
        # In a real implementation, this would load from a more comprehensive source
        # For now, we'll just hardcode some examples
        return {
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


if __name__ == "__main__":
    # Example usage
    processor = NewsProcessor()
    
    # Example article
    article = {
        "title": "Reliance Industries Reports Q2 Results, Profit Rises 10%",
        "content": "Reliance Industries Ltd (RIL) on Friday reported a 10% year-on-year rise in consolidated net profit to Rs 15,512 crore for the quarter ended September 30, 2023. The oil-to-telecom conglomerate's revenue from operations rose 3.5% to Rs 2.32 lakh crore. The company's telecom arm, Jio, saw a 12% increase in profits, while the retail business grew by 15%. Chairman Mukesh Ambani said the results reflect the resilience of the company's diversified portfolio in a challenging economic environment. The stock closed 2% higher on the NSE ahead of the results.",
        "source": "Economic Times",
        "date": datetime.datetime.now(),
        "url": "https://economictimes.indiatimes.com/example"
    }
    
    # Process article
    processed_article = processor.process_article(article)
    
    # Print results
    print("Sentiment:", processed_article["processed"]["sentiment"])
    print("Entities:", processed_article["processed"]["entities"])
    print("Keywords:", processed_article["processed"]["keywords"])
    
    # Save to file
    processor.save_processed_articles([processed_article]) 