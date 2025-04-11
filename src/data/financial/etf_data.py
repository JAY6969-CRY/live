"""
Module for retrieving ETF data from Indian and US markets.
"""
import os
import json
import csv
from typing import Dict, List, Optional, Union
import datetime
import requests
import pandas as pd


class ETFDataRetriever:
    """Class for retrieving ETF data from Indian and US markets."""
    
    def __init__(self, data_dir: str = "./data/financial/etfs"):
        """
        Initialize ETF data retriever.
        
        Args:
            data_dir: Directory to store ETF data
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Separate lists for Indian and US ETFs
        self.indian_etfs = None
        self.us_etfs = None
    
    def download_indian_etf_list(self, force_update: bool = False) -> List[Dict]:
        """
        Download list of Indian ETFs (or load from cache).
        
        Args:
            force_update: Whether to force update the list from the source
            
        Returns:
            List of ETF dictionaries
        """
        cache_file = os.path.join(self.data_dir, "indian_etf_list.json")
        
        # Return cached data if available and not forcing update
        if not force_update and os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                self.indian_etfs = json.load(f)
                return self.indian_etfs
        
        # In a real implementation, you would use an actual data source
        # This is a placeholder with some popular Indian ETFs
        try:
            # Placeholder data
            etfs = [
                {
                    "symbol": "NIFTYBEES",
                    "name": "Nippon India ETF Nifty BeES",
                    "isin": "INF204KB14I2",
                    "fund_house": "Nippon India Mutual Fund",
                    "category": "Equity",
                    "index": "Nifty 50",
                    "country": "India"
                },
                {
                    "symbol": "BANKBEES",
                    "name": "Nippon India ETF Bank BeES",
                    "isin": "INF204KB12I6",
                    "fund_house": "Nippon India Mutual Fund",
                    "category": "Equity",
                    "index": "Nifty Bank",
                    "country": "India"
                },
                {
                    "symbol": "NETFIT",
                    "name": "Nippon India ETF Nifty IT",
                    "isin": "INF204KB18D8",
                    "fund_house": "Nippon India Mutual Fund",
                    "category": "Equity",
                    "index": "Nifty IT",
                    "country": "India"
                },
                {
                    "symbol": "KOTAKGOLD",
                    "name": "Kotak Gold ETF",
                    "isin": "INF174K01D64",
                    "fund_house": "Kotak Mahindra Mutual Fund",
                    "category": "Commodity",
                    "index": "Gold",
                    "country": "India"
                },
                {
                    "symbol": "SETFNIFBK",
                    "name": "SBI ETF Nifty Bank",
                    "isin": "INF200KA1HM3",
                    "fund_house": "SBI Mutual Fund",
                    "category": "Equity",
                    "index": "Nifty Bank",
                    "country": "India"
                },
                {
                    "symbol": "LIQUIDETF",
                    "name": "DSP Liquid ETF",
                    "isin": "INF189K01UQ2",
                    "fund_house": "DSP Mutual Fund",
                    "category": "Debt",
                    "index": "CRISIL Liquid Fund Index",
                    "country": "India"
                },
                {
                    "symbol": "ICICILIQ",
                    "name": "ICICI Prudential Liquid ETF",
                    "isin": "INF109KC1SP9",
                    "fund_house": "ICICI Prudential Mutual Fund",
                    "category": "Debt",
                    "index": "CRISIL Liquid Fund Index",
                    "country": "India"
                },
                {
                    "symbol": "LITETF",
                    "name": "LIC MF ETF Nifty 50",
                    "isin": "INF767K01EE2",
                    "fund_house": "LIC Mutual Fund",
                    "category": "Equity",
                    "index": "Nifty 50",
                    "country": "India"
                },
                {
                    "symbol": "PSUBNKBEES",
                    "name": "Nippon India ETF PSU Bank BeES",
                    "isin": "INF204KB13I4",
                    "fund_house": "Nippon India Mutual Fund",
                    "category": "Equity",
                    "index": "Nifty PSU Bank",
                    "country": "India"
                },
                {
                    "symbol": "NETFPHARMA",
                    "name": "Nippon India ETF Nifty Pharma",
                    "isin": "INF204KB19D6",
                    "fund_house": "Nippon India Mutual Fund",
                    "category": "Equity",
                    "index": "Nifty Pharma",
                    "country": "India"
                }
            ]
            
            # Save processed data
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(etfs, f, ensure_ascii=False, indent=2)
            
            self.indian_etfs = etfs
            return etfs
            
        except Exception as e:
            print(f"Error downloading Indian ETF list: {e}")
            # Return empty list if download fails
            return []
    
    def download_us_etf_list(self, force_update: bool = False) -> List[Dict]:
        """
        Download list of US ETFs (or load from cache).
        
        Args:
            force_update: Whether to force update the list from the source
            
        Returns:
            List of ETF dictionaries
        """
        cache_file = os.path.join(self.data_dir, "us_etf_list.json")
        
        # Return cached data if available and not forcing update
        if not force_update and os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                self.us_etfs = json.load(f)
                return self.us_etfs
        
        # In a real implementation, you would use an actual data source
        # This is a placeholder with some popular US ETFs
        try:
            # Placeholder data for popular US ETFs
            etfs = [
                {
                    "symbol": "SPY",
                    "name": "SPDR S&P 500 ETF Trust",
                    "isin": "US78462F1030",
                    "fund_house": "State Street Global Advisors",
                    "category": "Equity",
                    "index": "S&P 500",
                    "country": "US"
                },
                {
                    "symbol": "QQQ",
                    "name": "Invesco QQQ Trust",
                    "isin": "US46090E1038",
                    "fund_house": "Invesco",
                    "category": "Equity",
                    "index": "NASDAQ-100",
                    "country": "US"
                },
                {
                    "symbol": "VTI",
                    "name": "Vanguard Total Stock Market ETF",
                    "isin": "US9229087690",
                    "fund_house": "Vanguard",
                    "category": "Equity",
                    "index": "CRSP US Total Market Index",
                    "country": "US"
                },
                {
                    "symbol": "VOO",
                    "name": "Vanguard S&P 500 ETF",
                    "isin": "US9229083632",
                    "fund_house": "Vanguard",
                    "category": "Equity",
                    "index": "S&P 500",
                    "country": "US"
                },
                {
                    "symbol": "IVV",
                    "name": "iShares Core S&P 500 ETF",
                    "isin": "US4642872000",
                    "fund_house": "BlackRock",
                    "category": "Equity",
                    "index": "S&P 500",
                    "country": "US"
                },
                {
                    "symbol": "VEA",
                    "name": "Vanguard FTSE Developed Markets ETF",
                    "isin": "US9219438580",
                    "fund_house": "Vanguard",
                    "category": "Equity",
                    "index": "FTSE Developed All Cap ex US Index",
                    "country": "US"
                },
                {
                    "symbol": "BND",
                    "name": "Vanguard Total Bond Market ETF",
                    "isin": "US9219378356",
                    "fund_house": "Vanguard",
                    "category": "Bond",
                    "index": "Bloomberg U.S. Aggregate Float Adjusted Index",
                    "country": "US"
                },
                {
                    "symbol": "VWO",
                    "name": "Vanguard FTSE Emerging Markets ETF",
                    "isin": "US9220428588",
                    "fund_house": "Vanguard",
                    "category": "Equity",
                    "index": "FTSE Emerging Markets All Cap China A Inclusion Index",
                    "country": "US"
                },
                {
                    "symbol": "AGG",
                    "name": "iShares Core U.S. Aggregate Bond ETF",
                    "isin": "US4642872265",
                    "fund_house": "BlackRock",
                    "category": "Bond",
                    "index": "Bloomberg U.S. Aggregate Bond Index",
                    "country": "US"
                },
                {
                    "symbol": "GLD",
                    "name": "SPDR Gold Shares",
                    "isin": "US78463V1070",
                    "fund_house": "State Street Global Advisors",
                    "category": "Commodity",
                    "index": "LBMA Gold Price PM",
                    "country": "US"
                }
            ]
            
            # Save processed data
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(etfs, f, ensure_ascii=False, indent=2)
            
            self.us_etfs = etfs
            return etfs
            
        except Exception as e:
            print(f"Error downloading US ETF list: {e}")
            # Return empty list if download fails
            return []
    
    def get_etf_data(self, symbol: str, country: str = "India", start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Get historical ETF data for a symbol.
        
        Args:
            symbol: ETF symbol
            country: Country of the ETF (India or US)
            start_date: Start date (format: YYYY-MM-DD)
            end_date: End date (format: YYYY-MM-DD)
            
        Returns:
            DataFrame with ETF data
        """
        if not start_date:
            # Default to 1 year ago
            start_date = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime("%Y-%m-%d")
        
        if not end_date:
            # Default to today
            end_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Check if data is cached
        cache_file = os.path.join(self.data_dir, f"{symbol}_{country}_{start_date}_{end_date}.csv")
        if os.path.exists(cache_file):
            return pd.read_csv(cache_file, parse_dates=["Date"], index_col="Date")
        
        # For real implementation, you would use a data source provided by the hackathon
        # This is just a placeholder with some simulated data
        try:
            # Generate some placeholder data (in a real implementation this would be fetched from an API)
            start_ts = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            end_ts = datetime.datetime.strptime(end_date, "%Y-%m-%d")
            
            dates = []
            current = start_ts
            while current <= end_ts:
                if current.weekday() < 5:  # Only weekdays
                    dates.append(current)
                current += datetime.timedelta(days=1)
            
            # Generate random price data
            import numpy as np
            n = len(dates)
            if n == 0:
                return pd.DataFrame()
            
            # Start with a base price
            base_price = 100
            if symbol in ["SPY", "QQQ", "VOO", "IVV"]:
                base_price = 400
            elif symbol in ["VTI", "VEA", "VWO"]:
                base_price = 200
            elif symbol in ["NIFTYBEES", "BANKBEES"]:
                base_price = 150
            
            # Generate prices with some randomness but trending upward
            changes = np.random.normal(0.0005, 0.01, n).cumsum()
            closes = base_price * (1 + changes)
            opens = closes * np.random.normal(1, 0.002, n)
            highs = np.maximum(opens, closes) * np.random.normal(1.01, 0.005, n)
            lows = np.minimum(opens, closes) * np.random.normal(0.99, 0.005, n)
            volumes = np.random.randint(100000, 10000000, n)
            
            # Create DataFrame
            df = pd.DataFrame({
                'Date': dates,
                'Open': opens,
                'High': highs,
                'Low': lows,
                'Close': closes,
                'Volume': volumes
            })
            
            # Set Date as index
            df.set_index('Date', inplace=True)
            
            # Save to cache
            df.to_csv(cache_file)
            
            return df
            
        except Exception as e:
            print(f"Error fetching ETF data for {symbol}: {e}")
            return pd.DataFrame()  # Return empty dataframe
    
    def get_etf_holdings(self, symbol: str, country: str = "India") -> Dict:
        """
        Get holdings data for an ETF.
        
        Args:
            symbol: ETF symbol
            country: Country of the ETF (India or US)
            
        Returns:
            Dictionary with holdings data
        """
        # Check if data is cached
        cache_file = os.path.join(self.data_dir, f"holdings_{symbol}_{country}.json")
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # For real implementation, you would use a data source provided by the hackathon
        # This is just a placeholder with some simulated data based on the ETF
        try:
            holdings = {
                "symbol": symbol,
                "country": country,
                "as_of_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "stocks": [],
                "sectors": [],
                "asset_allocation": []
            }
            
            # Populate with placeholder data based on the ETF type
            if symbol == "NIFTYBEES" or symbol == "SPY" or symbol == "VOO" or symbol == "IVV":
                # These track broad market indices
                holdings["stocks"] = [
                    {"name": "Reliance Industries Ltd." if country == "India" else "Apple Inc.", "percentage": 9.8},
                    {"name": "HDFC Bank Ltd." if country == "India" else "Microsoft Corp.", "percentage": 8.2},
                    {"name": "Infosys Ltd." if country == "India" else "Amazon.com Inc.", "percentage": 7.5},
                    {"name": "ICICI Bank Ltd." if country == "India" else "Facebook Inc.", "percentage": 6.5},
                    {"name": "Tata Consultancy Services Ltd." if country == "India" else "Alphabet Inc.", "percentage": 6.0}
                ]
                
                holdings["sectors"] = [
                    {"name": "Financial Services", "percentage": 33.5},
                    {"name": "IT", "percentage": 18.2},
                    {"name": "Oil & Gas", "percentage": 12.8},
                    {"name": "Consumer Goods", "percentage": 11.5},
                    {"name": "Healthcare", "percentage": 7.2}
                ]
                
                holdings["asset_allocation"] = [
                    {"type": "Equity", "percentage": 99.2},
                    {"type": "Cash", "percentage": 0.8}
                ]
                
            elif symbol == "BANKBEES" or symbol == "SETFNIFBK":
                # These track banking indices
                holdings["stocks"] = [
                    {"name": "HDFC Bank Ltd.", "percentage": 32.5},
                    {"name": "ICICI Bank Ltd.", "percentage": 22.3},
                    {"name": "Kotak Mahindra Bank Ltd.", "percentage": 14.8},
                    {"name": "Axis Bank Ltd.", "percentage": 12.2},
                    {"name": "State Bank of India", "percentage": 10.5}
                ]
                
                holdings["sectors"] = [
                    {"name": "Private Sector Banks", "percentage": 82.5},
                    {"name": "Public Sector Banks", "percentage": 17.0},
                    {"name": "Cash", "percentage": 0.5}
                ]
                
                holdings["asset_allocation"] = [
                    {"type": "Equity", "percentage": 99.5},
                    {"type": "Cash", "percentage": 0.5}
                ]
                
            elif symbol == "QQQ":
                # This tracks the NASDAQ-100
                holdings["stocks"] = [
                    {"name": "Apple Inc.", "percentage": 12.5},
                    {"name": "Microsoft Corp.", "percentage": 10.8},
                    {"name": "Amazon.com Inc.", "percentage": 8.7},
                    {"name": "Facebook Inc.", "percentage": 4.3},
                    {"name": "Alphabet Inc.", "percentage": 7.2}
                ]
                
                holdings["sectors"] = [
                    {"name": "Information Technology", "percentage": 48.5},
                    {"name": "Communication Services", "percentage": 18.2},
                    {"name": "Consumer Discretionary", "percentage": 17.8},
                    {"name": "Healthcare", "percentage": 6.5},
                    {"name": "Consumer Staples", "percentage": 5.0}
                ]
                
                holdings["asset_allocation"] = [
                    {"type": "Equity", "percentage": 99.7},
                    {"type": "Cash", "percentage": 0.3}
                ]
                
            elif symbol == "KOTAKGOLD" or symbol == "GLD":
                # These track gold
                holdings["stocks"] = []
                
                holdings["sectors"] = [
                    {"name": "Precious Metals", "percentage": 99.5},
                    {"name": "Cash", "percentage": 0.5}
                ]
                
                holdings["asset_allocation"] = [
                    {"type": "Commodity", "percentage": 99.5},
                    {"type": "Cash", "percentage": 0.5}
                ]
                
            elif symbol == "LIQUIDETF" or symbol == "ICICILIQ":
                # These are liquid ETFs
                holdings["stocks"] = []
                
                holdings["sectors"] = [
                    {"name": "Treasury Bills", "percentage": 45.0},
                    {"name": "Commercial Paper", "percentage": 30.0},
                    {"name": "Certificates of Deposit", "percentage": 20.0},
                    {"name": "Cash", "percentage": 5.0}
                ]
                
                holdings["asset_allocation"] = [
                    {"type": "Debt", "percentage": 95.0},
                    {"type": "Cash", "percentage": 5.0}
                ]
                
            elif symbol in ["BND", "AGG"]:
                # These are bond ETFs
                holdings["stocks"] = []
                
                holdings["sectors"] = [
                    {"name": "Treasury", "percentage": 40.0},
                    {"name": "Government Agency", "percentage": 20.0},
                    {"name": "Investment-Grade Corporate", "percentage": 25.0},
                    {"name": "Mortgage-Backed Securities", "percentage": 12.0},
                    {"name": "Cash", "percentage": 3.0}
                ]
                
                holdings["asset_allocation"] = [
                    {"type": "Bond", "percentage": 97.0},
                    {"type": "Cash", "percentage": 3.0}
                ]
            
            # Save to cache
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(holdings, f, ensure_ascii=False, indent=2)
            
            return holdings
            
        except Exception as e:
            print(f"Error fetching holdings data for {symbol}: {e}")
            return {}  # Return empty dict
    
    def search_etfs(self, query: str, country: Optional[str] = None) -> List[Dict]:
        """
        Search for ETFs by name, symbol, or index.
        
        Args:
            query: Search query
            country: Country filter (India or US)
            
        Returns:
            List of matching ETF dictionaries
        """
        # Load ETF lists if not already loaded
        if not self.indian_etfs:
            self.download_indian_etf_list()
        
        if not self.us_etfs:
            self.download_us_etf_list()
        
        # Create combined list based on country filter
        etfs_to_search = []
        if country is None or country.lower() == "india":
            etfs_to_search.extend(self.indian_etfs or [])
        
        if country is None or country.lower() == "us":
            etfs_to_search.extend(self.us_etfs or [])
        
        if not etfs_to_search:
            return []
        
        # Perform search
        query = query.lower()
        matches = []
        
        for etf in etfs_to_search:
            if (query in etf.get("symbol", "").lower() or
                query in etf.get("name", "").lower() or
                query in etf.get("isin", "").lower() or
                query in etf.get("index", "").lower() or
                query in etf.get("fund_house", "").lower()):
                matches.append(etf)
        
        return matches


if __name__ == "__main__":
    # Example usage
    retriever = ETFDataRetriever()
    
    # Get ETF lists
    indian_etfs = retriever.download_indian_etf_list()
    us_etfs = retriever.download_us_etf_list()
    
    print(f"Downloaded {len(indian_etfs)} Indian ETFs and {len(us_etfs)} US ETFs")
    
    # Search for ETFs
    search_results = retriever.search_etfs("nifty")
    print("\nSearch results for 'nifty':")
    for etf in search_results:
        print(f"{etf['symbol']} - {etf['name']} ({etf['country']})")
    
    # Get data for an ETF
    if search_results:
        symbol = search_results[0]["symbol"]
        country = search_results[0]["country"]
        data = retriever.get_etf_data(symbol, country)
        print(f"\nGot {len(data)} days of data for {symbol}")
        print(data.head())
        
        # Get holdings
        holdings = retriever.get_etf_holdings(symbol, country)
        print(f"\nTop holdings for {symbol}:")
        for stock in holdings.get("stocks", []):
            if stock:  # Check if stock exists and has data
                print(f"- {stock.get('name', 'Unknown')}: {stock.get('percentage', 0)}%") 