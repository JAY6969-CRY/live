"""
Scraper manager to handle multiple news sources.
"""
import datetime
import os
import json
from typing import Dict, List, Optional, Type, Union
import concurrent.futures

from src.data.scrapers.news_scraper import NewsScraperBase
from src.data.scrapers.economic_times_scraper import EconomicTimesScraper


class ScraperManager:
    """Manager for multiple news scrapers."""
    
    def __init__(self, output_dir: str = "./data/scraped"):
        """
        Initialize scraper manager.
        
        Args:
            output_dir: Directory to save scraped data
        """
        self.output_dir = output_dir
        self.scrapers = {}
        
        # Register scrapers
        self.register_scraper(EconomicTimesScraper)
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    def register_scraper(self, scraper_class: Type[NewsScraperBase]):
        """
        Register a news scraper.
        
        Args:
            scraper_class: Class of scraper to register
        """
        scraper = scraper_class()
        self.scrapers[scraper.name] = scraper
    
    def get_scraper(self, name: str) -> NewsScraperBase:
        """
        Get a scraper by name.
        
        Args:
            name: Name of scraper to get
            
        Returns:
            Scraper instance
        """
        if name not in self.scrapers:
            raise ValueError(f"Scraper {name} not registered. Available scrapers: {list(self.scrapers.keys())}")
        return self.scrapers[name]
    
    def scrape_all_headlines(self, category: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """
        Scrape headlines from all registered scrapers.
        
        Args:
            category: Category of news to scrape
            limit: Maximum number of headlines to scrape per source
            
        Returns:
            List of dictionaries containing headline data
        """
        all_headlines = []
        
        # Use ThreadPoolExecutor to scrape from multiple sources in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.scrapers)) as executor:
            future_to_scraper = {
                executor.submit(scraper.scrape_headlines, category, limit): scraper.name
                for scraper in self.scrapers.values()
            }
            
            for future in concurrent.futures.as_completed(future_to_scraper):
                scraper_name = future_to_scraper[future]
                try:
                    headlines = future.result()
                    all_headlines.extend(headlines)
                    print(f"Scraped {len(headlines)} headlines from {scraper_name}")
                except Exception as e:
                    print(f"Error scraping headlines from {scraper_name}: {e}")
        
        # Sort by date (newest first)
        all_headlines.sort(key=lambda x: x.get("date", datetime.datetime.now()), reverse=True)
        
        return all_headlines
    
    def scrape_articles(self, urls: List[str]) -> List[Dict]:
        """
        Scrape articles from multiple URLs.
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            List of dictionaries containing article data
        """
        articles = []
        
        # Determine which scraper to use for each URL
        url_to_scraper = {}
        for url in urls:
            for scraper_name, scraper in self.scrapers.items():
                if scraper.base_url in url:
                    url_to_scraper[url] = scraper
                    break
        
        # Use ThreadPoolExecutor to scrape multiple articles in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(10, len(urls))) as executor:
            future_to_url = {
                executor.submit(url_to_scraper[url].scrape_article, url): url
                for url in urls if url in url_to_scraper
            }
            
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    article = future.result()
                    articles.append(article)
                    print(f"Scraped article: {article.get('title', '')}")
                except Exception as e:
                    print(f"Error scraping article {url}: {e}")
        
        return articles
    
    def save_headlines(self, headlines: List[Dict], filename: Optional[str] = None):
        """
        Save headlines to a JSON file.
        
        Args:
            headlines: List of headline dictionaries
            filename: Name of file to save to (default: headlines_YYYY-MM-DD.json)
        """
        if not filename:
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
            filename = f"headlines_{date_str}.json"
        
        # Convert datetime objects to strings
        headlines_json = []
        for headline in headlines:
            headline_copy = headline.copy()
            if isinstance(headline_copy.get("date"), datetime.datetime):
                headline_copy["date"] = headline_copy["date"].isoformat()
            headlines_json.append(headline_copy)
        
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(headlines_json, f, ensure_ascii=False, indent=2)
        
        print(f"Saved {len(headlines)} headlines to {filepath}")
    
    def save_articles(self, articles: List[Dict], filename: Optional[str] = None):
        """
        Save articles to a JSON file.
        
        Args:
            articles: List of article dictionaries
            filename: Name of file to save to (default: articles_YYYY-MM-DD.json)
        """
        if not filename:
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
            filename = f"articles_{date_str}.json"
        
        # Convert datetime objects to strings
        articles_json = []
        for article in articles:
            article_copy = article.copy()
            if isinstance(article_copy.get("date"), datetime.datetime):
                article_copy["date"] = article_copy["date"].isoformat()
                
            # Add source_file to each article for traceability
            article_copy["source_file"] = filename
                
            articles_json.append(article_copy)
        
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(articles_json, f, ensure_ascii=False, indent=2)
        
        print(f"Saved {len(articles)} articles to {filepath}")


if __name__ == "__main__":
    # Example usage
    manager = ScraperManager()
    headlines = manager.scrape_all_headlines(category="markets", limit=10)
    manager.save_headlines(headlines)
    
    # Scrape full articles for the first 3 headlines
    if headlines:
        article_urls = [h["url"] for h in headlines[:3]]
        articles = manager.scrape_articles(article_urls)
        manager.save_articles(articles) 