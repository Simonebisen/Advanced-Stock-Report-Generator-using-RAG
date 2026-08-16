import os
import time
import logging
import asyncio
from typing import Dict, List, Optional, Any

import google.generativeai as genai
from services.edgar_service import EdgarService
from services.pinecone_service import PineconeService

# 设置日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("stock_report_debug.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('stock_report')

class RAGAgent:
    """Agent for retrieving and processing SEC filings using RAG."""
    
    def __init__(self, edgar_service: EdgarService, pinecone_service: PineconeService, gemini_api_key: str):
        """
        Initialize the RAG agent.
        
        Args:
            edgar_service: Service for downloading SEC filings
            pinecone_service: Service for vector database operations
            gemini_api_key: API key for Google Gemini
        """
        logger.info("初始化RAGAgent")
        self.edgar_service = edgar_service
        self.pinecone_service = pinecone_service
        
        # 初始化缓存
        self.section_cache = {}
        self.cache_ttl = 3600  # 缓存有效期（秒）
        self.cache_timestamps = {}
        
        # Initialize Gemini
        logger.info("配置Gemini API")
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        logger.info("RAGAgent初始化完成")
    
    async def process_filings(self, symbol: str) -> Dict[str, str]:
        """
        Process SEC filings for a given stock symbol.
        
        Args:
            symbol: Stock symbol (e.g., AAPL, MSFT, NVDA)
            
        Returns:
            Dict containing different sections of analyzed filing data
        """
        start_time = time.time()
        logger.info(f"开始处理股票 {symbol} 的文件")
        
        try:
            # 下载文件
            download_start = time.time()
            logger.info(f"开始下载 {symbol} 的SEC文件")
            filings = await self.edgar_service.download_filings(symbol)
            logger.info(f"下载完成，共 {len(filings)} 个文件，耗时 {time.time() - download_start:.2f} 秒")
            
            # 处理和索引文件
            index_start = time.time()
            logger.info(f"开始处理和索引 {symbol} 的文件")
            await self.process_and_index_filings(symbol, filings)
            logger.info(f"处理和索引完成，耗时 {time.time() - index_start:.2f} 秒")
            
            # 生成报告
            report_start = time.time()
            logger.info("开始生成报告部分")
            result = await self.generate_report_sections(symbol)
            logger.info(f"报告生成完成，耗时 {time.time() - report_start:.2f} 秒")
            
            logger.info(f"整个过程完成，总耗时 {time.time() - start_time:.2f} 秒")
            return result
        except Exception as e:
            logger.error(f"处理过程中出错: {str(e)}", exc_info=True)
            raise
    
    async def process_and_index_filings(self, symbol: str, filings: List[str]) -> None:
        """
        Process XBRL filings and index them in Pinecone.
        
        Args:
            symbol: Stock symbol
            filings: List of filing paths
        """
        symbol = symbol.lower()
        start_time = time.time()
        logger.info(f"开始处理和索引 {symbol} 的文件，共 {len(filings)} 个文件")
        
        try:
            # 检查索引是否存在
            index_check_start = time.time()
            logger.info(f"检查索引 {symbol} 是否存在")
            index_exists = await self.pinecone_service.index_exists(symbol)
            logger.info(f"检查索引存在耗时: {time.time() - index_check_start:.2f} 秒，结果: {index_exists}")
            
            if not index_exists:
                # 创建索引
                index_create_start = time.time()
                logger.info(f"开始为 {symbol} 创建索引")
                await self.pinecone_service.create_index(symbol)
                logger.info(f"创建索引完成，耗时 {time.time() - index_create_start:.2f} 秒")
                
                # 处理文件并添加到索引中
                await self._process_and_add_filings(symbol, filings)
            else:
                # 检查索引是否为空
                index_empty_check_start = time.time()
                logger.info(f"检查索引 {symbol} 是否为空")
                is_empty = await self.pinecone_service.index_is_empty(symbol)
                logger.info(f"检查索引是否为空耗时: {time.time() - index_empty_check_start:.2f} 秒，结果: {is_empty}")
                
                if is_empty:
                    logger.info(f"索引 {symbol} 存在但为空，开始处理和添加文件")
                    await self._process_and_add_filings(symbol, filings)
                else:
                    logger.info(f"索引 {symbol} 已存在且包含数据，跳过创建和索引步骤")
            
            logger.info(f"处理和索引 {symbol} 的所有文件完成，总耗时 {time.time() - start_time:.2f} 秒")
        except Exception as e:
            logger.error(f"处理和索引文件过程中出错: {str(e)}", exc_info=True)
            raise
    
    async def _process_and_add_filings(self, symbol: str, filings: List[str]) -> None:
        """
        并行处理文件并添加到索引中
        
        Args:
            symbol: 股票代号
            filings: 文件路径列表
        """
        batch_size = 3  # 并行处理的文件数量
        logger.info(f"开始并行处理 {len(filings)} 个文件，批次大小: {batch_size}")
        
        # 处理每个批次的文件
        for i in range(0, len(filings), batch_size):
            batch = filings[i:i+batch_size]
            batch_end = min(i+batch_size, len(filings))
            batch_start_time = time.time()
            logger.info(f"处理文件批次 {i+1}-{batch_end} / {len(filings)}")
            
            # 创建批次处理任务
            async def process_file(file_path, file_index):
                file_start = time.time()
                logger.info(f"开始处理第 {file_index+1}/{len(filings)} 个文件: {file_path}")
                
                try:
                    # 转换文件
                    convert_start = time.time()
                    logger.info(f"开始将文件转换为文本")
                    text = await self.edgar_service.convert_filing_to_text(file_path)
                    logger.info(f"文件转换完成，耗时 {time.time() - convert_start:.2f} 秒，文本长度: {len(text)}")
                    
                    # 分块
                    chunk_start = time.time()
                    logger.info(f"开始将文本分块")
                    chunks = self._split_text_into_chunks(text)
                    logger.info(f"文本分块完成，耗时 {time.time() - chunk_start:.2f} 秒，共 {len(chunks)} 个块")
                    
                    # 添加文件元数据
                    for chunk in chunks:
                        chunk["metadata"]["file_path"] = file_path
                        chunk["metadata"]["file_index"] = file_index
                    
                    logger.info(f"处理第 {file_index+1} 个文件完成，总耗时 {time.time() - file_start:.2f} 秒")
                    return chunks
                except Exception as e:
                    logger.error(f"处理文件 {file_path} 时出错: {str(e)}", exc_info=True)
                    return []
            
            # 并行处理当前批次
            tasks = [process_file(filing, i+j) for j, filing in enumerate(batch)]
            batch_results = await asyncio.gather(*tasks)
            
            # 合并所有块
            all_chunks = []
            for chunks in batch_results:
                all_chunks.extend(chunks)
            
            # 索引合并后的块
            if all_chunks:
                index_docs_start = time.time()
                logger.info(f"开始索引文档块，共 {len(all_chunks)} 个块")
                await self.pinecone_service.index_documents(symbol, all_chunks)
                logger.info(f"索引文档块完成，耗时 {time.time() - index_docs_start:.2f} 秒")
            
            logger.info(f"批次 {i+1}-{batch_end} 处理完成，总耗时 {time.time() - batch_start_time:.2f} 秒")
    
    def _split_text_into_chunks(self, text: str, min_chunk_size: int = 500, max_chunk_size: int = 8000) -> List[Dict[str, Any]]:
        """
        使用更智能的文本分块策略
        
        Args:
            text: 要分割的文本
            min_chunk_size: 最小块大小
            max_chunk_size: 最大块大小
                
        Returns:
            文档块列表
        """
        start_time = time.time()
        logger.info(f"开始智能分块，文本长度: {len(text)}")
        
        chunks = []
        current_pos = 0
        chunk_id = 0
        
        while current_pos < len(text):
            # 确定潜在的结束位置
            end_pos = min(current_pos + max_chunk_size, len(text))
            
            # 如果没有达到文本末尾，尝试在句子或段落边界处分割
            if end_pos < len(text):
                # 尝试在段落边界处分割
                paragraph_end = text.rfind('\n\n', current_pos, end_pos)
                
                # 尝试在句子边界处分割
                sentence_end = text.rfind('. ', current_pos, end_pos)
                
                # 如果找到合适的边界且长度不小于最小块大小
                if paragraph_end > current_pos + min_chunk_size:
                    end_pos = paragraph_end + 2  # 包含换行符
                elif sentence_end > current_pos + min_chunk_size:
                    end_pos = sentence_end + 2  # 包含句号和空格
            
            # 提取当前块文本
            chunk_text = text[current_pos:end_pos].strip()
            
            # 只添加非空块
            if chunk_text:
                chunks.append({
                    "id": f"chunk_{chunk_id}",
                    "text": chunk_text,
                    "metadata": {
                        "chunk_id": chunk_id,
                        "source": "sec_filing",
                        "start_pos": current_pos,
                        "end_pos": end_pos,
                        "text": chunk_text
                    }
                })
                chunk_id += 1
            
            current_pos = end_pos
        
        logger.info(f"智能分块完成，生成了 {len(chunks)} 个块，耗时 {time.time() - start_time:.2f} 秒")
        return chunks
    
    async def generate_report_sections(self, symbol: str) -> Dict[str, str]:
        """
        Generate different sections of the report using RAG.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dict with different report sections
        """
        symbol = symbol.lower()
        start_time = time.time()
        logger.info(f"开始为 {symbol} 生成报告部分")
        
        try:
            # 定义要生成的部分及其优先级
            section_queries = {
                "summary": {
                    "query": "Provide a concise executive summary of the company.",
                    "priority": 1
                },
                "company_overview": {
                    "query": "Describe the company's business model, products, and market position.",
                    "priority": 2
                },
                "industry_analysis": {
                    "query": "Analyze the current state, size, growth trends, and major players in the company's industry.",
                    "priority": 3
                },
                "competitive_position": {
                    "query": "Analyze the company's competitive position, market share, and competitive advantages in the industry.",
                    "priority": 4
                },
                "revenue_analysis": {
                    "query": "Analyze the company's main business revenue composition, growth trends, and performance across business lines.",
                    "priority": 5
                },
                "risk_assessment": {
                    "query": "Identify and analyze key risks mentioned in the company's SEC filings.",
                    "priority": 6
                },
                "detailed_financials": {
                    "query": "Provide a detailed analysis of income statement, balance sheet, and cash flow statement.",
                    "priority": 7
                }
            }
            
            # 按优先级顺序生成部分
            sections = {}
            
            # 创建并发任务
            tasks = []
            for section_name, section_info in sorted(section_queries.items(), key=lambda x: x[1]["priority"]):
                tasks.append(self._generate_section(symbol, section_name, section_info["query"]))
            
            # 并发执行所有部分生成
            results = await asyncio.gather(*tasks)
            
            # 组织结果
            for i, (section_name, _) in enumerate(sorted(section_queries.items(), key=lambda x: x[1]["priority"])):
                sections[section_name] = results[i]
            
            logger.info(f"所有报告部分生成完成，总耗时 {time.time() - start_time:.2f} 秒")
            return sections
        except Exception as e:
            logger.error(f"生成报告部分时出错: {str(e)}", exc_info=True)
            raise
    
    async def _generate_section(self, symbol: str, section_name: str, query: str) -> str:
        """
        Generate a specific section of the report with caching and retries.
        
        Args:
            symbol: Stock symbol
            section_name: Name of the section
            query: Query to run against the RAG system
            
        Returns:
            Generated text for the section
        """
        symbol = symbol.lower()
        start_time = time.time()
        logger.info(f"开始为 {symbol} 生成报告部分 '{section_name}'，查询: {query}")
        
        # 检查缓存
        cache_key = f"{symbol}_{section_name}"
        current_time = time.time()
        if cache_key in self.section_cache:
            timestamp = self.cache_timestamps.get(cache_key, 0)
            if current_time - timestamp < self.cache_ttl:
                logger.info(f"使用缓存生成结果，股票: {symbol}, 部分: '{section_name}'")
                return self.section_cache[cache_key]
        
        try:
            # 查询Pinecone
            query_start = time.time()
            logger.info(f"开始查询Pinecone索引")
            relevant_chunks = await self.pinecone_service.query(symbol, query, limit=8)  # 增加查询结果数量以获取更多上下文
            logger.info(f"Pinecone查询完成，返回 {len(relevant_chunks)} 个结果，耗时 {time.time() - query_start:.2f} 秒")
            
            # 如果没有结果，返回提示信息
            if not relevant_chunks:
                no_data_msg = f"无足够数据生成 {section_name} 部分。请确保已经索引了相关文件。"
                logger.warning(f"查询 '{section_name}' 没有返回结果")
                return no_data_msg
            
            # 排序结果并选择最相关的
            sorted_chunks = sorted(relevant_chunks, key=lambda x: x.get("score", 0), reverse=True)
            top_chunks = sorted_chunks[:5]  # 只使用最相关的5个块
            
            # 合并上下文，同时去除重复内容
            used_text = set()
            unique_contexts = []
            
            for chunk in top_chunks:
                text = chunk.get("text", "").strip()
                # 使用文本的前50个字符作为去重标识
                text_id = text[:min(50, len(text))]
                if text and text_id not in used_text:
                    unique_contexts.append(text)
                    used_text.add(text_id)
            
            context = "\n\n".join(unique_contexts)
            logger.info(f"合并上下文完成，去重后上下文数量: {len(unique_contexts)}，总长度: {len(context)}")
            
            # 生成响应
            generate_start = time.time()
            logger.info(f"开始使用Gemini生成内容")
            
            # 针对不同部分定制提示词
            section_specific_instructions = {
                "summary": "Focus on the most important high-level information about the company.",
                "company_overview": "Include details about business segments, product lines, and geographic markets.",
                "industry_analysis": "Analyze market trends, industry size, and growth projections.",
                "competitive_position": "Identify key competitors and the company's competitive advantages.",
                "revenue_analysis": "Break down revenue streams and analyze trends over recent periods.",
                "risk_assessment": "Prioritize the most significant risks facing the company.",
                "detailed_financials": "Provide numerical analysis with year-over-year comparisons."
            }
            
            specific_instruction = section_specific_instructions.get(section_name, "")
            
            prompt = f"""
            Based on the following information from SEC filings for {symbol.upper()}:
            
            {context}
            
            {query}
            
            {specific_instruction}
            
            Provide a detailed, well-structured response focusing only on factual information from the filings.
            Structure your response in a clear, professional format suitable for a financial report.
            Ensure all information is accurate and directly supported by the provided context.
            If the information is insufficient to fully address any aspect, acknowledge this limitation.
            """
            
            # 添加重试机制
            max_retries = 3
            retry_count = 0
            last_error = None
            
            while retry_count < max_retries:
                try:
                    # 使用不同的温度设置
                    generation_config = {
                        "temperature": 0.1,  # 低温度以获得更事实性的回答
                        "top_p": 0.95,
                        "top_k": 40,
                        "max_output_tokens": 4096,
                    }
                    
                    response = self.model.generate_content(
                        prompt, 
                        generation_config=generation_config
                    )
                    
                    section_content = response.text
                    
                    # 更新缓存
                    self.section_cache[cache_key] = section_content
                    self.cache_timestamps[cache_key] = time.time()
                    self._cleanup_cache()
                    
                    logger.info(f"'{section_name}' 部分生成完成，耗时 {time.time() - generate_start:.2f} 秒，内容长度: {len(section_content)}")
                    logger.info(f"总耗时 {time.time() - start_time:.2f} 秒")
                    return section_content
                    
                except Exception as e:
                    retry_count += 1
                    last_error = e
                    wait_time = 2 ** retry_count  # 指数退避
                    logger.warning(f"Gemini生成内容失败 (尝试 {retry_count}/{max_retries}): {str(e)}")
                    
                    if retry_count < max_retries:
                        logger.warning(f"等待 {wait_time} 秒后重试...")
                        await asyncio.sleep(wait_time)
            
            # 如果所有重试都失败，抛出最后一个错误
            logger.error(f"生成内容失败，已达到最大重试次数: {max_retries}")
            raise last_error
                
        except Exception as e:
            logger.error(f"生成报告部分 '{section_name}' 时出错: {str(e)}", exc_info=True)
            error_msg = f"Error generating {section_name} section: {str(e)}"
            return error_msg
    
    def _cleanup_cache(self):
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = []
        
        for key, timestamp in self.cache_timestamps.items():
            if current_time - timestamp > self.cache_ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            if key in self.section_cache:
                del self.section_cache[key]
            if key in self.cache_timestamps:
                del self.cache_timestamps[key]
        
        if expired_keys:
            logger.info(f"清理了 {len(expired_keys)} 个过期缓存项")
    
    async def get_company_overview(self, symbol: str) -> str:
        """
        Get a comprehensive overview of the company.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Company overview text
        """
        logger.info(f"获取公司概览: {symbol}")
        start_time = time.time()
        
        try:
            result = await self._generate_section(
                symbol, 
                "company_overview", 
                "Provide a comprehensive overview of the company, including its business model, products/services, market position, competitive advantages, and recent developments."
            )
            logger.info(f"公司概览生成完成，耗时 {time.time() - start_time:.2f} 秒")
            return result
        except Exception as e:
            logger.error(f"获取公司概览时出错: {str(e)}", exc_info=True)
            return f"Error generating company overview: {str(e)}"
    
    async def get_risk_assessment(self, symbol: str) -> str:
        """
        获取公司风险评估
        
        Args:
            symbol: 股票代号
            
        Returns:
            风险评估文本
        """
        logger.info(f"获取风险评估: {symbol}")
        start_time = time.time()
        
        try:
            result = await self._generate_section(
                symbol,
                "risk_assessment",
                "Provide a detailed assessment of all risks mentioned in the company's SEC filings, including operational, financial, market, regulatory, and other risk factors."
            )
            logger.info(f"风险评估生成完成，耗时 {time.time() - start_time:.2f} 秒")
            return result
        except Exception as e:
            logger.error(f"获取风险评估时出错: {str(e)}", exc_info=True)
            return f"Error generating risk assessment: {str(e)}"
    
    async def get_financial_analysis(self, symbol: str) -> str:
        """
        获取财务分析
        
        Args:
            symbol: 股票代号
            
        Returns:
            财务分析文本
        """
        logger.info(f"获取财务分析: {symbol}")
        start_time = time.time()
        
        try:
            result = await self._generate_section(
                symbol,
                "financial_analysis",
                "Analyze the company's financial performance including income statement, balance sheet, and cash flow trends. Include key financial ratios, year-over-year comparisons, and highlight any significant changes."
            )
            logger.info(f"财务分析生成完成，耗时 {time.time() - start_time:.2f} 秒")
            return result
        except Exception as e:
            logger.error(f"获取财务分析时出错: {str(e)}", exc_info=True)
            return f"Error generating financial analysis: {str(e)}"
    
    async def generate_full_report(self, symbol: str) -> Dict[str, str]:
        """
        生成完整的股票分析报告
        
        Args:
            symbol: 股票代号
            
        Returns:
            包含所有报告部分的字典
        """
        logger.info(f"开始生成 {symbol} 的完整报告")
        start_time = time.time()
        
        try:
            # 首先确保索引存在并包含数据
            await self.process_filings(symbol)
            
            # 生成各个部分
            logger.info("开始生成各报告部分")
            sections = await self.generate_report_sections(symbol)
            
            # 添加报告元数据
            sections["metadata"] = {
                "symbol": symbol.upper(),
                "generation_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "data_sources": "SEC Filings (10-K, 10-Q)",
                "version": "1.0"
            }
            
            logger.info(f"完整报告生成完成，总耗时 {time.time() - start_time:.2f} 秒")
            return sections
        except Exception as e:
            logger.error(f"生成完整报告时出错: {str(e)}", exc_info=True)
            return {"error": f"Error generating full report: {str(e)}"}
            
# 示例用法
if __name__ == "__main__":
    # 配置从环境变量加载
    google_api_key = os.environ.get("GOOGLE_API_KEY", "")
    pinecone_api_key = os.environ.get("PINECONE_API_KEY", "")
    
    # 创建服务
    edgar_service = EdgarService()
    pinecone_service = PineconeService(api_key=pinecone_api_key)
    
    # 创建RAG代理
    agent = RAGAgent(edgar_service, pinecone_service, google_api_key)
    
    # 运行报告生成（示例）
    symbol = "AAPL"
    
    async def run_example():
        report = await agent.generate_full_report(symbol)
        print(f"生成的报告部分: {list(report.keys())}")
        print(f"摘要部分:\n{report.get('summary', '未生成')[:500]}...")
    
    # 运行示例
    asyncio.run(run_example())