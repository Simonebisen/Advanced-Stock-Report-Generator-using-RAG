import os
from typing import Dict, List, Optional, Any
import pandas as pd
import httpx
from datetime import datetime, timedelta


class AlphaVantageService:
    """Service for retrieving stock data using Alpha Vantage API."""
    
    def __init__(self, api_key: str):
        """
        Initialize the Alpha Vantage service.
        
        Args:
            api_key: Alpha Vantage API key
        """
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
    
    async def get_weekly_data(self, symbol: str, years: int = 5) -> pd.DataFrame:
        """
        Get weekly stock data for the specified symbol.
        
        Args:
            symbol: Stock symbol
            years: Number of years of data to retrieve
            
        Returns:
            DataFrame containing weekly stock data
        """
        # Prepare request parameters
        params = {
            "function": "TIME_SERIES_WEEKLY",
            "symbol": symbol,
            "apikey": self.api_key,
            "datatype": "json"
        }
        
        # Make request to Alpha Vantage
        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract weekly time series
                weekly_data = data.get("Weekly Time Series", {})
                
                # Convert to DataFrame
                df = pd.DataFrame.from_dict(weekly_data, orient="index")
                
                # Sort by date and filter for the last N years
                df.index = pd.to_datetime(df.index)
                df = df.sort_index()
                
                cutoff_date = pd.to_datetime(datetime.now() - timedelta(days=365*years))
                df = df[df.index >= cutoff_date]
                
                return df
            else:
                print(f"Alpha Vantage API error: {response.status_code} - {response.text}")
                return pd.DataFrame()
    
    async def get_company_overview(self, symbol: str) -> Dict[str, Any]:
        """
        Get company overview data.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dict containing company overview data
        """
        # Prepare request parameters
        params = {
            "function": "OVERVIEW",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        # Make request to Alpha Vantage
        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                print(f"Alpha Vantage API error: {response.status_code} - {response.text}")
                return {}
    
    async def get_income_statement(self, symbol: str) -> Dict[str, Any]:
        """
        Get income statement data.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dict containing income statement data
        """
        # Prepare request parameters
        params = {
            "function": "INCOME_STATEMENT",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        # Make request to Alpha Vantage
        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                print(f"Alpha Vantage API error: {response.status_code} - {response.text}")
                return {}
    
    async def get_balance_sheet(self, symbol: str) -> Dict[str, Any]:
        """
        Get balance sheet data.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dict containing balance sheet data
        """
        # Prepare request parameters
        params = {
            "function": "BALANCE_SHEET",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        # Make request to Alpha Vantage
        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                print(f"Alpha Vantage API error: {response.status_code} - {response.text}")
                return {}