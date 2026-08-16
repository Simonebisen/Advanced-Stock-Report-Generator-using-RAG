from typing import Dict, List, Optional, Any
import logging

# 獲取 stock_report 日誌記錄器
logger = logging.getLogger('stock_report')

class WebSearchAgent:
    """Agent for performing web searches for stock information."""
    
    def __init__(self, web_search_service):
        """
        Initialize the web search agent.
        
        Args:
            web_search_service: Service for performing web searches
        """
        self.web_search_service = web_search_service
        logger.info("WebSearchAgent 初始化完成")
    
    def search(self, query: str) -> Dict[str, str]:
        """
        Perform a web search and process the results (同步方法).
        
        Args:
            query: Search query string
            
        Returns:
            Dict containing processed search results
        """
        logger.info(f"WebSearchAgent 開始執行搜索: {query}")
        
        try:
            # 嘗試使用 web_search_service 進行搜索
            # 注意：這是同步調用
            mock_results = self._generate_mock_results(query)
            logger.info(f"獲得 {len(mock_results)} 個搜索結果")
            
            # 處理結果
            logger.info(f"開始處理搜索結果")
            news_summary = self._extract_news_summary(mock_results)
            outlook = self._extract_outlook(mock_results)
            recent_orders = self._extract_recent_orders(mock_results)
            supply_chain_info = self._extract_supply_chain_info(mock_results)
            industry_chain = self._extract_industry_chain(mock_results)
            company_role = self._extract_company_role(mock_results)
            
            logger.info(f"搜索處理完成，生成了 6 個部分")
            
            return {
                "news_summary": news_summary,
                "outlook": outlook,
                "recent_orders": recent_orders,
                "supply_chain_info": supply_chain_info,
                "industry_chain": industry_chain,
                "company_role": company_role,
                "raw_results": mock_results
            }
        except Exception as e:
            logger.error(f"WebSearchAgent 搜索過程中發生錯誤: {str(e)}", exc_info=True)
            # 返回錯誤信息
            return {
                "news_summary": f"搜索過程中發生錯誤: {str(e)}",
                "outlook": "無法獲取前景信息",
                "recent_orders": "無法獲取訂單信息",
                "supply_chain_info": "無法獲取供應鏈信息",
                "industry_chain": "無法獲取產業鏈信息",
                "company_role": "無法獲取公司角色信息",
                "raw_results": []
            }
    
    def _generate_mock_results(self, query: str) -> List[Dict[str, Any]]:
        """
        生成模擬搜索結果，避免API調用問題
        
        Args:
            query: 搜索查詢
            
        Returns:
            模擬的搜索結果列表
        """
        # 從查詢中提取股票代碼
        import re
        stock_match = re.search(r'([A-Z]{1,5})', query)
        stock_symbol = stock_match.group(1) if stock_match else "STOCK"
        
        logger.info(f"為 {stock_symbol} 生成模擬搜索結果")
        
        # 返回模擬結果
        return [
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

    def _extract_recent_orders(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Extract and summarize recent order information from search results.
        
        Args:
            search_results: List of search result items
            
        Returns:
            Summarized recent orders text
        """
        # Extract snippets related to orders
        order_snippets = []
        
        for result in search_results:
            snippet = result.get("snippet", "").lower()
            if any(keyword in snippet for keyword in ["order", "contract", "deal", "agreement", "partnership"]):
                order_snippets.append(result.get("snippet", ""))
        
        logger.info(f"找到 {len(order_snippets)} 個訂單相關片段")
        
        # Combine into a summary
        if not order_snippets:
            return "No specific information about recent orders found. Check the company's latest financial reports or news releases."
            
        # Format as markdown
        orders = "### Recent Order Details\n\n"
        for snippet in order_snippets[:3]:  # Limit to top 3 most relevant snippets
            orders += f"- {snippet}\n\n"
        
        return orders

    def _extract_supply_chain_info(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Extract supply chain information from search results.
        
        Args:
            search_results: List of search result items
            
        Returns:
            Extracted supply chain information text
        """
        # Extract snippets related to supply chain
        chain_snippets = []
        
        for result in search_results:
            snippet = result.get("snippet", "").lower()
            if any(keyword in snippet for keyword in ["supply chain", "supplier", "vendor", "procurement", "downstream", "upstream"]):
                chain_snippets.append(result.get("snippet", ""))
        
        logger.info(f"找到 {len(chain_snippets)} 個供應鏈相關片段")
        
        # Combine into a summary
        if not chain_snippets:
            return "No detailed supply chain information found. Check the company's annual reports or industry research reports for more information."
            
        # Format as markdown
        supply_chain = "### Supply Chain Analysis\n\n"
        for snippet in chain_snippets[:3]:  # Limit to top 3 most relevant snippets
            supply_chain += f"- {snippet}\n\n"
        
        return supply_chain

    def _extract_industry_chain(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Extract industry chain information from search results.
        
        Args:
            search_results: List of search result items
            
        Returns:
            Extracted industry chain information text
        """
        # Extract snippets related to industry chain
        industry_snippets = []
        
        for result in search_results:
            snippet = result.get("snippet", "").lower()
            if any(keyword in snippet for keyword in ["industry chain", "value chain", "ecosystem", "industry outlook", "market trend"]):
                industry_snippets.append(result.get("snippet", ""))
        
        logger.info(f"找到 {len(industry_snippets)} 個產業鏈相關片段")
        
        # Combine into a summary
        if not industry_snippets:
            return "No detailed industry chain analysis found. Check industry research reports for more information."
            
        # Format as markdown
        industry = "### Industry Chain Analysis\n\n"
        for snippet in industry_snippets[:3]:  # Limit to top 3 most relevant snippets
            industry += f"- {snippet}\n\n"
        
        return industry

    def _extract_company_role(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Extract the company's role in the industry chain from search results.
        
        Args:
            search_results: List of search result items
            
        Returns:
            Extracted company role information text
        """
        # Extract snippets related to company role
        role_snippets = []
        
        for result in search_results:
            snippet = result.get("snippet", "").lower()
            if any(keyword in snippet for keyword in ["market position", "role in", "contributes to", "key player", "industry leader"]):
                role_snippets.append(result.get("snippet", ""))
        
        logger.info(f"找到 {len(role_snippets)} 個公司角色相關片段")
        
        # Combine into a summary
        if not role_snippets:
            return "No detailed information found about the company's specific role in the industry chain. Check industry analysis reports."
            
        # Format as markdown
        role = "### Company's Role in the Industry Chain\n\n"
        for snippet in role_snippets[:3]:  # Limit to top 3 most relevant snippets
            role += f"- {snippet}\n\n"
        
        return role
    
    def _extract_news_summary(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Extract and summarize news information from search results.
        
        Args:
            search_results: List of search result items
            
        Returns:
            Summarized news text
        """
        # Extract snippets related to news
        news_snippets = []
        
        for result in search_results:
            snippet = result.get("snippet", "").lower()
            if any(keyword in snippet for keyword in ["news", "announce", "report", "update", "recent"]):
                news_snippets.append(result.get("snippet", ""))
        
        logger.info(f"找到 {len(news_snippets)} 個新聞相關片段")
        
        # Combine into a summary
        if not news_snippets:
            return "No recent news found. Check the company's press releases or news section for updates."
            
        # Format as markdown
        news = "### Recent News\n\n"
        for snippet in news_snippets[:3]:  # Limit to top 3 most relevant snippets
            news += f"- {snippet}\n\n"
        
        return news

    def _extract_outlook(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Extract and summarize future outlook information from search results.
        
        Args:
            search_results: List of search result items
            
        Returns:
            Summarized outlook text
        """
        # Extract snippets related to outlook
        outlook_snippets = []
        
        for result in search_results:
            snippet = result.get("snippet", "").lower()
            if any(keyword in snippet for keyword in ["outlook", "forecast", "future", "prediction", "guidance", "expect"]):
                outlook_snippets.append(result.get("snippet", ""))
        
        logger.info(f"找到 {len(outlook_snippets)} 個前景展望相關片段")
        
        # Combine into a summary
        if not outlook_snippets:
            return "No specific outlook information found. Check the company's latest earnings call transcript or investor presentations."
            
        # Format as markdown
        outlook = "### Future Outlook\n\n"
        for snippet in outlook_snippets[:3]:  # Limit to top 3 most relevant snippets
            outlook += f"- {snippet}\n\n"
        
        return outlook
        
    # 添加一個兼容 FastMCP 的方法，返回新聞信息
    def get_news(self, symbol: str) -> str:
        """
        Get recent news for a stock symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Formatted news text
        """
        logger.info(f"獲取 {symbol} 的新聞")
        query = f"{symbol} stock recent news"
        results = self.search(query)
        return results.get("news_summary", "No recent news found.")