import os
import re
import aiofiles
import logging
from typing import Dict, List, Optional, Any
import asyncio
from sec_edgar_downloader import Downloader

from agents.utils import extract_text_from_filing

# 配置日志
logger = logging.getLogger(__name__)

class EdgarService:
    """Service for downloading and processing SEC EDGAR filings."""
    
    def __init__(self, name: str, email: str, output_dir: str = "./"):
        """
        Initialize the SEC EDGAR service.
        
        Args:
            name: Requester name for SEC EDGAR
            email: Requester email for SEC EDGAR
            output_dir: Directory to store downloaded filings
        """
        self.name = name
        self.email = email
        self.output_dir = output_dir
        self.downloader = Downloader(name, email, output_dir)
    
    async def download_filings(self, symbol: str, form_type: str = "10-K", years: int = 5) -> List[str]:
        """
        Download SEC filings for a given stock symbol.
        
        Args:
            symbol: Stock symbol (e.g., AAPL, MSFT, NVDA)
            form_type: SEC form type (default: 10-K)
            years: Number of years of filings to download
            
        Returns:
            List of paths to downloaded filings
        """
        logger.info(f"开始下载 {symbol} 的 {form_type} 文件")
        # Convert to a coroutine
        return await asyncio.to_thread(self._sync_download_filings, symbol, form_type, years)
    
    def _sync_download_filings(self, symbol: str, form_type: str, years: int) -> List[str]:
        """
        Synchronous version of download_filings.
        
        Args:
            symbol: Stock symbol
            form_type: SEC form type
            years: Number of years
            
        Returns:
            List of filing paths
        """
        # Check if files already exist
        sec_dir = os.path.join(self.output_dir, "sec-edgar-filings", symbol, form_type)
        if os.path.exists(sec_dir):
            # Count existing filings
            existing_filings = [os.path.join(sec_dir, d) for d in os.listdir(sec_dir) if os.path.isdir(os.path.join(sec_dir, d))]
            if len(existing_filings) >= years:
                logger.info(f"已找到 {len(existing_filings)} 个现有的 {form_type} 文件，无需下载")
                filing_paths = self._get_filing_paths(existing_filings)
                logger.info(f"从现有文件中找到了 {len(filing_paths)} 个文档")
                
                # 如果没有找到文件，尝试强制重新下载
                if len(filing_paths) == 0:
                    logger.warning(f"尽管找到了 {len(existing_filings)} 个目录，但未找到任何文件。尝试重新下载...")
                    return self._force_download_filings(symbol, form_type)
                
                return filing_paths
        
        # Download filings
        return self._force_download_filings(symbol, form_type)
    
    def _force_download_filings(self, symbol: str, form_type: str) -> List[str]:
        """强制下载文件"""
        try:
            logger.info(f"开始从 SEC EDGAR 下载 {symbol} 的 {form_type} 文件")
            
            # 确保文件夹存在
            sec_dir = os.path.join(self.output_dir, "sec-edgar-filings", symbol, form_type)
            os.makedirs(os.path.dirname(sec_dir), exist_ok=True)
            
            # 使用原有的日期参数方式下载
            self.downloader.get(form_type, symbol, after="2020-01-01", download_details=True)
            
            # 检查下载结果
            filing_dirs = []
            if os.path.exists(sec_dir):
                filing_dirs = [os.path.join(sec_dir, d) for d in os.listdir(sec_dir) if os.path.isdir(os.path.join(sec_dir, d))]
                logger.info(f"成功下载了 {len(filing_dirs)} 个 {form_type} 文件目录")
            else:
                logger.warning(f"警告：下载后未找到 {sec_dir} 目录")
            
            filing_paths = self._get_filing_paths(filing_dirs)
            logger.info(f"从下载的文件中找到了 {len(filing_paths)} 个文档")
            return filing_paths
                
        except Exception as e:
            logger.error(f"下载 SEC 文件时出错: {str(e)}")
            return []
    
    def _check_if_xbrl_content(self, file_path: str) -> bool:
        """
        检查文件内容是否是 XBRL 格式
        
        Args:
            file_path: 文件路径
            
        Returns:
            布尔值，表示是否是 XBRL 格式
        """
        try:
            # 只读取文件的前 1000 个字符来检查
            with open(file_path, 'r', errors='ignore') as f:
                content = f.read(1000)
                
            # 检查 XBRL 相关标记
            if ('<xbrl' in content.lower() or 
                '<html' in content.lower() or
                '<?xml' in content.lower() or
                '<sec-document' in content.lower() or
                '<document' in content.lower()):
                logger.debug(f"文件 {file_path} 包含 XBRL/XML/HTML 标记")
                return True
                
            return False
        except Exception as e:
            logger.error(f"检查文件 {file_path} 是否是 XBRL 格式时出错: {str(e)}")
            # 出错时假设不是 XBRL 格式
            return False
    
    def _get_filing_paths(self, filing_dirs: List[str]) -> List[str]:
        """
        Get paths to filing documents from filing directories.
        
        Args:
            filing_dirs: List of filing directory paths
            
        Returns:
            List of filing document paths
        """
        filing_paths = []
        
        # 常见的 SEC 文件扩展名
        standard_extensions = ('.htm', '.html', '.xml', '.xbrl')
        # 需要检查内容的扩展名
        check_content_extensions = ('.txt', '.doc', '.docx', '.pdf')
        
        for dir_path in filing_dirs:
            try:
                files_in_dir = 0
                logger.debug(f"检查目录 {dir_path} 的内容")
                
                # 收集目录中的所有文件
                all_files = []
                for root, _, files in os.walk(dir_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        all_files.append((root, file, file_path))
                
                if not all_files:
                    logger.warning(f"目录 {dir_path} 中没有找到任何文件")
                    continue
                
                # 记录所有找到的文件
                logger.debug(f"目录 {dir_path} 中找到 {len(all_files)} 个文件")
                
                # 第一步：找标准格式的文件
                standard_files = []
                for root, file, file_path in all_files:
                    if file.endswith(standard_extensions):
                        standard_files.append((root, file, file_path))
                
                if standard_files:
                    logger.info(f"在目录 {dir_path} 中找到 {len(standard_files)} 个标准格式文件")
                    for root, file, file_path in standard_files:
                        filing_paths.append(file_path)
                        files_in_dir += 1
                        logger.debug(f"添加标准格式文件: {file_path}")
                
                # 第二步：如果没有标准格式，检查文本文件是否包含 XBRL 内容
                if files_in_dir == 0:
                    logger.info(f"在目录 {dir_path} 中未找到标准格式文件，检查其他文件内容")
                    for root, file, file_path in all_files:
                        if file.endswith(check_content_extensions):
                            # 检查文件内容是否是 XBRL 格式
                            if self._check_if_xbrl_content(file_path):
                                filing_paths.append(file_path)
                                files_in_dir += 1
                                logger.info(f"添加包含 XBRL 内容的文件: {file_path}")
                
                # 第三步：如果仍然没有找到，添加任何 .txt 文件
                if files_in_dir == 0:
                    for root, file, file_path in all_files:
                        if file.endswith('.txt'):
                            filing_paths.append(file_path)
                            files_in_dir += 1
                            logger.info(f"添加 TXT 文件: {file_path}")
                            break  # 只添加第一个找到的
                
                # 最后步骤：如果仍然没有找到，添加第一个文件
                if files_in_dir == 0 and all_files:
                    root, file, file_path = all_files[0]
                    filing_paths.append(file_path)
                    files_in_dir += 1
                    logger.info(f"添加第一个可用文件: {file_path}")
                
                logger.info(f"在目录 {dir_path} 中找到了 {files_in_dir} 个有用文件")
                
            except Exception as e:
                logger.error(f"处理文件目录 {dir_path} 时出错: {str(e)}")
        
        logger.info(f"总共找到了 {len(filing_paths)} 个文件文档")
        
        # 如果没有找到任何文件，记录更详细的警告
        if len(filing_paths) == 0:
            logger.warning(f"警告：未找到任何文件文档。请检查下载是否成功，以及文件格式是否符合预期。")
        
        return filing_paths
    
    async def convert_filing_to_text(self, filing_path: str) -> str:
        """
        Convert a filing to plain text.
        
        Args:
            filing_path: Path to filing file
            
        Returns:
            Plain text extracted from filing
        """
        try:
            # Convert to a coroutine
            text = await asyncio.to_thread(extract_text_from_filing, filing_path)
            logger.info(f"成功从 {os.path.basename(filing_path)} 提取文本，长度: {len(text)} 字符")
            
            if not text or len(text.strip()) == 0:
                logger.warning(f"警告：从 {os.path.basename(filing_path)} 提取的文本为空")
            
            return text
        except Exception as e:
            logger.error(f"从 {filing_path} 提取文本时出错: {str(e)}")
            return ""