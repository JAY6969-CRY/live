"""
Module for retrieving mutual fund data.
"""
import os
import json
import csv
from typing import Dict, List, Optional, Union
import datetime
import requests
import pandas as pd


class MutualFundDataRetriever:
    """Class for retrieving mutual fund data."""
    
    def __init__(self, data_dir: str = "./data/financial/mutual_funds"):
        """
        Initialize mutual fund data retriever.
        
        Args:
            data_dir: Directory to store mutual fund data
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.fund_list = None
        self.holdings_data = {}
    
    def download_fund_list(self, force_update: bool = False) -> List[Dict]:
        """
        Download list of mutual funds (or load from cache).
        
        Args:
            force_update: Whether to force update the list from the source
            
        Returns:
            List of mutual fund dictionaries
        """
        cache_file = os.path.join(self.data_dir, "fund_list.json")
        
        # Return cached data if available and not forcing update
        if not force_update and os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                self.fund_list = json.load(f)
                return self.fund_list
        
        # URL should be provided by the hackathon, but for now we'll use a placeholder
        # In a real implementation, you would use the actual URL provided in the challenge
        url = "https://api.mfapi.in/mf"
        
        try:
            # Download fund list
            response = requests.get(url)
            response.raise_for_status()
            
            # Parse JSON
            funds_raw = response.json()
            
            # Process data
            funds = []
            for fund in funds_raw:
                funds.append({
                    "scheme_code": fund.get("schemeCode", ""),
                    "scheme_name": fund.get("schemeName", ""),
                    "amc": self._extract_amc(fund.get("schemeName", "")),
                    "category": self._extract_category(fund.get("schemeName", ""))
                })
            
            # Save processed data
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(funds, f, ensure_ascii=False, indent=2)
            
            self.fund_list = funds
            return funds
            
        except Exception as e:
            print(f"Error downloading mutual fund list: {e}")
            # Return empty list if download fails
            return []
    
    def get_fund_data(self, scheme_code: str) -> pd.DataFrame:
        """
        Get historical NAV data for a mutual fund.
        
        Args:
            scheme_code: Mutual fund scheme code
            
        Returns:
            DataFrame with NAV data
        """
        # Check if data is cached
        cache_file = os.path.join(self.data_dir, f"nav_{scheme_code}.csv")
        if os.path.exists(cache_file):
            return pd.read_csv(cache_file, parse_dates=["Date"])
        
        # For real implementation, you would use a data source provided by the hackathon
        # This is just a placeholder - in a real scenario, you'd use the actual data source
        try:
            # Example URL (this one is actually real and works for Indian mutual funds)
            url = f"https://api.mfapi.in/mf/{scheme_code}"
            
            response = requests.get(url)
            response.raise_for_status()
            
            # Parse JSON
            data = response.json()
            
            # Extract NAV data
            nav_data = data.get("data", [])
            
            # Convert to dataframe
            df = pd.DataFrame(nav_data)
            
            # Rename columns
            df.rename(columns={"date": "Date", "nav": "NAV"}, inplace=True)
            
            # Convert types
            df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y")
            df["NAV"] = pd.to_numeric(df["NAV"])
            
            # Sort by date
            df.sort_values("Date", inplace=True)
            
            # Save to cache
            df.to_csv(cache_file, index=False)
            
            return df
            
        except Exception as e:
            print(f"Error fetching mutual fund data for {scheme_code}: {e}")
            return pd.DataFrame()  # Return empty dataframe
    
    def get_fund_holdings(self, scheme_code: str) -> Dict:
        """
        Get holdings data for a mutual fund.
        
        Args:
            scheme_code: Mutual fund scheme code
            
        Returns:
            Dictionary with holdings data
        """
        # Check if data is cached in memory
        if scheme_code in self.holdings_data:
            return self.holdings_data[scheme_code]
        
        # Check if data is cached on disk
        cache_file = os.path.join(self.data_dir, f"holdings_{scheme_code}.json")
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                holdings = json.load(f)
                self.holdings_data[scheme_code] = holdings
                return holdings
        
        # For real implementation, you would use a data source provided by the hackathon
        # This is just a placeholder - in a real scenario, you'd use the actual data source
        try:
            # This is a placeholder. In a real implementation, you would need to scrape
            # holdings data from a reliable source, as this information is typically not
            # available through simple APIs for Indian mutual funds
            
            # As a placeholder, we'll just create some dummy data
            holdings = {
                "scheme_code": scheme_code,
                "as_of_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "stocks": [
                    {"name": "HDFC Bank Ltd.", "percentage": 8.2},
                    {"name": "ICICI Bank Ltd.", "percentage": 7.5},
                    {"name": "Reliance Industries Ltd.", "percentage": 7.2},
                    {"name": "Infosys Ltd.", "percentage": 6.8},
                    {"name": "Tata Consultancy Services Ltd.", "percentage": 6.3}
                ],
                "sectors": [
                    {"name": "Financial Services", "percentage": 32.5},
                    {"name": "Information Technology", "percentage": 18.2},
                    {"name": "Oil & Gas", "percentage": 10.8},
                    {"name": "Consumer Goods", "percentage": 8.5},
                    {"name": "Automobile", "percentage": 7.2}
                ],
                "asset_allocation": [
                    {"type": "Equity", "percentage": 95.2},
                    {"type": "Debt", "percentage": 0.0},
                    {"type": "Cash", "percentage": 4.8}
                ]
            }
            
            # Save to cache
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(holdings, f, ensure_ascii=False, indent=2)
            
            self.holdings_data[scheme_code] = holdings
            return holdings
            
        except Exception as e:
            print(f"Error fetching holdings data for {scheme_code}: {e}")
            return {}  # Return empty dict
    
    def search_funds(self, query: str) -> List[Dict]:
        """
        Search for mutual funds by name or AMC.
        
        Args:
            query: Search query
            
        Returns:
            List of matching mutual fund dictionaries
        """
        if not self.fund_list:
            self.download_fund_list()
        
        if not self.fund_list:
            return []
        
        query = query.lower()
        matches = []
        
        for fund in self.fund_list:
            if (query in fund.get("scheme_name", "").lower() or
                query in fund.get("amc", "").lower()):
                matches.append(fund)
        
        return matches
    
    def _extract_amc(self, scheme_name: str) -> str:
        """
        Extract AMC name from scheme name.
        
        Args:
            scheme_name: Mutual fund scheme name
            
        Returns:
            AMC name
        """
        # This is a simple heuristic method. In a real implementation,
        # you would need a more robust approach or a mapping.
        common_amcs = [
            "HDFC", "ICICI", "SBI", "Aditya Birla", "Axis", "Kotak", "Franklin",
            "UTI", "DSP", "IDFC", "Tata", "Nippon", "L&T", "Invesco", "Mirae"
        ]
        
        for amc in common_amcs:
            if amc in scheme_name:
                return amc
        
        return "Unknown"
    
    def _extract_category(self, scheme_name: str) -> str:
        """
        Extract category from scheme name.
        
        Args:
            scheme_name: Mutual fund scheme name
            
        Returns:
            Fund category
        """
        # This is a simple heuristic method. In a real implementation,
        # you would need a more robust approach.
        scheme_name = scheme_name.lower()
        
        categories = {
            "large cap": "Large Cap",
            "mid cap": "Mid Cap",
            "small cap": "Small Cap",
            "multi cap": "Multi Cap",
            "equity": "Equity",
            "debt": "Debt",
            "liquid": "Liquid",
            "hybrid": "Hybrid",
            "balanced": "Balanced",
            "ultra short": "Ultra Short Duration",
            "short duration": "Short Duration", 
            "gilt": "Gilt",
            "index": "Index",
            "etf": "ETF",
            "fund of funds": "Fund of Funds",
            "sector": "Sector",
            "tax saver": "ELSS"
        }
        
        for key, value in categories.items():
            if key in scheme_name:
                return value
        
        return "Other"


if __name__ == "__main__":
    # Example usage
    retriever = MutualFundDataRetriever()
    funds = retriever.download_fund_list()
    print(f"Downloaded {len(funds)} mutual funds")
    
    # Search for a fund
    matches = retriever.search_funds("hdfc")
    for i, match in enumerate(matches[:5]):
        print(f"Found: {match['scheme_code']} - {match['scheme_name']} ({match['amc']})")
    
    # Get NAV data
    if matches:
        scheme_code = matches[0]["scheme_code"]
        data = retriever.get_fund_data(scheme_code)
        print(f"Got {len(data)} days of NAV data for {scheme_code}")
        print(data.head())
        
        # Get holdings
        holdings = retriever.get_fund_holdings(scheme_code)
        print(f"Top holdings for {scheme_code}:")
        for stock in holdings.get("stocks", []):
            print(f"- {stock['name']}: {stock['percentage']}%") 