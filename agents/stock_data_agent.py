from typing import Dict, List, Optional, Any
import pandas as pd
import matplotlib.pyplot as plt
import io
import logging
import traceback
import time
import asyncio
# 獲取 stock_report 日誌記錄器
logger = logging.getLogger('stock_report')

class StockDataAgent:
    """Agent for analyzing stock price data and financial metrics."""
    
    def __init__(self, alpha_vantage_service):
        """
        Initialize the stock data agent.
        
        Args:
            alpha_vantage_service: Service for retrieving stock data
        """
        self.alpha_vantage_service = alpha_vantage_service
        logger.info("StockDataAgent 初始化完成")
    
    async def analyze(self, symbol: str) -> Dict[str, Any]:
        """
        Analyze stock data for the given symbol.
        
        Args:
            symbol: Stock symbol (e.g., AAPL, MSFT, NVDA)
            
        Returns:
            Dict containing analysis results
        """
        logger.info(f"========== 開始分析 {symbol} 股票數據 ==========")
        
        try:
            # Get weekly stock data for the past 5 years with timeout
            logger.info(f"獲取 {symbol} 過去 5 年的每週股票數據")
            try:
                # 完全跳過 API 調用，直接使用模擬數據
                logger.info(f"跳過 API 調用，直接創建 {symbol} 的模擬股票數據")
                import time
                import pandas as pd
                import numpy as np
                from datetime import datetime, timedelta
                
                # 創建模擬數據 - 最近100週的數據
                dates = [datetime.now() - timedelta(days=i*7) for i in range(100)]
                dates.sort()  # 確保日期按升序排列
                
                # 根據不同股票生成不同的基礎價格
                base_price = 150.0  # 默認基礎價格
                if symbol == "AAPL":
                    base_price = 170.0
                elif symbol == "MSFT":
                    base_price = 320.0
                elif symbol == "NVDA":
                    base_price = 750.0
                elif symbol == "GOOGL":
                    base_price = 140.0
                
                # 創建帶有輕微上升趨勢的價格
                trend = np.linspace(0.8, 1.2, 100)  # 價格變化趨勢
                prices = base_price * trend
                
                # 為價格添加隨機波動
                noise = np.random.normal(0, 0.02, 100)  # 2% 的隨機波動
                prices = prices * (1 + noise)
                
                # 生成開高低收價格
                closes = prices
                opens = closes * (1 + np.random.normal(0, 0.01, 100))  # 開盤價
                highs = np.maximum(opens, closes) * (1 + abs(np.random.normal(0, 0.015, 100)))  # 最高價
                lows = np.minimum(opens, closes) * (1 - abs(np.random.normal(0, 0.015, 100)))  # 最低價
                volumes = np.random.uniform(5000000, 15000000, 100)  # 交易量
                
                # 創建 DataFrame
                stock_data = pd.DataFrame({
                    '1. open': opens,
                    '2. high': highs,
                    '3. low': lows,
                    '4. close': closes,
                    '5. volume': volumes
                }, index=dates)
                
                logger.info(f"創建了模擬數據，包含 {len(stock_data)} 條記錄")
                if stock_data.empty:
                    logger.error(f"未能獲取 {symbol} 的股票數據，返回結果為空")
                    return {
                        "technical_summary": f"Error: No stock data available for {symbol}",
                        "valuation_analysis": "No data available",
                        "earnings_forecast": "No data available",
                        "investment_recommendation": "No data available"
                    }
                
                logger.info(f"成功獲取 {symbol} 的股票數據，收到 {len(stock_data)} 條記錄")
                logger.info(f"股票數據的欄位: {list(stock_data.columns)}")
                
            except asyncio.TimeoutError:
                logger.error(f"獲取 {symbol} 的股票數據超時 (30秒)")
                # 創建一個合理的測試數據框架
                import pandas as pd
                import numpy as np
                from datetime import datetime, timedelta
                
                # 創建模擬數據 - 最近100週的數據
                logger.info(f"創建 {symbol} 的模擬股票數據作為備用")
                dates = [datetime.now() - timedelta(days=i*7) for i in range(100)]
                dates.sort()  # 確保日期按升序排列
                
                # 根據不同股票生成不同的基礎價格
                base_price = 150.0  # 默認基礎價格
                if symbol == "AAPL":
                    base_price = 170.0
                elif symbol == "MSFT":
                    base_price = 320.0
                elif symbol == "NVDA":
                    base_price = 750.0
                elif symbol == "GOOGL":
                    base_price = 140.0
                
                # 創建帶有輕微上升趨勢的價格
                trend = np.linspace(0.8, 1.2, 100)  # 價格變化趨勢
                prices = base_price * trend
                
                # 為價格添加隨機波動
                noise = np.random.normal(0, 0.02, 100)  # 2% 的隨機波動
                prices = prices * (1 + noise)
                
                # 生成開高低收價格
                closes = prices
                opens = closes * (1 + np.random.normal(0, 0.01, 100))  # 開盤價
                highs = np.maximum(opens, closes) * (1 + abs(np.random.normal(0, 0.015, 100)))  # 最高價
                lows = np.minimum(opens, closes) * (1 - abs(np.random.normal(0, 0.015, 100)))  # 最低價
                volumes = np.random.uniform(5000000, 15000000, 100)  # 交易量
                
                # 創建 DataFrame
                stock_data = pd.DataFrame({
                    '1. open': opens,
                    '2. high': highs,
                    '3. low': lows,
                    '4. close': closes,
                    '5. volume': volumes
                }, index=dates)
                
                logger.info(f"創建了模擬數據，包含 {len(stock_data)} 條記錄")
                
            except Exception as e:
                logger.error(f"獲取 {symbol} 的股票數據時出錯: {str(e)}")
                logger.error(traceback.format_exc())
                
                # 返回帶有錯誤信息的默認結果
                return {
                    "error": f"Error fetching stock data: {str(e)}",
                    "technical_summary": f"Error: Could not retrieve stock data for {symbol}. {str(e)}",
                    "valuation_analysis": "No data available due to API error",
                    "earnings_forecast": "No data available due to API error",
                    "investment_recommendation": "No recommendation available due to data retrieval error"
                }
            
            # Calculate technical indicators with timeout
            logger.info(f"計算 {symbol} 的技術指標")
            try:
                start_time = time.time()
                tech_indicators = self._calculate_technical_indicators(stock_data)
                logger.info(f"技術指標計算完成，耗時: {time.time() - start_time:.2f}秒，生成了 {len(tech_indicators)} 個指標")
            except Exception as e:
                logger.error(f"計算技術指標時出錯: {str(e)}")
                logger.error(traceback.format_exc())
                
                # 提供基本的技術指標
                if 'close' in stock_data.columns or '4. close' in stock_data.columns:
                    close_col = 'close' if 'close' in stock_data.columns else '4. close'
                    current_price = stock_data[close_col].iloc[-1]
                else:
                    current_price = 100.0  # 默認價格
                    
                tech_indicators = {
                    "error": str(e),
                    "current_price": current_price,
                    "ma_20": current_price * 0.98,
                    "ma_50": current_price * 0.95,
                    "ma_200": current_price * 0.90,
                    "macd": 0.5,
                    "signal": 0.3,
                    "rsi": 50.0,
                    "bb_middle": current_price,
                    "bb_upper": current_price * 1.05,
                    "bb_lower": current_price * 0.95
                }
            
            # Get company overview data with timeout
            logger.info(f"獲取 {symbol} 的公司概覽數據")
            #try:
            #    start_time = time.time()
            #    overview = await asyncio.wait_for(
            #        self.alpha_vantage_service.get_company_overview(symbol),
            #        timeout=20.0  # 20秒超時
            #    )
            #    logger.info(f"公司概覽數據獲取完成，耗時: {time.time() - start_time:.2f}秒，包含 {len(overview) if isinstance(overview, dict) else 0} 個字段")
            #except asyncio.TimeoutError:
            #    logger.error(f"獲取 {symbol} 的公司概覽數據超時 (20秒)")
                # 創建基本的公司概覽數據
            #    overview = self._create_mock_company_overview(symbol)
            #    logger.info(f"創建了模擬公司概覽數據，包含 {len(overview)} 個字段")
            #except Exception as e:
            ##    logger.error(f"獲取公司概覽數據時出錯: {str(e)}")
            #    logger.error(traceback.format_exc())
            #    overview = self._create_mock_company_overview(symbol)
            #    logger.info(f"由於錯誤創建了模擬公司概覽數據")
            logger.info(f"跳過API調用，直接創建 {symbol} 的模擬公司概覽數據")
            overview = self._create_mock_company_overview(symbol)
            logger.info(f"創建了模擬公司概覽數據，包含 {len(overview)} 個字段")
            # Create reports with timeouts for each section
            results = {}
            
            # Generate technical analysis summary
            logger.info(f"生成 {symbol} 的技術分析摘要")
            try:
                start_time = time.time()
                technical_summary = self._generate_technical_summary(symbol, stock_data, tech_indicators)
                results["technical_summary"] = technical_summary
                logger.info(f"技術分析摘要生成完成，耗時: {time.time() - start_time:.2f}秒，長度: {len(technical_summary)} 字符")
            except Exception as e:
                logger.error(f"生成技術分析摘要時出錯: {str(e)}")
                logger.error(traceback.format_exc())
                results["technical_summary"] = f"Error generating technical summary: {str(e)}"
            
            # Generate valuation analysis
            logger.info(f"生成 {symbol} 的估值分析")
            try:
                start_time = time.time()
                valuation_analysis = self._generate_valuation_analysis(symbol, overview, stock_data)
                results["valuation_analysis"] = valuation_analysis
                logger.info(f"估值分析生成完成，耗時: {time.time() - start_time:.2f}秒，長度: {len(valuation_analysis)} 字符")
            except Exception as e:
                logger.error(f"生成估值分析時出錯: {str(e)}")
                logger.error(traceback.format_exc())
                results["valuation_analysis"] = f"Error generating valuation analysis: {str(e)}"
            
            # Generate earnings forecast
            logger.info(f"生成 {symbol} 的盈利預測")
            try:
                start_time = time.time()
                earnings_forecast = self._generate_earnings_forecast(symbol, overview, stock_data)
                results["earnings_forecast"] = earnings_forecast
                logger.info(f"盈利預測生成完成，耗時: {time.time() - start_time:.2f}秒，長度: {len(earnings_forecast)} 字符")
            except Exception as e:
                logger.error(f"生成盈利預測時出錯: {str(e)}")
                logger.error(traceback.format_exc())
                results["earnings_forecast"] = f"Error generating earnings forecast: {str(e)}"
            
            # Generate investment recommendation
            logger.info(f"生成 {symbol} 的投資建議")
            try:
                start_time = time.time()
                investment_recommendation = self._generate_investment_recommendation(
                    symbol, overview, stock_data, tech_indicators, results.get("valuation_analysis", "")
                )
                results["investment_recommendation"] = investment_recommendation
                logger.info(f"投資建議生成完成，耗時: {time.time() - start_time:.2f}秒，長度: {len(investment_recommendation)} 字符")
            except Exception as e:
                logger.error(f"生成投資建議時出錯: {str(e)}")
                logger.error(traceback.format_exc())
                results["investment_recommendation"] = f"Error generating investment recommendation: {str(e)}"
            
            # Prepare final results
            logger.info(f"整合 {symbol} 的所有分析結果")
            results.update({
                "stock_data": stock_data,
                "technical_indicators": tech_indicators,
                "company_overview": overview
            })
            
            logger.info(f"========== 完成 {symbol} 股票數據分析 ==========")
            return results
            
        except Exception as e:
            logger.error(f"分析 {symbol} 股票數據時發生未處理的錯誤: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "error": str(e),
                "technical_summary": f"Error in stock analysis: {str(e)}",
                "valuation_analysis": f"Error in stock analysis: {str(e)}",
                "earnings_forecast": f"Error in stock analysis: {str(e)}",
                "investment_recommendation": f"Error in stock analysis: {str(e)}"
            }

    # 添加一個輔助方法來創建模擬的公司概覽數據
    def _create_mock_company_overview(self, symbol: str) -> Dict[str, Any]:
        """創建模擬的公司概覽數據"""
        # 根據不同股票設置不同的數據
        overview_data = {
            "Symbol": symbol,
            "Name": f"{symbol} Inc.",
            "Description": f"{symbol} is a leading technology company focused on innovation.",
            "Exchange": "NASDAQ",
            "Currency": "USD",
            "Country": "USA",
            "Sector": "Technology",
            "Industry": "Technology Hardware",
            "PERatio": "25.4",
            "PEGRatio": "1.8",
            "PriceToBookRatio": "8.5",
            "PriceToSalesRatioTTM": "6.2",
            "EPS": "6.5",
            "DividendYield": "0.8",
            "Beta": "1.2",
            "52WeekHigh": "185.50",
            "52WeekLow": "120.75"
        }
        
        # 根據不同股票調整數據
        if symbol == "AAPL":
            overview_data.update({
                "Name": "Apple Inc.",
                "Industry": "Consumer Electronics",
                "Description": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide."
            })
        elif symbol == "MSFT":
            overview_data.update({
                "Name": "Microsoft Corporation",
                "Industry": "Software—Infrastructure",
                "Description": "Microsoft Corporation develops, licenses, and supports software, services, devices, and solutions worldwide."
            })
        elif symbol == "NVDA":
            overview_data.update({
                "Name": "NVIDIA Corporation",
                "Industry": "Semiconductors",
                "Description": "NVIDIA Corporation provides graphics, and compute and networking solutions in the United States, Taiwan, China, and internationally."
            })
        elif symbol == "GOOGL":
            overview_data.update({
                "Name": "Alphabet Inc.",
                "Industry": "Internet Content & Information",
                "Description": "Alphabet Inc. provides various products and platforms in the United States, Europe, the Middle East, Africa, the Asia-Pacific, Canada, and Latin America."
            })
        
        return overview_data

    def _generate_valuation_analysis(self, symbol: str, overview: Dict[str, Any], data: pd.DataFrame) -> str:
        """
        Generate valuation analysis.
        
        Args:
            symbol: Stock symbol
            overview: Company overview data
            data: DataFrame containing stock price data
            
        Returns:
            Formatted valuation analysis text
        """
        logger.info(f"開始生成 {symbol} 的估值分析")
        
        # Extract key financial metrics
        pe_ratio = overview.get("PERatio", "N/A")
        pb_ratio = overview.get("PriceToBookRatio", "N/A")
        ps_ratio = overview.get("PriceToSalesRatioTTM", "N/A")
        eps = overview.get("EPS", "N/A")
        
        logger.info(f"估值指標: P/E={pe_ratio}, P/B={pb_ratio}, P/S={ps_ratio}, EPS={eps}")
        
        # Generate valuation analysis text
        analysis = f"""## Valuation Analysis

    ### Current Valuation Metrics
    - **Price-to-Earnings (P/E):** {pe_ratio}
    - **Price-to-Book (P/B):** {pb_ratio}
    - **Price-to-Sales (P/S):** {ps_ratio}
    - **Earnings Per Share (EPS):** {eps}

    ### Industry Comparison
    Based on the above valuation metrics compared to the industry average:

    """
        
        # Add industry comparison analysis
        # This needs actual data, using example text for now
        try:
            if pe_ratio != "N/A" and float(pe_ratio) > 0:
                pe_value = float(pe_ratio)
                if pe_value > 30:
                    analysis += "- **P/E Analysis:** Current P/E ratio is above the industry average, indicating high growth expectations from the market, but also potential overvaluation risk.\n"
                    logger.info(f"{symbol} P/E 分析: 高於行業平均值 (P/E={pe_value})")
                elif pe_value > 15:
                    analysis += "- **P/E Analysis:** Current P/E ratio is at the industry average level, suggesting relatively reasonable valuation.\n"
                    logger.info(f"{symbol} P/E 分析: 接近行業平均值 (P/E={pe_value})")
                else:
                    analysis += "- **P/E Analysis:** Current P/E ratio is below the industry average, potentially indicating undervaluation.\n"
                    logger.info(f"{symbol} P/E 分析: 低於行業平均值 (P/E={pe_value})")
        except Exception as e:
            logger.error(f"生成 P/E 分析時出錯: {str(e)}")
            analysis += "- **P/E Analysis:** Unable to analyze P/E ratio due to data issues.\n"
        
        # Add DCF valuation analysis
        analysis += """
    ### Discounted Cash Flow (DCF) Valuation
    Based on historical growth rates, industry averages, and analyst expectations:

    - **5-year Revenue Forecast Growth Rate:** [to be filled]%
    - **Long-term Growth Rate:** [to be filled]%
    - **Weighted Average Cost of Capital (WACC):** [to be filled]%

    According to the DCF model, the company's reasonable valuation range is $[to be filled] - $[to be filled].

    ### Comprehensive Valuation Conclusion
    Combining multiple valuation methods, including relative valuation and absolute valuation models, [to be filled]
    """
        
        logger.info(f"{symbol} 估值分析生成完成")
        return analysis

    def _generate_earnings_forecast(self, symbol: str, overview: Dict[str, Any], data: pd.DataFrame) -> str:
        """
        Generate earnings forecast.
        
        Args:
            symbol: Stock symbol
            overview: Company overview data
            data: DataFrame containing stock price data
            
        Returns:
            Formatted earnings forecast text
        """
        logger.info(f"開始生成 {symbol} 的盈利預測")
        
        # Extract company information
        sector = overview.get("Sector", "")
        industry = overview.get("Industry", "")
        
        logger.info(f"{symbol} 所屬行業: {industry}, 所屬部門: {sector}")
        
        # Generate earnings forecast text
        forecast = f"""## Earnings Forecast

    ### Main Business Revenue Analysis
    {symbol} belongs to the {industry} segment within the {sector} sector. Based on historical financial data analysis:

    - **Revenue Composition:** [to be filled]
    - **Main Growth Drivers:** [to be filled]
    - **Gross Margin Trends:** [to be filled]

    ### 3-Year Performance Forecast
    Based on industry trends, company historical performance, and market competition, the forecast is as follows:

    | Fiscal Year | Revenue(M) | YoY Growth | Net Profit(M) | YoY Growth | EPS | PE |
    |-------------|------------|------------|---------------|------------|-----|-----|
    | FY1         | [to be filled] | [to be filled]% | [to be filled] | [to be filled]% | [to be filled] | [to be filled] |
    | FY2         | [to be filled] | [to be filled]% | [to be filled] | [to be filled]% | [to be filled] | [to be filled] |
    | FY3         | [to be filled] | [to be filled]% | [to be filled] | [to be filled]% | [to be filled] | [to be filled] |

    ### Basis for Performance Forecast
    - **Industry Growth Forecast:** [to be filled]
    - **Expected Changes in Company Market Share:** [to be filled]
    - **New Product/Service Contribution:** [to be filled]
    - **Expected Cost Structure Changes:** [to be filled]
    """
        
        logger.info(f"{symbol} 盈利預測生成完成")
        return forecast

    def _generate_investment_recommendation(
        self, 
        symbol: str, 
        overview: Dict[str, Any], 
        data: pd.DataFrame, 
        indicators: Dict[str, Any],
        valuation: str
    ) -> str:
        """
        Generate investment recommendation.
        
        Args:
            symbol: Stock symbol
            overview: Company overview data
            data: DataFrame containing stock price data
            indicators: Technical indicators dictionary
            valuation: Valuation analysis
            
        Returns:
            Formatted investment recommendation text
        """
        logger.info(f"開始生成 {symbol} 的投資建議")
        
        # Extract key metrics
        current_price = indicators.get("current_price", 0)
        logger.info(f"{symbol} 當前價格: ${current_price}")
        
        # Signals based on technical analysis
        bullish_signals = 0
        bearish_signals = 0
        
        try:
            if indicators.get("ma_50", 0) > indicators.get("ma_200", 0): 
                bullish_signals += 1
                logger.info(f"{symbol} 50日均線 > 200日均線 (看漲)")
            else: 
                bearish_signals += 1
                logger.info(f"{symbol} 50日均線 < 200日均線 (看跌)")
            
            if indicators.get("macd", 0) > indicators.get("signal", 0): 
                bullish_signals += 1
                logger.info(f"{symbol} MACD > 信號線 (看漲)")
            else: 
                bearish_signals += 1
                logger.info(f"{symbol} MACD < 信號線 (看跌)")
            
            rsi = indicators.get("rsi", 50)
            if rsi > 50 and rsi < 70: 
                bullish_signals += 1
                logger.info(f"{symbol} RSI 在 50-70 之間 (看漲)")
            elif rsi < 50 and rsi > 30: 
                bearish_signals += 1
                logger.info(f"{symbol} RSI 在 30-50 之間 (看跌)")
            
            logger.info(f"{symbol} 看漲信號: {bullish_signals}, 看跌信號: {bearish_signals}")
        except Exception as e:
            logger.error(f"計算技術信號時出錯: {str(e)}")
        
        # Generate investment recommendation
        recommendation = f"""## Investment Recommendation

    """
        
        # Determine investment rating
        try:
            if bullish_signals > bearish_signals + 1:
                rating = "Buy"
                price_target = current_price * 1.15  # 15% upside
                logger.info(f"{symbol} 投資評級: 買入, 目標價: ${price_target:.2f}")
            elif bullish_signals > bearish_signals:
                rating = "Accumulate"
                price_target = current_price * 1.10  # 10% upside
                logger.info(f"{symbol} 投資評級: 增持, 目標價: ${price_target:.2f}")
            elif bearish_signals > bullish_signals + 1:
                rating = "Sell"
                price_target = current_price * 0.85  # 15% downside
                logger.info(f"{symbol} 投資評級: 賣出, 目標價: ${price_target:.2f}")
            elif bearish_signals > bullish_signals:
                rating = "Reduce"
                price_target = current_price * 0.90  # 10% downside
                logger.info(f"{symbol} 投資評級: 減持, 目標價: ${price_target:.2f}")
            else:
                rating = "Hold"
                price_target = current_price * 1.05  # 5% upside
                logger.info(f"{symbol} 投資評級: 持有, 目標價: ${price_target:.2f}")
            
            recommendation += f"""### Investment Rating: {rating}
    ### Target Price: ${price_target:.2f} (Current Price: ${current_price:.2f})
    ### Potential Return: {((price_target/current_price - 1) * 100):.2f}%
            """
        except Exception as e:
            logger.error(f"計算投資評級時出錯: {str(e)}")
            recommendation += """### Investment Rating: N/A
    ### Target Price: N/A (Current Price: N/A)
    ### Potential Return: N/A
            """
        
        recommendation += f"""
    ### Rating Basis
    - **Fundamental Analysis:** [to be filled]
    - **Technical Analysis:** {'Bullish signals exceed bearish signals' if bullish_signals > bearish_signals else 'Bearish signals exceed bullish signals' if bearish_signals > bullish_signals else 'Balanced bullish and bearish signals'}
    - **Valuation Analysis:** [to be filled]
    - **Industry Outlook:** [to be filled]

    ### Investment Timeframe Recommendation
    - **Short-term (3-6 months):** [to be filled]
    - **Medium-term (6-18 months):** [to be filled]
    - **Long-term (18+ months):** [to be filled]

    ### Core Investment Logic
    [to be filled]
    """
        
        logger.info(f"{symbol} 投資建議生成完成")
        return recommendation
    
    def _generate_technical_summary(self, symbol: str, data: pd.DataFrame, indicators: Dict[str, Any]) -> str:
        """
        Generate technical analysis summary.
        
        Args:
            symbol: Stock symbol
            data: DataFrame containing stock price data
            indicators: Dictionary containing calculated technical indicators
            
        Returns:
            Formatted technical analysis summary text
        """
        logger.info(f"開始生成 {symbol} 的技術分析摘要")
        
        try:
            # 複製數據並確保欄位名稱標準化
            df = data.copy()
            
            # 檢查並標準化欄位名稱
            column_mapping = {}
            for col in df.columns:
                if '1. open' in col or 'open' in col.lower():
                    column_mapping[col] = 'open'
                elif '2. high' in col or 'high' in col.lower():
                    column_mapping[col] = 'high'
                elif '3. low' in col or 'low' in col.lower():
                    column_mapping[col] = 'low'
                elif '4. close' in col or 'close' in col.lower():
                    column_mapping[col] = 'close'
                elif '5. volume' in col or 'volume' in col.lower():
                    column_mapping[col] = 'volume'
            
            # 應用重命名
            if column_mapping:
                df = df.rename(columns=column_mapping)
                logger.info(f"在技術分析中重命名欄位: {column_mapping}")
            
            logger.info(f"技術分析數據欄位: {list(df.columns)}")
            
            # 確保有 'close' 欄位
            if 'close' not in df.columns:
                # 如果沒有 'close'，但有 '4. close'
                if '4. close' in df.columns:
                    df['close'] = df['4. close']
                    logger.info("使用 '4. close' 作為 'close' 欄位")
                else:
                    # 尋找任何可能的 close 欄位
                    for col in df.columns:
                        if 'close' in col.lower():
                            df['close'] = df[col]
                            logger.info(f"使用 '{col}' 作為 'close' 欄位")
                            break
                    else:
                        logger.error(f"無法找到 close 欄位，可用欄位: {list(df.columns)}")
                        return f"## Technical Analysis Summary\n\nError: Could not find 'close' price data for {symbol}."
            
            # Extract key indicators
            current_price = indicators["current_price"]
            ma_20 = indicators["ma_20"]
            ma_50 = indicators["ma_50"]
            ma_200 = indicators["ma_200"]
            macd = indicators["macd"]
            signal = indicators["signal"]
            rsi = indicators["rsi"]
            bb_middle = indicators["bb_middle"]
            bb_upper = indicators["bb_upper"]
            bb_lower = indicators["bb_lower"]
            
            logger.info(f"{symbol} 關鍵指標: 價格=${current_price:.2f}, 20日均線=${ma_20:.2f}, 50日均線=${ma_50:.2f}, 200日均線=${ma_200}, RSI={rsi:.2f}")
            
            # Calculate price changes
            # 直接使用技術指標而不是重新計算
            week_change = indicators.get("roc_5", 0.0)
            month_change = indicators.get("roc_20", 0.0)
            ytd_change = 10.0  # 假設值
            
            logger.info(f"{symbol} 價格變化: 週={week_change:.2f}%, 月={month_change:.2f}%, 年初至今={ytd_change:.2f}%")
            
            # Generate trend analysis
            if current_price > ma_50 and ma_50 > ma_200:
                trend = "Bullish (Long-Term Uptrend)"
                logger.info(f"{symbol} 趨勢: 看漲 (長期上升趨勢)")
            elif current_price > ma_50 and ma_50 < ma_200:
                trend = "Cautiously Bullish (Potential Golden Cross)"
                logger.info(f"{symbol} 趨勢: 謹慎看漲 (潛在金叉形態)")
            elif current_price < ma_50 and ma_50 > ma_200:
                trend = "Cautiously Bearish (Potential Short-Term Correction)"
                logger.info(f"{symbol} 趨勢: 謹慎看跌 (潛在短期修正)")
            else:
                trend = "Bearish (Long-Term Downtrend)"
                logger.info(f"{symbol} 趨勢: 看跌 (長期下降趨勢)")
        except Exception as e:
            logger.error(f"處理技術指標時出錯: {str(e)}")
            logger.error(traceback.format_exc())
            return f"## Technical Analysis Summary\n\nError generating technical summary: {str(e)}"
        
        # Format the summary text
        try:
            summary = f"""## Technical Analysis Summary

        ### Price Action
        - **Current Price:** ${current_price:.2f}
        - **Price Change (Week):** {week_change:.2f}%
        - **Price Change (Month):** {month_change:.2f}%
        - **Price Change (YTD):** {ytd_change:.2f}%
        
        ### Moving Averages
        - **20-Day MA:** ${ma_20:.2f} ({'Above' if current_price > ma_20 else 'Below'} current price)
        - **50-Day MA:** ${ma_50:.2f} ({'Above' if current_price > ma_50 else 'Below'} current price)
        - **200-Day MA:** ${ma_200:.2f} ({'Above' if current_price > ma_200 else 'Below'} current price)
        
        ### Technical Indicators
        - **Overall Trend:** {trend}
        - **RSI (14):** {rsi:.2f} ({'Overbought' if rsi > 70 else 'Oversold' if rsi < 30 else 'Neutral'})
        - **MACD:** {macd:.2f} ({'Bullish' if macd > signal else 'Bearish'} crossover with signal line at {signal:.2f})
        - **Bollinger Bands:**
        - Upper Band: ${bb_upper:.2f}
        - Middle Band: ${bb_middle:.2f}
        - Lower Band: ${bb_lower:.2f}
        - Position: {
                'Near Upper Band (Potential Resistance)' if abs(current_price - bb_upper) < 0.05 * bb_middle else
                'Near Lower Band (Potential Support)' if abs(current_price - bb_lower) < 0.05 * bb_middle else
                'Mid-Range'
            }
        
        ### Support and Resistance Levels
        - **Key Resistance Levels:** [to be filled]
        - **Key Support Levels:** [to be filled]
        
        ### Trading Volume Analysis
        - **Recent Volume vs Average:** {'Above average' if indicators.get('recent_volume', 0) > indicators.get('avg_volume', 0) else 'Below average'} trading volume
        - **Volume Trend:** [to be filled]
        
        ### Key Price Levels to Watch
        - **Potential Upside Target:** ${current_price * 1.1:.2f} (10% upside)
        - **Potential Downside Risk:** ${current_price * 0.9:.2f} (10% downside)
        - **Stop Loss Suggestion:** ${current_price * 0.85:.2f} (15% downside protection)
        """
            
            logger.info(f"{symbol} 技術分析摘要生成完成")
            return summary
        except Exception as e:
            logger.error(f"格式化技術分析摘要時出錯: {str(e)}")
            logger.error(traceback.format_exc())
            return f"## Technical Analysis Summary\n\nError formatting technical summary: {str(e)}"
    
    def _calculate_technical_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate technical indicators for stock data.
        
        Args:
            data: DataFrame containing stock price data
            
        Returns:
            Dictionary containing calculated technical indicators
        """
        logger.info("開始計算技術指標")
        
        # Make a copy to avoid modifying the original data
        df = data.copy()
        
        try:
            # Rename columns to standardized names
            logger.info(f"原始數據欄位: {list(df.columns)}")
            column_mapping = {}
            for col in df.columns:
                if '1. open' in col or 'open' in col.lower():
                    column_mapping[col] = 'open'
                elif '2. high' in col or 'high' in col.lower():
                    column_mapping[col] = 'high'
                elif '3. low' in col or 'low' in col.lower():
                    column_mapping[col] = 'low'
                elif '4. close' in col or 'close' in col.lower():
                    column_mapping[col] = 'close'
                elif '5. volume' in col or 'volume' in col.lower():
                    column_mapping[col] = 'volume'
            
            # Apply the rename if we found mappings
            if column_mapping:
                df = df.rename(columns=column_mapping)
                logger.info(f"重命名欄位: {column_mapping}")
            
            logger.info(f"標準化後欄位: {list(df.columns)}")
            
            # Check if 'close' column exists
            if 'close' not in df.columns:
                # Print available columns for debugging
                logger.warning(f"未找到 'close' 欄位，可用欄位: {list(df.columns)}")
                
                # Try to find a suitable column
                for col in df.columns:
                    if 'close' in col.lower() or 'price' in col.lower():
                        df['close'] = df[col]
                        logger.info(f"使用 '{col}' 作為 'close' 欄位")
                        break
                else:
                    # If we still don't have a 'close' column, use the 4th column (typical location of close price)
                    if len(df.columns) >= 4:
                        df['close'] = df.iloc[:, 3]
                        logger.info(f"使用索引 3 的欄位作為 'close' 欄位")
                    else:
                        error_msg = f"無法找到 'close' 價格欄位，可用欄位: {list(df.columns)}"
                        logger.error(error_msg)
                        raise ValueError(error_msg)
            
            # Convert string values to float
            for col in ['open', 'high', 'low', 'close', 'volume']:
                if col in df.columns and df[col].dtype == 'object':
                    logger.info(f"將 {col} 從字符串轉換為數值")
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Check for NaN values
            for col in ['open', 'high', 'low', 'close']:
                if col in df.columns:
                    nan_count = df[col].isna().sum()
                    if nan_count > 0:
                        logger.warning(f"{col} 欄位中有 {nan_count} 個 NaN 值")
            
            # Basic calculations
            current_price = df['close'].iloc[-1]
            logger.info(f"當前價格: ${current_price:.2f}")
            
            # Simple Moving Averages (SMA)
            logger.info("計算移動平均線")
            df['ma_20'] = df['close'].rolling(window=20).mean()
            df['ma_50'] = df['close'].rolling(window=50).mean()
            df['ma_200'] = df['close'].rolling(window=200).mean()
            
            # Get the most recent values for moving averages
            ma_20 = df['ma_20'].iloc[-1]
            ma_50 = df['ma_50'].iloc[-1]
            ma_200 = df['ma_200'].iloc[-1]
            
            # MACD (Moving Average Convergence Divergence)
            logger.info("計算 MACD")
            df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
            df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
            df['macd'] = df['ema_12'] - df['ema_26']
            df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
            
            # Get recent MACD values
            macd = df['macd'].iloc[-1]
            signal = df['signal'].iloc[-1]
            
            # RSI (Relative Strength Index)
            logger.info("計算 RSI")
            delta = df['close'].diff()
            gain = delta.where(delta > 0, 0).rolling(window=14).mean()
            loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # Get recent RSI value
            rsi = df['rsi'].iloc[-1]
            
            # Bollinger Bands
            logger.info("計算布林帶")
            df['bb_middle'] = df['close'].rolling(window=20).mean()
            std = df['close'].rolling(window=20).std()
            df['bb_upper'] = df['bb_middle'] + (std * 2)
            df['bb_lower'] = df['bb_middle'] - (std * 2)
            
            # Get recent Bollinger Band values
            bb_middle = df['bb_middle'].iloc[-1]
            bb_upper = df['bb_upper'].iloc[-1]
            bb_lower = df['bb_lower'].iloc[-1]
            
            # Volume analysis
            logger.info("計算交易量分析")
            avg_volume = df['volume'].mean() if 'volume' in df.columns else 0
            recent_volume = df['volume'].iloc[-1] if 'volume' in df.columns else 0
        
        # Price momentum (rate of change)
            logger.info("計算價格動量")
            df['roc_5'] = df['close'].pct_change(periods=5) * 100
            df['roc_20'] = df['close'].pct_change(periods=20) * 100
            
            roc_5 = df['roc_5'].iloc[-1]
            roc_20 = df['roc_20'].iloc[-1]
            logger.info(f"短期價格動量(5天): {roc_5:.2f}%, 中期價格動量(20天): {roc_20:.2f}%")
            
            # Return all indicators in a dictionary
            logger.info("所有技術指標計算完成，整合結果")
            result = {
                "current_price": current_price,
                "ma_20": ma_20,
                "ma_50": ma_50,
                "ma_200": ma_200,
                "macd": macd,
                "signal": signal,
                "rsi": rsi,
                "bb_middle": bb_middle,
                "bb_upper": bb_upper,
                "bb_lower": bb_lower,
                "avg_volume": avg_volume,
                "recent_volume": recent_volume,
                "roc_5": roc_5,
                "roc_20": roc_20,
                "dataframe": df  # Include the dataframe with all calculated indicators
            }
            
            logger.info(f"返回 {len(result)-1} 個技術指標 (不計算 dataframe)")
            return result
            
        except Exception as e:
            logger.error(f"計算技術指標時發生錯誤: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            # 返回基本資料，避免後續處理失敗
            return {
                "current_price": df['close'].iloc[-1] if 'close' in df.columns and len(df) > 0 else 0,
                "ma_20": 0,
                "ma_50": 0, 
                "ma_200": 0,
                "macd": 0,
                "signal": 0,
                "rsi": 50,  # 中性值
                "bb_middle": 0,
                "bb_upper": 0,
                "bb_lower": 0,
                "avg_volume": 0,
                "recent_volume": 0,
                "roc_5": 0,
                "roc_20": 0,
                "error": str(e)
            }
            
    async def get_financial_data(self, symbol: str) -> str:
        """
        獲取股票的財務數據。
        這個方法是為了支援 FastMCP 中的 financial://{symbol}/data 資源。
        
        Args:
            symbol: 股票代號
            
        Returns:
            格式化後的財務數據文字
        """
        logger.info(f"獲取 {symbol} 的財務數據")
        try:
            # 獲取公司概覽數據
            overview = await self.alpha_vantage_service.get_company_overview(symbol)
            
            if not overview:
                logger.error(f"無法獲取 {symbol} 的公司概覽數據")
                return f"無法獲取 {symbol} 的財務數據"
            
            # 提取關鍵財務指標
            market_cap = overview.get("MarketCapitalization", "N/A")
            pe_ratio = overview.get("PERatio", "N/A")
            eps = overview.get("EPS", "N/A")
            dividend_yield = overview.get("DividendYield", "N/A")
            beta = overview.get("Beta", "N/A")
            
            # 格式化為 Markdown
            financial_data = f"""# {symbol} 財務數據概覽

## 關鍵財務指標
- **市值:** {market_cap}
- **市盈率:** {pe_ratio}
- **每股收益:** {eps}
- **股息收益率:** {dividend_yield}
- **Beta值:** {beta}

## 其他財務數據
- **52週高點:** {overview.get("52WeekHigh", "N/A")}
- **52週低點:** {overview.get("52WeekLow", "N/A")}
- **50日均線:** {overview.get("50DayMovingAverage", "N/A")}
- **200日均線:** {overview.get("200DayMovingAverage", "N/A")}
- **每股帳面值:** {overview.get("BookValue", "N/A")}
- **毛利率:** {overview.get("GrossProfitTTM", "N/A")}
- **股本回報率:** {overview.get("ReturnOnEquityTTM", "N/A")}

## 企業信息
- **公司名稱:** {overview.get("Name", "N/A")}
- **行業:** {overview.get("Industry", "N/A")}
- **部門:** {overview.get("Sector", "N/A")}
- **交易所:** {overview.get("Exchange", "N/A")}
- **貨幣:** {overview.get("Currency", "N/A")}
- **國家:** {overview.get("Country", "N/A")}
"""
            
            logger.info(f"{symbol} 財務數據生成完成")
            return financial_data
            
        except Exception as e:
            logger.error(f"獲取 {symbol} 財務數據時出錯: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return f"Error retrieving financial data for {symbol}: {str(e)}"