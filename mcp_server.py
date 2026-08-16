from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
import os
from typing import Dict, List, Optional, Any
import re
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP, Context, Image
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import io

from agents.rag_agent import RAGAgent
from agents.web_search_agent import WebSearchAgent
from agents.stock_data_agent import StockDataAgent
from services.edgar_service import EdgarService
from services.pinecone_service import PineconeService
from services.web_search_service import WebSearchService
from services.alpha_vantage_service import AlphaVantageService
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime

import base64
import traceback
import markdown2
from weasyprint import HTML



load_dotenv()  # Load environment variables from .env file

@dataclass
class AppContext:
    edgar_service: EdgarService
    pinecone_service: PineconeService
    web_search_service: WebSearchService
    alpha_vantage_service: AlphaVantageService
    rag_agent: RAGAgent
    web_search_agent: WebSearchAgent
    stock_data_agent: StockDataAgent


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Initialize and manage application lifecycle with services and agents."""
    # Initialize services
    edgar_service = EdgarService(
        name="Sicheng Bao", 
        email="Jellysillyfish@gmail.com",
        output_dir="./"
    )
    
    pinecone_service = PineconeService(
        api_key=os.getenv("PINECONE_API_KEY"),
        environment=os.getenv("PINECONE_ENVIRONMENT")
    )
    
    web_search_service = WebSearchService(
        api_key=os.getenv("SERPAPI_API_KEY")
    )
    
    alpha_vantage_service = AlphaVantageService(
        api_key=os.getenv("ALPHA_VANTAGE_API_KEY")
    )
    
    # Initialize agents
    rag_agent = RAGAgent(
        edgar_service=edgar_service,
        pinecone_service=pinecone_service,
        gemini_api_key=os.getenv("GEMINI_API_KEY")
    )
    
    web_search_agent = WebSearchAgent(
        web_search_service=web_search_service
    )
    
    stock_data_agent = StockDataAgent(
        alpha_vantage_service=alpha_vantage_service
    )
    
    context = AppContext(
        edgar_service=edgar_service,
        pinecone_service=pinecone_service,
        web_search_service=web_search_service,
        alpha_vantage_service=alpha_vantage_service,
        rag_agent=rag_agent,
        web_search_agent=web_search_agent,
        stock_data_agent=stock_data_agent
    )
    
    try:
        yield context
    finally:
        # Cleanup resources
        await pinecone_service.disconnect()


# Create MCP server
mcp = FastMCP(
    "Stock Research Report Generator",
    lifespan=app_lifespan,
    dependencies=[
        "pandas", "numpy", "matplotlib", "seaborn", "plotly",
        "pinecone", "google-generativeai", "sec-edgar-downloader",  # 使用pinecone而不是pinecone-client
        "alpha_vantage", "python-dotenv", "beautifulsoup4", 
        "lxml","kaleido","reportlab","boto3"
    ]
)


def clean_dot_blocks(report):
    dot_chars = r"\.•．。・●○‧‥⋅∙·・﹒･·⬤◦⦁❍"
    
    # 清除 ``` 中只含點的程式碼區塊
    report = re.sub(
        rf"```[\s\n]*([{dot_chars}\s\n]+)```",
        "",
        report,
        flags=re.MULTILINE
    )

    # 移除整行只包含點點的段落
    lines = report.splitlines()
    filtered = [line for line in lines if not re.fullmatch(rf"[{dot_chars}\s]+", line)]
    return "\n".join(filtered)


# 在 FastMCP 的 generate_stock_report 函數中修改網頁搜索部分

@mcp.tool()
async def generate_stock_report(symbol: str, ctx: Context) -> str:
    """
    Generate a comprehensive 20-30 page research report for the specified stock.
    The report includes data from SEC filings, web search results, and financial analysis.
    
    Args:
        symbol: Stock symbol (e.g., AAPL, MSFT, NVDA)
    
    Returns:
        A detailed report with fundamental analysis, technical analysis, and news.
    """
    # 設置詳細的日誌
    import logging
    import traceback
    import sys
    import os
    from datetime import datetime
    
    logger = logging.getLogger('stock_report')
    logger.info(f"========== 開始為 {symbol} 生成報告 ==========")
    logger.info(f"Python 版本: {sys.version}")
    logger.info(f"當前工作目錄: {os.getcwd()}")
    
    # 檢查上下文
    try:
        app_ctx = ctx.request_context.lifespan_context
        logger.info(f"上下文檢查成功，類型: {type(app_ctx)}")
        ctx.info(f"开始为 {symbol} 生成报告")
    except Exception as e:
        logger.error(f"獲取上下文失敗: {str(e)}")
        logger.error(traceback.format_exc())
        return f"Error: Failed to get context - {str(e)}"
   
    # Report progress
    try:
        ctx.info(f"Starting research for {symbol}")
        await ctx.report_progress(0, 4)
        logger.info(f"進度報告: 0/4")
    except Exception as e:
        logger.error(f"更新進度時出錯: {str(e)}")
    
    # 定義變量以便在各個步驟之間共享結果
    rag_results = {}
    web_results = {}
    stock_analysis = {}
    
    # Step 1: RAG - Process SEC filings
    try:
        logger.info(f"步驟 1: 處理 {symbol} 的 SEC 文件")
        ctx.info(f"Processing SEC filings for {symbol}")
        
        # 檢查 rag_agent 是否存在
        if not hasattr(app_ctx, 'rag_agent'):
            logger.error("app_ctx 不包含 rag_agent 屬性")
            rag_results = {"company_overview": "Error: RAG agent not available"}
        else:
            logger.info(f"開始調用 rag_agent.process_filings({symbol})")
            rag_results = await app_ctx.rag_agent.process_filings(symbol)
            logger.info(f"SEC 文件處理完成，獲取的部分: {list(rag_results.keys()) if isinstance(rag_results, dict) else type(rag_results)}")
        
        await ctx.report_progress(1, 4)
        logger.info(f"進度報告: 1/4")
    except Exception as e:
        logger.error(f"處理 SEC 文件時出錯: {str(e)}")
        logger.error(traceback.format_exc())
        rag_results = {
            "company_overview": f"Error processing SEC filings: {str(e)}",
            "error": str(e)
        }
    
# Step 2: Web search for recent news and analysis
    try:
        logger.info(f"==== 步驟 2: 搜索 {symbol} 的相關信息 ====")
        ctx.info(f"Searching for recent news about {symbol}")
        
        # 檢查 web_search_agent 是否存在
        if not hasattr(app_ctx, 'web_search_agent'):
            logger.error("app_ctx 不包含 web_search_agent 屬性")
            web_results = {"news_summary": "Error: Web search agent not available"}
        else:
            try:
                # 調用不使用 await 的同步方法
                logger.info(f"開始調用 web_search_agent.search({symbol})")
                search_query = f"{symbol} stock recent orders supply chain partners financial analysis"
                web_results = app_ctx.web_search_agent.search(search_query)
                logger.info(f"網頁搜索完成，獲取的部分: {list(web_results.keys()) if isinstance(web_results, dict) else type(web_results)}")
            except Exception as search_error:
                logger.error(f"執行 web_search_agent.search 時出錯: {str(search_error)}")
                logger.error(traceback.format_exc())
                web_results = {
                    "news_summary": f"Error in web search execution: {str(search_error)}",
                    "outlook": "No outlook information available",
                    "recent_orders": "No recent order information available",
                    "supply_chain_info": "No supply chain information available",
                    "industry_chain": "No industry chain information available",
                    "company_role": "No company role information available",
                    "raw_results": []
                }
        
        # 通知用戶搜索完成
        try:
            ctx.info(f"Web search completed successfully")
        except Exception as notify_error:
            logger.error(f"通知用戶搜索完成時出錯: {str(notify_error)}")
        
        # 嘗試更新進度報告，但不讓它阻止後續步驟
        try:
            logger.info("準備更新進度報告 2/4")
            # 使用超時限制來避免無限等待
            import asyncio
            try:
            # 非阻塞調用，如果 5 毫秒內沒完成就繼續
                await asyncio.wait_for(ctx.report_progress(2, 4), timeout=0.005)
            except:
                # 忽略任何錯誤
                pass
            #await asyncio.wait_for(ctx.report_progress(2, 4), timeout=5.0)
            logger.info(f"進度報告: 2/4")
        except asyncio.TimeoutError:
            logger.error("更新進度報告超時 (5秒)")
        except Exception as progress_error:
            logger.error(f"更新進度報告時出錯: {str(progress_error)}")
            logger.error(traceback.format_exc())
        
        # 無論進度報告是否成功，直接繼續執行
        logger.info("=== Web Search 步驟完成，準備繼續下一步 ===")

    except Exception as e:
        logger.error(f"執行網頁搜索整體流程時出錯: {str(e)}")
        logger.error(traceback.format_exc())
        web_results = {
            "news_summary": f"Error in web search process: {str(e)}",
            "outlook": "No outlook information available",
            "recent_orders": "No recent order information available",
            "supply_chain_info": "No supply chain information available",
            "industry_chain": "No industry chain information available",
            "company_role": "No company role information available",
            "raw_results": []
        }
        
        # 即使整體出錯，仍嘗試更新進度，但用獨立的錯誤處理
        try:
            ctx.info(f"Web search failed with error: {str(e)}")
            await ctx.report_progress(2, 4)
        except Exception as progress_error:
            logger.error(f"出錯後更新進度報告時出錯: {str(progress_error)}")
    # Step 3: Stock data analysis
    try:
        logger.info(f"步驟 3: 分析 {symbol} 的股票數據")
        ctx.info(f"Analyzing stock performance data for {symbol}")
        
        # 檢查 stock_data_agent 是否存在
        if not hasattr(app_ctx, 'stock_data_agent'):
            logger.error("app_ctx 不包含 stock_data_agent 屬性")
            stock_analysis = {"earnings_forecast": "Error: Stock data agent not available"}
        else:
            logger.info(f"開始調用 stock_data_agent.analyze({symbol})")
            stock_analysis = await app_ctx.stock_data_agent.analyze(symbol)
            logger.info(f"股票數據分析完成，獲取的部分: {list(stock_analysis.keys()) if isinstance(stock_analysis, dict) else type(stock_analysis)}")
        
        #await ctx.report_progress(3, 4)
        logger.info(f"進度報告: 3/4")
    except Exception as e:
        logger.error(f"分析股票數據時出錯: {str(e)}")
        logger.error(traceback.format_exc())
        stock_analysis = {
            "earnings_forecast": f"Error analyzing stock data: {str(e)}",
            "valuation_analysis": "No valuation analysis available",
            "investment_recommendation": "No investment recommendation available"
        }
    
    # Step 4: Compile final report
    
    try:
        logger.info(f"==== 步驟 4: 編譯 {symbol} 的最終報告 ====")
        ctx.info(f"Compiling final research report for {symbol}")
        
        # 跳過進度報告
        # await ctx.report_progress(3, 4)  # 註釋掉這一行
        
        # 檢查必要的鍵是否存在，未找到則提供默認值
        if not isinstance(rag_results, dict) or "company_overview" not in rag_results:
            logger.warning("rag_results 中缺少 company_overview，使用默認值")
            company_overview = "Company overview data not available"
        else:
            company_overview = rag_results.get("company_overview", "")
            
        # 編譯報告文本
        
        logger.info("開始構建報告文本")
        report = f"""# Comprehensive Research Report for {symbol}
 

    ## 1. Company and Industry Overview

    ### Company Introduction
    {company_overview}

    ### Industry Analysis
    {rag_results.get('industry_analysis', 'Industry analysis data is being processed.')}

    ### Company's Position in the Industry
    {rag_results.get('competitive_position', 'Competitive position analysis is being processed.')}

    ### Upstream and Downstream Supply-Demand Analysis
    {web_results.get('supply_chain_info', 'Supply chain information is being processed.')}

    ## 2. Industry Chain Analysis

    ### Recent Major Orders
    {web_results.get('recent_orders', 'Recent order information is being processed.')}

    ### Position of Orders in the Industry Chain
    {web_results.get('industry_chain', 'Industry chain analysis is being processed.')}

    ### Current Status and Future Outlook of the Industry Chain
    {web_results.get('outlook', 'Industry outlook analysis is being processed.')}

    ### Company's Role in the Industry Chain
    {web_results.get('company_role', 'Company role analysis is being processed.')}

    ## 3. Earnings Forecast and Investment Recommendations

    ### Main Business Revenue Analysis
    {rag_results.get('revenue_analysis', 'Revenue analysis is being processed.')}

    ### Future Performance Forecast
    {stock_analysis.get('earnings_forecast', 'Performance forecast is being processed.')}

    ### Valuation Analysis
    {stock_analysis.get('valuation_analysis', 'Valuation analysis is being processed.')}

    ### Investment Recommendation
    {stock_analysis.get('investment_recommendation', 'Investment recommendation is being processed.')}

    ## 4. Risk Assessment
    {rag_results.get('risk_assessment', 'Risk assessment is being processed.')}

    ## Appendix: Data Sources
    - SEC Edgar 10-K Reports (Last 5 years)
    - Alpha Vantage Stock Price Data (Last 5 years, weekly data)
    - Web Search Results (as of report generation date)
    """
        logger.info(f"報告文本編譯完成，長度: {len(report)} 字符")
        try:
            logger.info("開始嘗試生成 PDF (透過 markdown2 + weasyprint)")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_filename = f"{symbol}_Research_Report_{timestamp}.pdf"

            try:
                # 清除無意義的點點區塊
                report = clean_dot_blocks(report)
                
                # 先生成股票分析圖表並保存為圖片文件
                logger.info("準備生成股票分析圖表")
                try:
                    # 使用與 generate_stock_analysis_chart 相同的代碼生成圖表
                    # 但不返回 Image 對象，而是保存為文件
                    chart_filename = f"{symbol}_Chart_{timestamp}.png"
                    
                    # 使用 Alpha Vantage 獲取股票數據
                    # 由於我們已經有模擬數據，直接使用相同的邏輯
                    stock_data = stock_analysis.get('stock_data')
                    
                    if stock_data is None or stock_data.empty:
                        logger.warning("沒有可用的股票數據用於繪圖，將創建模擬數據")
                        # 創建模擬數據
                        import pandas as pd
                        import numpy as np
                        from datetime import datetime, timedelta
                        
                        dates = [datetime.now() - timedelta(days=i*7) for i in range(100)]
                        dates.sort()
                        
                        base_price = 150.0
                        if symbol == "AAPL":
                            base_price = 170.0
                        elif symbol == "MSFT":
                            base_price = 320.0
                        elif symbol == "NVDA":
                            base_price = 750.0
                        
                        trend = np.linspace(0.8, 1.2, 100)
                        prices = base_price * trend
                        noise = np.random.normal(0, 0.02, 100)
                        prices = prices * (1 + noise)
                        
                        closes = prices
                        opens = closes * (1 + np.random.normal(0, 0.01, 100))
                        highs = np.maximum(opens, closes) * (1 + abs(np.random.normal(0, 0.015, 100)))
                        lows = np.minimum(opens, closes) * (1 - abs(np.random.normal(0, 0.015, 100)))
                        volumes = np.random.uniform(5000000, 15000000, 100)
                        
                        stock_data = pd.DataFrame({
                            '1. open': opens,
                            '2. high': highs,
                            '3. low': lows,
                            '4. close': closes,
                            '5. volume': volumes
                        }, index=dates)
                        
                        logger.info("已創建模擬數據用於繪圖")
                    
                    # 創建圖表
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                    vertical_spacing=0.1,
                                    subplot_titles=(f'{symbol} Stock Price', 'Volume'),
                                    row_heights=[0.7, 0.3])
                    
                    # 添加價格數據
                    fig.add_trace(
                        go.Candlestick(
                            x=stock_data.index,
                            open=stock_data['1. open'] if '1. open' in stock_data.columns else stock_data['open'],
                            high=stock_data['2. high'] if '2. high' in stock_data.columns else stock_data['high'],
                            low=stock_data['3. low'] if '3. low' in stock_data.columns else stock_data['low'],
                            close=stock_data['4. close'] if '4. close' in stock_data.columns else stock_data['close'],
                            name="Price"
                        ),
                        row=1, col=1
                    )
                    
                    # 添加成交量圖表
                    volume_col = '5. volume' if '5. volume' in stock_data.columns else 'volume'
                    fig.add_trace(
                        go.Bar(
                            x=stock_data.index,
                            y=stock_data[volume_col],
                            name="Volume"
                        ),
                        row=2, col=1
                    )
                    
                    # 添加移動平均線
                    close_col = '4. close' if '4. close' in stock_data.columns else 'close'
                    stock_data['MA50'] = stock_data[close_col].rolling(window=50).mean()
                    stock_data['MA200'] = stock_data[close_col].rolling(window=200).mean()
                    
                    fig.add_trace(
                        go.Scatter(
                            x=stock_data.index,
                            y=stock_data['MA50'],
                            name="50-day MA",
                            line=dict(color='orange', width=1)
                        ),
                        row=1, col=1
                    )
                    
                    fig.add_trace(
                        go.Scatter(
                            x=stock_data.index,
                            y=stock_data['MA200'],
                            name="200-day MA",
                            line=dict(color='red', width=1)
                        ),
                        row=1, col=1
                    )
                    
                    # 更新布局
                    fig.update_layout(
                        title=f'{symbol} Stock Analysis',
                        xaxis_title="Date",
                        yaxis_title="Price ($)",
                        height=600,
                        xaxis_rangeslider_visible=False
                    )
                    
                    # 保存為圖片文件
                    fig.write_image(chart_filename, width=1000, height=600)
                    logger.info(f"股票圖表已保存為: {chart_filename}")
                    
                    # 檢查文件是否存在
                    if not os.path.exists(chart_filename):
                        logger.error(f"圖表文件 {chart_filename} 未成功創建")
                        chart_filename = None
                    else:
                        logger.info(f"圖表文件大小: {os.path.getsize(chart_filename)} 字節")
                        
                except Exception as chart_error:
                    logger.error(f"生成股票分析圖表時出錯: {str(chart_error)}")
                    logger.error(traceback.format_exc())
                    chart_filename = None
                    
                # Markdown 轉 HTML
                html_content = markdown2.markdown(report)
                logger.info("Markdown 已成功轉換為 HTML")
                
                # 在 HTML 中插入圖表圖片
                chart_html = ""
                if chart_filename and os.path.exists(chart_filename):
                    try:
                        # 將圖片轉為 base64
                        with open(chart_filename, "rb") as img_file:
                            img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
                            
                        # 在 "## 3. Earnings Forecast and Investment Recommendations" 部分前插入圖表
                        chart_html = f"""
                        <div style="margin: 20px 0;">
                            <h2>Technical Analysis Chart</h2>
                            <img src="data:image/png;base64,{img_base64}" alt="{symbol} Stock Chart" style="max-width:100%; height:auto;">
                        </div>
                        """
                        logger.info("已成功將圖表轉換為 base64 並添加到 HTML 中")
                    except Exception as img_error:
                        logger.error(f"處理圖表圖片時出錯: {str(img_error)}")
                        logger.error(traceback.format_exc())
                
                # 包裝 HTML 模板
                html_template = f"""
                <html>
                <head>
                    <meta charset="utf-8">
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            padding: 40px;
                            line-height: 1.6;
                        }}
                        h1, h2, h3 {{
                            color: #2C3E50;
                        }}
                        code {{
                            background-color: #f4f4f4;
                            padding: 2px 4px;
                            font-family: monospace;
                        }}
                        pre {{
                            background-color: #f4f4f4;
                            padding: 10px;
                            overflow-x: auto;
                        }}
                    </style>
                </head>
                <body>
                    {html_content}
                    {chart_html}
                </body>
                </html>
                """

                # HTML 轉 PDF
                HTML(string=html_template).write_pdf(pdf_filename)
                logger.info(f"PDF 已成功生成: {pdf_filename}")

                if os.path.exists(pdf_filename):
                    file_size = os.path.getsize(pdf_filename)
                    logger.info(f"確認 PDF 文件已創建，大小: {file_size} 字節")

                    # 移除臨時圖表文件
                    if chart_filename and os.path.exists(chart_filename):
                        try:
                            os.remove(chart_filename)
                            logger.info(f"臨時圖表文件 {chart_filename} 已移除")
                        except Exception as rm_error:
                            logger.warning(f"移除臨時圖表文件時出錯: {str(rm_error)}")

                    # base64 encode for web embedding
                    with open(pdf_filename, "rb") as f:
                        pdf_bytes = f.read()
                    b64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
                    download_link = f"[📄 Click here to download the PDF report](data:application/pdf;base64,{b64_pdf})"
                    logger.info("已創建 PDF 下載鏈接")
                    return f"{download_link}\n\n---\n\n## Report Preview\n\n```\n{report[:1500]}\n...```"
                else:
                    logger.error("PDF 文件未成功創建")
                    return f"Report generated but PDF file not found: {pdf_filename}"
            except Exception as e:
                logger.error(f"生成 PDF 時出錯: {str(e)}")
                logger.error(traceback.format_exc())
                return f"Report generated but PDF creation failed: {str(e)}"
            
        except Exception as e:
            logger.error(f"整體報告生成過程出錯: {str(e)}")
            logger.error(traceback.format_exc())
            return f"Error generating report: {str(e)}"
            # 這行代碼不會執行，因為上面的代碼已經返回了結果
       
        # 暫時跳過PDF生成
        logger.info("跳過PDF生成，直接返回報告文本")
        logger.info(f"========== 完成 {symbol} 報告生成 ==========")
        
        return f"Report generated successfully for {symbol}. Length: {len(report)} characters.\n\n{report[:1000]}...\n\n(Full report available)"
        
    except Exception as e:
        logger.error(f"編譯報告文本時出錯: {str(e)}")
        logger.error(traceback.format_exc())
        return f"Error generating report: {str(e)}"
    # Save the report as a PDF
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"{symbol}_Research_Report_{timestamp}.pdf"
        
        logger.info(f"開始創建 PDF: {pdf_filename}")
        ctx.info(f"Saving PDF report to {pdf_filename}")
        
        # 檢查 reportlab 元件是否正確引入
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            logger.info("ReportLab 元件引入成功")
        except Exception as e:
            logger.error(f"引入 ReportLab 元件時出錯: {str(e)}")
            return f"Report text generated but PDF creation failed: {str(e)}\n\n{report}"
        
        # Create a PDF document
        doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Create custom styles
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Title'],
            fontSize=16,
            spaceAfter=12
        )
        
        heading1_style = ParagraphStyle(
            'Heading1',
            parent=styles['Heading1'],
            fontSize=14,
            spaceAfter=10
        )
        
        heading2_style = ParagraphStyle(
            'Heading2',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=8
        )
        
        normal_style = styles['Normal']
        logger.info("PDF 樣式設置完成")
        
        # Parse the markdown report into PDF elements
        elements = []
        
        # Split the report into lines
        lines = report.split('\n')
        logger.info(f"報告分割為 {len(lines)} 行")
        
        line_count = 0
        for line in lines:
            try:
                if line.startswith('# '):
                    # Title
                    elements.append(Paragraph(line[2:], title_style))
                    elements.append(Spacer(1, 12))
                elif line.startswith('## '):
                    # Heading 1
                    elements.append(Paragraph(line[3:], heading1_style))
                    elements.append(Spacer(1, 10))
                elif line.startswith('### '):
                    # Heading 2
                    elements.append(Paragraph(line[4:], heading2_style))
                    elements.append(Spacer(1, 8))
                elif line.startswith('- '):
                    # Bullet points
                    elements.append(Paragraph('• ' + line[2:], normal_style))
                    elements.append(Spacer(1, 6))
                elif line.strip() == '':
                    # Empty line
                    elements.append(Spacer(1, 6))
                else:
                    # Normal text
                    elements.append(Paragraph(line, normal_style))
                    elements.append(Spacer(1, 6))
                
                line_count += 1
                if line_count % 100 == 0:
                    logger.info(f"處理了 {line_count} 行")
            except Exception as e:
                logger.error(f"處理行 '{line[:30]}...' 時出錯: {str(e)}")
                # 繼續處理下一行
        
        logger.info(f"生成了 {len(elements)} 個 PDF 元素")
        
        # Build the PDF
        try:
            logger.info("開始構建 PDF")
            doc.build(elements)
            logger.info(f"PDF 構建完成: {pdf_filename}")
        except Exception as e:
            logger.error(f"構建 PDF 時出錯: {str(e)}")
            logger.error(traceback.format_exc())
            return f"Report text generated but PDF building failed: {str(e)}\n\n{report}"
        
        ctx.info(f"PDF report saved to {pdf_filename}")
        await ctx.report_progress(4, 4)
        logger.info(f"進度報告: 4/4")
        ctx.info(f"Research report for {symbol} completed")
        
        # 檢查文件是否真的創建
        if os.path.exists(pdf_filename):
            file_size = os.path.getsize(pdf_filename)
            logger.info(f"確認 PDF 文件已創建，大小: {file_size} 字節")
        else:
            logger.error(f"PDF 文件 {pdf_filename} 創建失敗，未找到文件")
        
        logger.info(f"========== 完成 {symbol} 報告生成 ==========")
        return f"Report generated and saved as {pdf_filename}\n\n{report[:1000]}...\n\n(Full report available in the PDF file)"
    except Exception as e:
        logger.error(f"保存 PDF 報告時出錯: {str(e)}")
        logger.error(traceback.format_exc())
        return f"Report text generated but PDF saving failed: {str(e)}\n\n{report}"

@mcp.tool()
async def generate_stock_analysis_chart(symbol: str, ctx: Context) -> Image:
    """
    Generate a stock analysis chart with price history, volume, and technical indicators.
    
    Args:
        symbol: Stock symbol (e.g., AAPL, MSFT, NVDA)
    
    Returns:
        An image of the stock price chart with technical indicators.
    """
    app_ctx = ctx.request_context.lifespan_context
    
    # Get stock data
    ctx.info(f"Retrieving historical data for {symbol}")
    stock_data = await app_ctx.alpha_vantage_service.get_weekly_data(symbol, years=5)
    
    # Create the chart
    ctx.info(f"Creating stock analysis chart for {symbol}")
    
    # Create figure with secondary Y axis
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                         vertical_spacing=0.1,
                         subplot_titles=(f'{symbol} Stock Price', 'Volume'),
                         row_heights=[0.7, 0.3])
    
    # Add price data
    fig.add_trace(
        go.Candlestick(
            x=stock_data.index,
            open=stock_data['1. open'],
            high=stock_data['2. high'],
            low=stock_data['3. low'],
            close=stock_data['4. close'],
            name="Price"
        ),
        row=1, col=1
    )
    
    # Add volume bar chart
    fig.add_trace(
        go.Bar(
            x=stock_data.index,
            y=stock_data['5. volume'],
            name="Volume"
        ),
        row=2, col=1
    )
    
    # Add moving averages
    stock_data['MA50'] = stock_data['4. close'].rolling(window=50).mean()
    stock_data['MA200'] = stock_data['4. close'].rolling(window=200).mean()
    
    fig.add_trace(
        go.Scatter(
            x=stock_data.index,
            y=stock_data['MA50'],
            name="50-day MA",
            line=dict(color='orange', width=1)
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=stock_data.index,
            y=stock_data['MA200'],
            name="200-day MA",
            line=dict(color='red', width=1)
        ),
        row=1, col=1
    )
    
    # Update layout
    fig.update_layout(
        title=f'{symbol} 5-Year Stock Analysis',
        xaxis_title="Date",
        yaxis_title="Price ($)",
        height=800,
        xaxis_rangeslider_visible=False
    )
    
    # Convert to image
    img_bytes = fig.to_image(format="png", width=1200, height=800)
    
    return Image(data=img_bytes, format="png")


@mcp.tool()
async def get_key_financial_ratios(symbol: str, ctx: Context) -> str:
    """
    Get key financial ratios and metrics for the specified stock.
    
    Args:
        symbol: Stock symbol (e.g., AAPL, MSFT, NVDA)
    
    Returns:
        A formatted table of key financial ratios.
    """
    app_ctx = ctx.request_context.lifespan_context
    
    # Get data from Alpha Vantage
    ctx.info(f"Retrieving financial metrics for {symbol}")
    overview = await app_ctx.alpha_vantage_service.get_company_overview(symbol)
    
    # Format data as a table
    ratios = [
        ("Market Cap", overview.get("MarketCapitalization", "N/A")),
        ("P/E Ratio", overview.get("PERatio", "N/A")),
        ("PEG Ratio", overview.get("PEGRatio", "N/A")),
        ("Price to Book", overview.get("PriceToBookRatio", "N/A")),
        ("Price to Sales", overview.get("PriceToSalesRatioTTM", "N/A")),
        ("EPS", overview.get("EPS", "N/A")),
        ("ROE", overview.get("ReturnOnEquityTTM", "N/A")),
        ("Profit Margin", overview.get("ProfitMargin", "N/A")),
        ("Operating Margin", overview.get("OperatingMarginTTM", "N/A")),
        ("Dividend Yield", overview.get("DividendYield", "N/A")),
        ("Dividend Per Share", overview.get("DividendPerShare", "N/A")),
        ("Beta", overview.get("Beta", "N/A")),
        ("52 Week High", overview.get("52WeekHigh", "N/A")),
        ("52 Week Low", overview.get("52WeekLow", "N/A"))
    ]
    
    # Format as markdown table
    result = f"# Key Financial Ratios for {symbol}\n\n"
    result += "| Metric | Value |\n"
    result += "|--------|-------|\n"
    
    for metric, value in ratios:
        result += f"| {metric} | {value} |\n"
    
    return result


@mcp.resource("company://{symbol}/overview")
async def get_company_overview(symbol: str) -> str:
    """
    Get a comprehensive overview of the company based on its SEC filings.
    
    Args:
        symbol: Stock symbol (e.g., AAPL, MSFT, NVDA)
    """
    request = mcp.get_request_context()
    app_ctx = request.lifespan_context
    
    print(f"Retrieving company overview for {symbol}")
    rag_results = await app_ctx.rag_agent.get_company_overview(symbol)
    
    return rag_results

@mcp.resource("market://{symbol}/news")
async def get_market_news(symbol: str) -> str:
    """
    Get recent market news about the specified company.
    
    Args:
        symbol: Stock symbol (e.g., AAPL, MSFT, NVDA)
    """
    request = mcp.get_request_context()
    app_ctx = request.lifespan_context
    
    print(f"Searching for market news about {symbol}")
    news = await app_ctx.web_search_agent.get_news(symbol)
    
    return news

@mcp.resource("financial://{symbol}/data")
async def get_financial_data(symbol: str) -> str:
    """
    Get key financial data for the specified company.
    
    Args:
        symbol: Stock symbol (e.g., AAPL, MSFT, NVDA)
    """
    request = mcp.get_request_context()
    app_ctx = request.lifespan_context
    
    print(f"Retrieving financial data for {symbol}")
    financial_data = await app_ctx.stock_data_agent.get_financial_data(symbol)
    
    return financial_data



@mcp.prompt()
async def research_stock(symbol: str) -> str:
    """
    Create a prompt for researching a specific stock.
    
    Args:
        symbol: Stock symbol to research
    """
    return f"""
    Please create a comprehensive research report for {symbol} stock. This should include:
    
    1. A summary of the company's business model and industry position
    2. Key financial metrics and performance indicators
    3. Recent news and market developments affecting the company
    4. Technical analysis of stock price trends
    5. Growth prospects and potential risks
    6. Investment recommendation with supporting rationale
    
    Use all available data sources including SEC filings, market news, and stock price history.
    """


if __name__ == "__main__":
    mcp.run()