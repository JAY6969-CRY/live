"""
Economic Times news scraper.
"""
import datetime
from typing import Dict, List, Optional
import re
from bs4 import BeautifulSoup

from src.data.scrapers.news_scraper import NewsScraperBase


class EconomicTimesScraper(NewsScraperBase):
    """Scraper for Economic Times."""
    
    def __init__(self):
        super().__init__(
            name="Economic Times",
            base_url="https://economictimes.indiatimes.com"
        )
        self.categories = {
            "markets": "/markets/stocks/news",
            "mutual_funds": "/mutual-funds/mf-news",
            "economy": "/news/economy",
            "companies": "/news/company",
            "industry": "/industry",
        }
    
    def scrape_headlines(self, category: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """
        Scrape headlines from Economic Times.
        
        Args:
            category: Category of news to scrape
            limit: Maximum number of headlines to scrape
            
        Returns:
            List of dictionaries containing headline data
        """
        if category and category not in self.categories:
            raise ValueError(f"Invalid category: {category}. Valid categories: {list(self.categories.keys())}")
        
        url = self.base_url + (self.categories.get(category, ""))
        soup = self.get_soup(url)
        
        headlines = []
        article_elements = soup.select(".eachStory")
        
        for article in article_elements[:limit]:
            try:
                headline_element = article.select_one(".title")
                link_element = headline_element.find("a") if headline_element else None
                
                if not link_element:
                    continue
                    
                title = self.clean_text(link_element.text)
                url = link_element.get("href")
                if url and not url.startswith("http"):
                    url = self.base_url + url
                
                # Extract date if available
                date_element = article.select_one(".date-format")
                date_text = date_element.text if date_element else None
                
                # Extract summary if available
                summary_element = article.select_one(".desc")
                summary = self.clean_text(summary_element.text) if summary_element else ""
                
                headlines.append({
                    "title": title,
                    "url": url,
                    "source": self.name,
                    "category": category,
                    "date": self.extract_date(date_text) if date_text else datetime.datetime.now(),
                    "summary": summary,
                })
            except Exception as e:
                print(f"Error scraping headline: {e}")
                continue
        
        return headlines
    
    def scrape_article(self, url: str) -> Dict:
        """
        Scrape a full article from Economic Times.
        
        Args:
            url: URL of the article to scrape
            
        Returns:
            Dictionary containing article data
        """
        soup = self.get_soup(url)
        
        try:
            # Extract title
            title_element = soup.select_one("h1.artTitle")
            title = self.clean_text(title_element.text) if title_element else ""
            
            # Extract date
            date_element = soup.select_one(".publish_on")
            date_text = date_element.text if date_element else None
            
            # Extract author
            author_element = soup.select_one(".author")
            author = self.clean_text(author_element.text) if author_element else "Unknown"
            
            # Extract content
            content_elements = soup.select(".artText p")
            content = "\n\n".join([self.clean_text(p.text) for p in content_elements])
            
            # Extract tags/keywords
            tag_elements = soup.select(".keyTags .keyDiv a")
            tags = [self.clean_text(tag.text) for tag in tag_elements]
            
            # Try to extract related stocks/companies
            stock_elements = soup.select(".relatedStock a")
            related_stocks = [self.clean_text(stock.text) for stock in stock_elements]
            
            return {
                "title": title,
                "url": url,
                "source": self.name,
                "date": self.extract_date(date_text) if date_text else datetime.datetime.now(),
                "author": author,
                "content": content,
                "tags": tags,
                "related_stocks": related_stocks,
            }
        except Exception as e:
            print(f"Error scraping article: {e}")
            return {
                "title": "",
                "url": url,
                "source": self.name,
                "date": datetime.datetime.now(),
                "author": "Unknown",
                "content": "",
                "tags": [],
                "related_stocks": [],
                "error": str(e)
            }
    
    def extract_date(self, date_text: str) -> datetime.datetime:
        """
        Extract date from Economic Times date format.
        
        Args:
            date_text: Text containing a date
            
        Returns:
            Parsed datetime object
        """
        if not date_text:
            return datetime.datetime.now()
        
        # Example: "Last Updated: Apr 15, 2023, 10:30 AM IST"
        date_text = self.clean_text(date_text)
        match = re.search(r'(\w+ \d+, \d{4}, \d{1,2}:\d{2} (?:AM|PM))', date_text)
        
        if match:
            date_str = match.group(1)
            try:
                return datetime.datetime.strptime(date_str, "%b %d, %Y, %I:%M %p")
            except ValueError:
                pass
        
        # Fall back to parent class implementation
        return super().extract_date(date_text) 