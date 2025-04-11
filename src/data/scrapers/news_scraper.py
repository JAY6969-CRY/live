"""
News scraper base module to handle scraping from various financial news sources.
"""
import abc
import datetime
from typing import Dict, List, Optional, Union
import requests
from bs4 import BeautifulSoup


class NewsScraperBase(abc.ABC):
    """Base class for all news scrapers."""
    
    def __init__(self, name: str, base_url: str):
        """
        Initialize a news scraper.
        
        Args:
            name: Name of the news source
            base_url: Base URL of the news source
        """
        self.name = name
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    @abc.abstractmethod
    def scrape_headlines(self, category: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """
        Scrape headlines from the news source.
        
        Args:
            category: Category of news to scrape
            limit: Maximum number of headlines to scrape
            
        Returns:
            List of dictionaries containing headline data
        """
        pass
    
    @abc.abstractmethod
    def scrape_article(self, url: str) -> Dict:
        """
        Scrape a full article from the given URL.
        
        Args:
            url: URL of the article to scrape
            
        Returns:
            Dictionary containing article data
        """
        pass
    
    def get_soup(self, url: str) -> BeautifulSoup:
        """
        Get a BeautifulSoup object for the given URL.
        
        Args:
            url: URL to get soup for
            
        Returns:
            BeautifulSoup object
        """
        response = self.session.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    
    def clean_text(self, text: str) -> str:
        """
        Clean text by removing extra whitespace and normalizing.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        return " ".join(text.split())
    
    def extract_date(self, date_text: str) -> datetime.datetime:
        """
        Extract date from a text string.
        
        Args:
            date_text: Text containing a date
            
        Returns:
            Parsed datetime object
        """
        # This is a simple implementation. Each subclass may need to override this
        # with more specific parsing logic for their particular news source
        # For now, we'll try a few common formats
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%d %b %Y",
            "%d %B %Y",
            "%d %b %Y %H:%M",
            "%d %B %Y %H:%M"
        ]
        
        for fmt in formats:
            try:
                return datetime.datetime.strptime(date_text.strip(), fmt)
            except ValueError:
                continue
                
        # If we can't parse the date, return the current time
        return datetime.datetime.now() 