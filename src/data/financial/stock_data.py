"""
Module for retrieving stock data.
"""
import os
import json
import csv
from typing import Dict, List, Optional, Union
import datetime
import requests
import pandas as pd


class StockDataRetriever:
    """Class for retrieving stock data."""
    
    def __init__(self, data_dir: str = "./data/financial/stocks"):
        """
        Initialize stock data retriever.
        
        Args:
            data_dir: Directory to store stock data
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.stock_list = None
    
    def download_stock_list(self, force_update: bool = False) -> List[Dict]:
        """
        Download list of stocks (or load from cache).
        
        Args:
            force_update: Whether to force update the list from the source
            
        Returns:
            List of stock dictionaries
        """
        cache_file = os.path.join(self.data_dir, "stock_list.json")
        
        # Return cached data if available and not forcing update
        if not force_update and os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                self.stock_list = json.load(f)
                return self.stock_list
        
        # URL should be provided by the hackathon, but for now we'll use a placeholder
        # In a real implementation, you would use the actual URL provided in the challenge
        url = "https://www1.nseindia.com/content/equities/EQUITY_L.csv"
        
        try:
            # Download stock list
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Save raw data
            raw_file = os.path.join(self.data_dir, "stock_list_raw.csv")
            with open(raw_file, 'wb') as f:
                f.write(response.content)
            
            # Parse CSV
            stocks = []
            with open(raw_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    stocks.append({
                        "symbol": row.get("SYMBOL", ""),
                        "name": row.get("NAME OF COMPANY", ""),
                        "series": row.get("SERIES", ""),
                        "isin": row.get("ISIN NUMBER", ""),
                        "sector": row.get("INDUSTRY", "")
                    })
            
            # Save processed data
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(stocks, f, ensure_ascii=False, indent=2)
            
            self.stock_list = stocks
            return stocks
            
        except Exception as e:
            print(f"Error downloading stock list: {e}")
            # Return empty list if download fails
            return []
    
    def get_stock_data(self, symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Get historical stock data for a symbol.
        
        Args:
            symbol: Stock symbol
            start_date: Start date (format: YYYY-MM-DD)
            end_date: End date (format: YYYY-MM-DD)
            
        Returns:
            DataFrame with stock data
        """
        if not start_date:
            # Default to 1 year ago
            start_date = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime("%Y-%m-%d")
        
        if not end_date:
            # Default to today
            end_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Check if data is cached
        cache_file = os.path.join(self.data_dir, f"{symbol}_{start_date}_{end_date}.csv")
        if os.path.exists(cache_file):
            return pd.read_csv(cache_file, parse_dates=["Date"], index_col="Date")
        
        # For real implementation, you would use a data source provided by the hackathon
        # This is just a placeholder - in a real scenario, you'd use the actual data source
        # For NSE data, you might need to use their API or scrape from their website
        try:
            # Example URL (not real)
            base_url = "https://query1.finance.yahoo.com/v7/finance/download"
            params = {
                "period1": int(datetime.datetime.strptime(start_date, "%Y-%m-%d").timestamp()),
                "period2": int(datetime.datetime.strptime(end_date, "%Y-%m-%d").timestamp()),
                "interval": "1d",
                "events": "history",
                "includeAdjustedClose": "true"
            }
            
            # This is a placeholder. In a real implementation, you would use the proper API
            url = f"{base_url}/{symbol}.NS"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            # Save raw data
            with open(cache_file, 'wb') as f:
                f.write(response.content)
            
            # Load as dataframe
            df = pd.read_csv(cache_file, parse_dates=["Date"], index_col="Date")
            return df
            
        except Exception as e:
            print(f"Error fetching stock data for {symbol}: {e}")
            return pd.DataFrame()  # Return empty dataframe
    
    def search_stocks(self, query: str) -> List[Dict]:
        """
        Search for stocks by name or symbol.
        
        Args:
            query: Search query
            
        Returns:
            List of matching stock dictionaries
        """
        if not self.stock_list:
            self.download_stock_list()
        
        if not self.stock_list:
            return []
        
        query = query.lower()
        matches = []
        
        for stock in self.stock_list:
            if (query in stock.get("symbol", "").lower() or
                query in stock.get("name", "").lower() or
                query in stock.get("isin", "").lower()):
                matches.append(stock)
        
        return matches


if __name__ == "__main__":
    # Example usage
    retriever = StockDataRetriever()
    stocks = retriever.download_stock_list()
    print(f"Downloaded {len(stocks)} stocks")
    
    # Search for a stock
    matches = retriever.search_stocks("infosys")
    for match in matches:
        print(f"Found: {match['symbol']} - {match['name']} ({match['isin']})")
    
    # Get historical data
    if matches:
        symbol = matches[0]["symbol"]
        data = retriever.get_stock_data(symbol)
        print(f"Got {len(data)} days of data for {symbol}")
        print(data.head()) 