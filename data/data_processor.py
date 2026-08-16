import os
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Optional, Tuple


def process_stock_data(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Process stock price data to calculate technical indicators.
    
    Args:
        data: DataFrame containing stock price data
        
    Returns:
        Dict containing processed data and calculated indicators
    """
    # Extract OHLC and volume data
    if data.empty:
        return {"error": "No data available"}
    
    # Convert string values to float if needed
    for col in data.columns:
        data[col] = pd.to_numeric(data[col], errors='coerce')
    
    # Rename columns for clarity
    data.columns = [col.split('. ')[1] if '. ' in col else col for col in data.columns]
    
    # Calculate technical indicators
    # 1. Moving Averages
    data['MA50'] = data['close'].rolling(window=50).mean()
    data['MA200'] = data['close'].rolling(window=200).mean()
    
    # 2. RSI (Relative Strength Index)
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    # 3. MACD (Moving Average Convergence Divergence)
    data['EMA12'] = data['close'].ewm(span=12, adjust=False).mean()
    data['EMA26'] = data['close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = data['EMA12'] - data['EMA26']
    data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
    
    # 4. Bollinger Bands
    data['MA20'] = data['close'].rolling(window=20).mean()
    data['StdDev'] = data['close'].rolling(window=20).std()
    data['UpperBand'] = data['MA20'] + (data['StdDev'] * 2)
    data['LowerBand'] = data['MA20'] - (data['StdDev'] * 2)
    
    # Calculate returns
    data['DailyReturn'] = data['close'].pct_change()
    
    # Calculate volatility (standard deviation of returns)
    data['Volatility'] = data['DailyReturn'].rolling(window=21).std() * (252 ** 0.5)
    
    return {
        "processed_data": data,
        "last_price": data['close'].iloc[-1] if not data.empty else None,
        "last_ma50": data['MA50'].iloc[-1] if not data.empty else None,
        "last_ma200": data['MA200'].iloc[-1] if not data.empty else None,
        "last_rsi": data['RSI'].iloc[-1] if not data.empty else None,
        "last_macd": data['MACD'].iloc[-1] if not data.empty else None,
        "last_signal": data['Signal'].iloc[-1] if not data.empty else None,
        "last_upper_band": data['UpperBand'].iloc[-1] if not data.empty else None,
        "last_lower_band": data['LowerBand'].iloc[-1] if not data.empty else None
    }


def create_stock_chart(data: pd.DataFrame, symbol: str) -> Tuple[plt.Figure, plt.Axes]:
    """
    Create a stock chart with price and indicators.
    
    Args:
        data: DataFrame containing processed stock data
        symbol: Stock symbol
        
    Returns:
        Figure and axes objects
    """
    # Create figure and subplots
    fig, axs = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})
    
    # Plot price and moving averages
    axs[0].plot(data.index, data['close'], label='Close Price', color='black', linewidth=1)
    axs[0].plot(data.index, data['MA50'], label='50-day MA', color='blue', linewidth=1)
    axs[0].plot(data.index, data['MA200'], label='200-day MA', color='red', linewidth=1)
    
    # Plot Bollinger Bands
    axs[0].plot(data.index, data['UpperBand'], label='Upper Bollinger Band', color='gray', linestyle='--', linewidth=0.8)
    axs[0].plot(data.index, data['LowerBand'], label='Lower Bollinger Band', color='gray', linestyle='--', linewidth=0.8)
    
    # Plot volume
    axs[1].bar(data.index, data['volume'], label='Volume', color='blue', alpha=0.5)
    
    # Add labels and titles
    axs[0].set_title(f'{symbol} Stock Price and Indicators')
    axs[0].set_ylabel('Price')
    axs[0].legend()
    axs[0].grid(True)
    
    axs[1].set_xlabel('Date')
    axs[1].set_ylabel('Volume')
    axs[1].grid(True)
    
    # Format dates on x-axis
    fig.autofmt_xdate()
    
    # Adjust layout
    plt.tight_layout()
    
    return fig, axs


def process_financial_data(income_statement: Dict[str, Any], balance_sheet: Dict[str, Any], overview: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process financial data for analysis.
    
    Args:
        income_statement: Income statement data
        balance_sheet: Balance sheet data
        overview: Company overview data
        
    Returns:
        Dict containing processed financial data
    """
    processed_data = {
        "company_name": overview.get("Name", ""),
        "company_description": overview.get("Description", ""),
        "industry": overview.get("Industry", ""),
        "sector": overview.get("Sector", ""),
        "market_cap": overview.get("MarketCapitalization", ""),
        "pe_ratio": overview.get("PERatio", ""),
        "eps": overview.get("EPS", ""),
        "dividend_yield": overview.get("DividendYield", ""),
        "beta": overview.get("Beta", ""),
        "52_week_high": overview.get("52WeekHigh", ""),
        "52_week_low": overview.get("52WeekLow", ""),
        "financial_ratios": {}
    }
    
    # Extract annual reports
    if income_statement and "annualReports" in income_statement:
        annual_income = income_statement["annualReports"]
        processed_data["annual_income"] = annual_income
        
        # Calculate growth rates if more than one year available
        if len(annual_income) > 1:
            yearly_revenue = [float(report.get("totalRevenue", 0)) for report in annual_income]
            yearly_net_income = [float(report.get("netIncome", 0)) for report in annual_income]
            
            # Calculate year-over-year growth
            revenue_growth = [(yearly_revenue[i] - yearly_revenue[i+1]) / yearly_revenue[i+1] * 100 
                             for i in range(len(yearly_revenue)-1)]
            
            income_growth = [(yearly_net_income[i] - yearly_net_income[i+1]) / yearly_net_income[i+1] * 100 
                            for i in range(len(yearly_net_income)-1)]
            
            processed_data["revenue_growth"] = revenue_growth
            processed_data["income_growth"] = income_growth
    
    # Extract balance sheet data
    if balance_sheet and "annualReports" in balance_sheet:
        annual_balance = balance_sheet["annualReports"]
        processed_data["annual_balance"] = annual_balance
        
        # Calculate financial ratios from latest report
        if annual_balance and annual_income:
            latest_balance = annual_balance[0]
            latest_income = annual_income[0]
            
            # Convert string values to float
            total_assets = float(latest_balance.get("totalAssets", 0))
            total_equity = float(latest_balance.get("totalShareholderEquity", 0))
            total_liabilities = float(latest_balance.get("totalLiabilities", 0))
            total_revenue = float(latest_income.get("totalRevenue", 0))
            net_income = float(latest_income.get("netIncome", 0))
            
            # Calculate ratios
            if total_equity > 0:
                processed_data["financial_ratios"]["roe"] = (net_income / total_equity) * 100
            
            if total_assets > 0:
                processed_data["financial_ratios"]["roa"] = (net_income / total_assets) * 100
                processed_data["financial_ratios"]["debt_to_assets"] = (total_liabilities / total_assets) * 100
            
            if total_revenue > 0:
                processed_data["financial_ratios"]["profit_margin"] = (net_income / total_revenue) * 100
    
    return processed_data