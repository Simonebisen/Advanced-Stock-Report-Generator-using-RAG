import logging
import requests
from typing import List, Dict, Any

# 獲取 stock_report 日誌記錄器
logger = logging.getLogger('stock_report')

class WebSearchService:
    """服務用於執行網頁搜索獲取股票信息。"""
    
    def __init__(self, api_key: str = None):
        """
        初始化網頁搜索服務。
        
        Args:
            api_key: 搜索API密鑰（可選）
        """
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search"
        logger.info("WebSearchService 初始化完成")
    
    def search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        執行搜索並返回結果 (同步方法).
        
        Args:
            query: 搜索查詢字符串
            num_results: 返回結果數量
            
        Returns:
            搜索結果列表
        """
        logger.info(f"WebSearchService 執行網頁搜索: '{query}'")
        
        # 檢查API密鑰
        if not self.api_key:
            logger.warning("WebSearchService: 未提供API密鑰，使用模擬數據")
            return self._mock_search_results(query)
            
        try:
            # 準備請求參數
            params = {
                "q": query,
                "api_key": self.api_key,
                "engine": "google",
                "num": num_results,
                "gl": "us",  # Google location parameter (United States)
                "hl": "en"   # Language (English)
            }
            
            logger.info(f"WebSearchService: 準備發送請求，參數設置完成")
            
            # 使用 requests 執行請求 (同步)
            response = requests.get(self.base_url, params=params)
            
            # 檢查響應狀態
            if response.status_code == 200:
                data = response.json()
                logger.info(f"WebSearchService: API響應成功，狀態碼: {response.status_code}")
                
                # 提取搜索結果
                results = data.get("organic_results", [])
                logger.info(f"WebSearchService: 提取到 {len(results)} 個搜索結果")
                
                # 格式化結果
                formatted_results = []
                for result in results:
                    formatted_result = {
                        "title": result.get("title", ""),
                        "link": result.get("link", ""),
                        "snippet": result.get("snippet", ""),
                        "source": result.get("source", "")
                    }
                    formatted_results.append(formatted_result)
                
                logger.info(f"WebSearchService: 搜索完成，返回 {len(formatted_results)} 個結果")
                return formatted_results
            else:
                logger.error(f"WebSearchService: 搜索API錯誤: {response.status_code} - {response.text}")
                return self._mock_search_results(query)
                
        except Exception as e:
            logger.error(f"WebSearchService: 搜索過程中發生錯誤: {str(e)}", exc_info=True)
            return self._mock_search_results(query)
    
    def _mock_search_results(self, query: str) -> List[Dict[str, Any]]:
        """
        生成模擬搜索結果，用於API不可用時的備用
        
        Args:
            query: 搜索查詢
            
        Returns:
            模擬的搜索結果列表
        """
        # 從查詢中提取股票代碼
        import re
        stock_match = re.search(r'([A-Z]{1,5})', query)
        stock_symbol = stock_match.group(1) if stock_match else "STOCK"
        
        logger.info(f"WebSearchService: 為 {stock_symbol} 生成模擬搜索結果")
        
        # 返回模擬結果
        mock_results = [
            {
                "title": f"{stock_symbol} Reports Strong Quarterly Results",
                "link": f"https://example.com/finance/{stock_symbol.lower()}/earnings",
                "snippet": f"{stock_symbol} reported quarterly earnings that exceeded analyst expectations, with revenue growing 15% year-over-year to $10.2 billion and EPS of $2.45, up 18% from the same period last year.",
                "source": "Financial News"
            },
            {
                "title": f"Analyst Upgrades {stock_symbol} to 'Buy'",
                "link": f"https://example.com/finance/analyst-ratings/{stock_symbol.lower()}-upgrade",
                "snippet": f"Morgan Stanley upgraded {stock_symbol} from 'Hold' to 'Buy' with a price target of $180, citing strong growth prospects in the company's new product lines and expanding market share in key segments.",
                "source": "Market Analysis"
            },
            {
                "title": f"{stock_symbol} Announces Major Supply Chain Improvements",
                "link": f"https://example.com/finance/supply-chain/{stock_symbol.lower()}-improvements",
                "snippet": f"{stock_symbol} has announced significant improvements to its supply chain, reducing lead times by 30% and cutting logistics costs by 15%. This is expected to improve gross margins by approximately 2 percentage points starting in Q3 2023.",
                "source": "Supply Chain Digest"
            },
            {
                "title": f"Industry Outlook: What's Next for {stock_symbol}",
                "link": f"https://example.com/finance/industry-outlook/{stock_symbol.lower()}-sector",
                "snippet": f"The industry is expected to grow at 12% CAGR over the next five years. {stock_symbol}, as the market leader with 35% market share, is well-positioned to capitalize on this growth through its innovative product portfolio and strategic partnerships.",
                "source": "Industry Report"
            },
            {
                "title": f"{stock_symbol} Signs Major Partnership Deal",
                "link": f"https://example.com/finance/partnerships/{stock_symbol.lower()}-announcement",
                "snippet": f"{stock_symbol} has signed a 5-year strategic partnership with three major industry players to develop next-generation technology solutions. The deal is valued at approximately $500 million and is expected to contribute to revenue starting in late 2023.",
                "source": "Business News"
            },
            {
                "title": f"{stock_symbol}'s Role in Reshaping the Industry",
                "link": f"https://example.com/finance/industry-analysis/{stock_symbol.lower()}-impact",
                "snippet": f"{stock_symbol} continues to play a pivotal role in industry transformation, with its market-leading position allowing it to set standards and influence the direction of technological development across the ecosystem.",
                "source": "Tech Analysis"
            },
            {
                "title": f"{stock_symbol} Secures Government Contract",
                "link": f"https://example.com/finance/contracts/{stock_symbol.lower()}-government",
                "snippet": f"{stock_symbol} has been awarded a $2.5 billion contract to supply technology systems to government agencies over the next 7 years. This represents the largest government contract in the company's history.",
                "source": "Contract News"
            },
            {
                "title": f"{stock_symbol}'s Competitive Advantages Analysis",
                "link": f"https://example.com/finance/competition/{stock_symbol.lower()}-advantages",
                "snippet": f"{stock_symbol} maintains significant competitive advantages through its proprietary technology, extensive patent portfolio, strong brand recognition, and vast ecosystem of complementary products and services.",
                "source": "Competitive Analysis"
            }
        ]
        
        logger.info(f"WebSearchService: 生成了 {len(mock_results)} 個模擬搜索結果")
        return mock_results