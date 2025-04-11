"""
Command-line interface for NewsSense.
"""
import os
import sys
import json
import argparse
import datetime
from typing import Dict, List, Optional, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.scrapers.scraper_manager import ScraperManager
from src.data.financial.stock_data import StockDataRetriever
from src.data.financial.mutual_fund_data import MutualFundDataRetriever
from src.models.news_processor import NewsProcessor
from src.models.financial_qa import FinancialQA


class NewsSenseCLI:
    """Command-line interface for NewsSense."""
    
    def __init__(self):
        """Initialize NewsSense CLI."""
        self.scraper_manager = ScraperManager()
        self.stock_data = StockDataRetriever()
        self.mutual_fund_data = MutualFundDataRetriever()
        self.news_processor = NewsProcessor()
        
        # Initialize QA system if API key is available
        if "OPENAI_API_KEY" in os.environ:
            self.qa_system = FinancialQA(api_key=os.environ.get("OPENAI_API_KEY"))
        else:
            self.qa_system = None
    
    def ask(self, question: str) -> str:
        """
        Answer a financial question using news and financial data.
        
        Args:
            question: Question to answer
            
        Returns:
            Answer to the question
        """
        if not self.qa_system:
            return "Error: QA system requires OpenAI API key. Please set OPENAI_API_KEY environment variable."
        
        try:
            answer = self.qa_system.answer_question(question)
            return answer
        except Exception as e:
            return f"Error answering question: {str(e)}"
    
    def get_headlines(self, category: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """
        Get latest news headlines.
        
        Args:
            category: News category
            limit: Maximum number of headlines to return
            
        Returns:
            List of headline dictionaries
        """
        try:
            headlines = self.scraper_manager.scrape_all_headlines(category, limit)
            return headlines
        except Exception as e:
            print(f"Error fetching headlines: {str(e)}")
            return []
    
    def get_article(self, url: str) -> Dict:
        """
        Get full article by URL.
        
        Args:
            url: URL of article to fetch
            
        Returns:
            Article dictionary
        """
        try:
            articles = self.scraper_manager.scrape_articles([url])
            if articles:
                return articles[0]
            else:
                return {"error": "Article not found"}
        except Exception as e:
            return {"error": f"Error fetching article: {str(e)}"}
    
    def search_stocks(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for stocks by name or symbol.
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            List of matching stock dictionaries
        """
        try:
            stocks = self.stock_data.search_stocks(query)
            return stocks[:limit]
        except Exception as e:
            print(f"Error searching stocks: {str(e)}")
            return []
    
    def search_mutual_funds(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for mutual funds by name or AMC.
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            List of matching mutual fund dictionaries
        """
        try:
            funds = self.mutual_fund_data.search_funds(query)
            return funds[:limit]
        except Exception as e:
            print(f"Error searching mutual funds: {str(e)}")
            return []
    
    def process_article(self, article: Dict) -> Dict:
        """
        Process an article with NLP.
        
        Args:
            article: Article dictionary
            
        Returns:
            Processed article dictionary
        """
        try:
            processed_article = self.news_processor.process_article(article)
            return processed_article
        except Exception as e:
            print(f"Error processing article: {str(e)}")
            return article
    
    def format_headline(self, headline: Dict) -> str:
        """
        Format a headline for display.
        
        Args:
            headline: Headline dictionary
            
        Returns:
            Formatted headline string
        """
        title = headline.get("title", "No Title")
        source = headline.get("source", "Unknown")
        date = headline.get("date", "")
        
        if isinstance(date, datetime.datetime):
            date_str = date.strftime("%Y-%m-%d %H:%M")
        else:
            date_str = str(date)
        
        summary = headline.get("summary", "")
        
        return f"{title}\n{source} - {date_str}\n{summary}\n"
    
    def format_article(self, article: Dict) -> str:
        """
        Format an article for display.
        
        Args:
            article: Article dictionary
            
        Returns:
            Formatted article string
        """
        title = article.get("title", "No Title")
        source = article.get("source", "Unknown")
        date = article.get("date", "")
        
        if isinstance(date, datetime.datetime):
            date_str = date.strftime("%Y-%m-%d %H:%M")
        else:
            date_str = str(date)
        
        content = article.get("content", "No content available.")
        
        return f"{title}\n{source} - {date_str}\n\n{content}\n"
    
    def format_stock(self, stock: Dict) -> str:
        """
        Format a stock for display.
        
        Args:
            stock: Stock dictionary
            
        Returns:
            Formatted stock string
        """
        symbol = stock.get("symbol", "")
        name = stock.get("name", "")
        isin = stock.get("isin", "")
        sector = stock.get("sector", "Unknown")
        
        return f"{symbol} - {name}\nISIN: {isin}\nSector: {sector}\n"
    
    def format_mutual_fund(self, fund: Dict) -> str:
        """
        Format a mutual fund for display.
        
        Args:
            fund: Mutual fund dictionary
            
        Returns:
            Formatted mutual fund string
        """
        scheme_code = fund.get("scheme_code", "")
        scheme_name = fund.get("scheme_name", "")
        amc = fund.get("amc", "Unknown")
        category = fund.get("category", "Unknown")
        
        return f"{scheme_code} - {scheme_name}\nAMC: {amc}\nCategory: {category}\n"


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="NewsSense CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Ask question command
    ask_parser = subparsers.add_parser("ask", help="Ask a financial question")
    ask_parser.add_argument("question", help="Question to ask")
    
    # Headlines command
    headlines_parser = subparsers.add_parser("headlines", help="Get latest news headlines")
    headlines_parser.add_argument("--category", help="News category", choices=["markets", "mutual_funds", "economy", "companies"])
    headlines_parser.add_argument("--limit", help="Maximum number of headlines to return", type=int, default=10)
    
    # Article command
    article_parser = subparsers.add_parser("article", help="Get full article by URL")
    article_parser.add_argument("url", help="URL of article to fetch")
    
    # Search stocks command
    stocks_parser = subparsers.add_parser("stocks", help="Search for stocks")
    stocks_parser.add_argument("query", help="Search query")
    stocks_parser.add_argument("--limit", help="Maximum number of results to return", type=int, default=10)
    
    # Search mutual funds command
    funds_parser = subparsers.add_parser("funds", help="Search for mutual funds")
    funds_parser.add_argument("query", help="Search query")
    funds_parser.add_argument("--limit", help="Maximum number of results to return", type=int, default=10)
    
    # Interactive mode command
    subparsers.add_parser("interactive", help="Start interactive mode")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Initialize CLI
    cli = NewsSenseCLI()
    
    # Execute command
    if args.command == "ask":
        answer = cli.ask(args.question)
        print(f"Q: {args.question}")
        print(f"A: {answer}")
    
    elif args.command == "headlines":
        headlines = cli.get_headlines(args.category, args.limit)
        for i, headline in enumerate(headlines, 1):
            print(f"{i}. {cli.format_headline(headline)}")
            print("---")
    
    elif args.command == "article":
        article = cli.get_article(args.url)
        if "error" in article:
            print(article["error"])
        else:
            print(cli.format_article(article))
    
    elif args.command == "stocks":
        stocks = cli.search_stocks(args.query, args.limit)
        if not stocks:
            print("No stocks found matching your query.")
        else:
            for i, stock in enumerate(stocks, 1):
                print(f"{i}. {cli.format_stock(stock)}")
                print("---")
    
    elif args.command == "funds":
        funds = cli.search_mutual_funds(args.query, args.limit)
        if not funds:
            print("No mutual funds found matching your query.")
        else:
            for i, fund in enumerate(funds, 1):
                print(f"{i}. {cli.format_mutual_fund(fund)}")
                print("---")
    
    elif args.command == "interactive":
        print("NewsSense Interactive Mode")
        print("Type 'exit' or 'quit' to exit")
        print("Type 'help' for available commands")
        
        while True:
            user_input = input("\n> ")
            
            if user_input.lower() in ["exit", "quit"]:
                break
            
            if user_input.lower() == "help":
                print("Commands:")
                print("  ask <question>          - Ask a financial question")
                print("  headlines [category]    - Get latest news headlines")
                print("  article <url>           - Get full article by URL")
                print("  stocks <query>          - Search for stocks")
                print("  funds <query>           - Search for mutual funds")
                print("  exit, quit              - Exit interactive mode")
                continue
            
            parts = user_input.split(maxsplit=1)
            if not parts:
                continue
            
            command = parts[0].lower()
            args_str = parts[1] if len(parts) > 1 else ""
            
            if command == "ask":
                if not args_str:
                    print("Usage: ask <question>")
                    continue
                answer = cli.ask(args_str)
                print(f"A: {answer}")
            
            elif command == "headlines":
                category = args_str if args_str in ["markets", "mutual_funds", "economy", "companies"] else None
                headlines = cli.get_headlines(category, 5)
                for i, headline in enumerate(headlines, 1):
                    print(f"{i}. {cli.format_headline(headline)}")
                    print("---")
            
            elif command == "article":
                if not args_str:
                    print("Usage: article <url>")
                    continue
                article = cli.get_article(args_str)
                if "error" in article:
                    print(article["error"])
                else:
                    print(cli.format_article(article))
            
            elif command == "stocks":
                if not args_str:
                    print("Usage: stocks <query>")
                    continue
                stocks = cli.search_stocks(args_str, 5)
                if not stocks:
                    print("No stocks found matching your query.")
                else:
                    for i, stock in enumerate(stocks, 1):
                        print(f"{i}. {cli.format_stock(stock)}")
                        print("---")
            
            elif command == "funds":
                if not args_str:
                    print("Usage: funds <query>")
                    continue
                funds = cli.search_mutual_funds(args_str, 5)
                if not funds:
                    print("No mutual funds found matching your query.")
                else:
                    for i, fund in enumerate(funds, 1):
                        print(f"{i}. {cli.format_mutual_fund(fund)}")
                        print("---")
            
            else:
                # If not a command, treat as a question
                answer = cli.ask(user_input)
                print(f"A: {answer}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 