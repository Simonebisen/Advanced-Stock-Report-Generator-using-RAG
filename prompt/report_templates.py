from typing import Dict, Any


def get_comprehensive_report_prompt(symbol: str) -> str:
    """
    Generate a prompt for a comprehensive research report.
    
    Args:
        symbol: Stock symbol
        
    Returns:
        Prompt text
    """
    return f"""
    Please create a detailed research report for {symbol} stock, including the following four main sections:

    1. Company and Industry Overview
       - Detailed company introduction (history, main products/services, business model)
       - Industry analysis (market size, growth rate, major trends)
       - Company's position in the industry (market share, competitive advantages)
       - Upstream and downstream supply-demand analysis (supply chain relationships, bargaining power)
       
    2. Industry Chain Analysis
       - Recent major orders (amount, customers, timing)
       - Position of orders in the industry chain
       - Current status and future outlook of the industry chain (technology development, policy impact, market trends)
       - Company's role and contribution in the industry chain
       
    3. Earnings Forecast and Investment Recommendations
       - Main business revenue analysis (by product/service category, geography)
       - 3-5 year revenue forecast (based on industry growth, market share changes, new products)
       - Profit margin and EPS forecast
       - Valuation analysis (PE, PB, DCF, and other methods)
       - Clear investment recommendation (buy/hold/sell) and target price
       
    4. Risk Assessment
       - Industry competition risk
       - Technology iteration risk
       - Policy and regulatory risk
       - Macroeconomic risk
       - Other specific risk factors
    
    The report should be based on SEC filings, news, market data, etc. and provide substantive data support. Each section should include detailed data analysis and charts.
    """


def get_executive_summary_prompt(symbol: str, company_data: Dict[str, Any]) -> str:
    """
    Generate a prompt for creating an executive summary.
    
    Args:
        symbol: Stock symbol
        company_data: Company data dictionary
        
    Returns:
        Prompt text
    """
    return f"""
    Create a concise and informative executive summary for {symbol} ({company_data.get('company_name', '')}).
    This should include:
    
    1. Brief company overview
    2. Key investment highlights
    3. Recent financial performance
    4. Major risks and challenges
    5. Overall investment thesis
    
    This executive summary will appear at the beginning of a detailed research report.
    """


def get_financial_analysis_prompt(symbol: str, financials: Dict[str, Any]) -> str:
    """
    Generate a prompt for financial analysis.
    
    Args:
        symbol: Stock symbol
        financials: Financial data dictionary
        
    Returns:
        Prompt text
    """
    return f"""
    Provide a comprehensive financial analysis for {symbol} based on the following data:
    
    Income Statement:
    {financials.get('annual_income', [])}
    
    Balance Sheet:
    {financials.get('annual_balance', [])}
    
    Key Financial Ratios:
    {financials.get('financial_ratios', {})}
    
    The analysis should include:
    1. Revenue and earnings trends
    2. Profitability analysis
    3. Balance sheet strength
    4. Cash flow analysis
    5. Key financial ratios compared to industry benchmarks
    6. Areas of financial concern or strength
    """


def get_technical_analysis_prompt(symbol: str, indicators: Dict[str, Any]) -> str:
    """
    Generate a prompt for technical analysis.
    
    Args:
        symbol: Stock symbol
        indicators: Technical indicators dictionary
        
    Returns:
        Prompt text
    """
    return f"""
    Based on the following technical indicators for {symbol}, provide a comprehensive technical analysis:
    
    Current Price: {indicators.get('last_price')}
    50-day Moving Average: {indicators.get('last_ma50')}
    200-day Moving Average: {indicators.get('last_ma200')}
    RSI (14): {indicators.get('last_rsi')}
    MACD: {indicators.get('last_macd')}
    MACD Signal Line: {indicators.get('last_signal')}
    Upper Bollinger Band: {indicators.get('last_upper_band')}
    Lower Bollinger Band: {indicators.get('last_lower_band')}
    
    The analysis should include:
    1. Current trend identification
    2. Support and resistance levels
    3. Technical signals and patterns
    4. Volume analysis
    5. Momentum indicators interpretation
    6. Technical outlook (short, medium, and long term)
    """


def get_conclusion_prompt(symbol: str, data: Dict[str, Any]) -> str:
    """
    Generate a prompt for the report conclusion.
    
    Args:
        symbol: Stock symbol
        data: Combined data dictionary
        
    Returns:
        Prompt text
    """
    return f"""
    Based on the comprehensive analysis of {symbol}, provide a strong concluding section that includes:
    
    1. Investment recommendation (Buy/Hold/Sell)
    2. Price target with rationale
    3. Key catalysts to watch
    4. Timeline considerations
    5. Risk factors that could change the thesis
    6. Final investment summary in 2-3 sentences
    
    This conclusion should synthesize the fundamental analysis, technical indicators, and market sentiment to provide a clear investment direction.
    """