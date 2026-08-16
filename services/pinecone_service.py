import os
import time
import logging
import asyncio
from typing import Dict, List, Optional, Any
import numpy as np
import google.generativeai as genai
from pinecone import Pinecone, ServerlessSpec

# 配置日志
logger = logging.getLogger(__name__)

# 设置类
class Settings:
    def __init__(self, google_api_key: str, pinecone_api_key: str):
        self.GOOGLE_API_KEY = google_api_key
        self.PINECONE_API_KEY = pinecone_api_key

# 从环境变量获取API密钥
settings = Settings(
    google_api_key=os.environ.get("GOOGLE_API_KEY", ""),
    pinecone_api_key=os.environ.get("PINECONE_API_KEY", "")
)

class PineconeService:
    """Service for interacting with Pinecone vector database."""
    
    def __init__(self, api_key: str, environment: str = "gcp-starter"):
        """
        Initialize the Pinecone service.
        
        Args:
            api_key: Pinecone API key
            environment: Pinecone environment
        """
        self.api_key = api_key
        self.environment = environment
        self.initialized = False
        self.pc = None
        self.query_cache = {}  # 用于缓存查询结果
        self.cache_ttl = 300  # 缓存有效期（秒）
        self.cache_timestamps = {}  # 缓存时间戳
        self._initialize()
    
    async def _initialize(self) -> None:
        """Initialize the Pinecone client with retry mechanism."""
        if not self.initialized:
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    # 使用新的API初始化
                    self.pc = Pinecone(api_key=self.api_key)
                    self.initialized = True
                    logger.info("Pinecone客户端初始化成功")
                    break
                except Exception as e:
                    retry_count += 1
                    wait_time = 2 ** retry_count  # 指数退避
                    logger.warning(f"Pinecone初始化失败 (尝试 {retry_count}/{max_retries}): {str(e)}")
                    logger.warning(f"等待 {wait_time} 秒后重试...")
                    await asyncio.sleep(wait_time)
            
            if not self.initialized:
                logger.error(f"Pinecone初始化失败，已达到最大重试次数: {max_retries}")
                raise Exception("无法连接到Pinecone服务")
    
    async def index_exists(self, index_name: str) -> bool:
        """
        Check if an index exists in Pinecone.
        
        Args:
            index_name: Name of the index
            
        Returns:
            True if index exists, False otherwise
        """
        try:
            await self._initialize()
            index_list = self.pc.list_indexes().names()
            exists = index_name in index_list
            logger.info(f"索引列表: {index_list}")
            logger.info(f"索引 {index_name} 存在: {exists}")
            return exists
        except Exception as e:
            logger.error(f"检查索引存在时出错: {str(e)}")
            return False
    
    async def get_index_stats(self, index_name: str) -> Dict:
        """
        Get statistics for an index.
        
        Args:
            index_name: Name of the index
            
        Returns:
            Dict with index statistics
        """
        try:
            await self._initialize()
            if not await self.index_exists(index_name):
                logger.warning(f"索引 {index_name} 不存在，无法获取统计信息")
                return {}
            
            index = self.pc.Index(index_name)
            stats = index.describe_index_stats()
            logger.info(f"索引 {index_name} 统计信息: {stats}")
            return stats
        except Exception as e:
            logger.error(f"获取索引统计信息出错: {str(e)}")
            return {}
    
    async def index_is_empty(self, index_name: str) -> bool:
        """
        Check if an index is empty (has no vectors).
        
        Args:
            index_name: Name of the index
            
        Returns:
            True if index is empty, False otherwise
        """
        try:
            stats = await self.get_index_stats(index_name)
            vector_count = stats.get("total_vector_count", 0)
            is_empty = vector_count == 0
            logger.info(f"索引 {index_name} 是否为空: {is_empty} (包含 {vector_count} 个向量)")
            return is_empty
        except Exception as e:
            logger.error(f"检查索引是否为空时出错: {str(e)}")
            return True  # 如果出错，假设为空以确保安全
    
    async def create_index(self, index_name: str, dimension: int = 768) -> None:
        """
        Create a new index in Pinecone.
        
        Args:
            index_name: Name of the index
            dimension: Dimension of the embeddings
        """
        try:
            await self._initialize()
            
            if not await self.index_exists(index_name):
                logger.info(f"创建新索引 {index_name}")
                
                # 添加重试机制
                max_retries = 3
                retry_count = 0
                
                while retry_count < max_retries:
                    try:
                        self.pc.create_index(
                            name=index_name,
                            dimension=dimension,
                            metric="cosine",
                            spec=ServerlessSpec(
                                cloud="aws",
                                region="us-east-1"
                            )
                        )
                        logger.info(f"索引 {index_name} 创建成功")
                        break
                    except Exception as e:
                        retry_count += 1
                        wait_time = 2 ** retry_count  # 指数退避
                        logger.warning(f"创建索引失败 (尝试 {retry_count}/{max_retries}): {str(e)}")
                        
                        if retry_count < max_retries:
                            logger.warning(f"等待 {wait_time} 秒后重试...")
                            await asyncio.sleep(wait_time)
                        else:
                            logger.error(f"创建索引失败，已达到最大重试次数")
                            raise
            else:
                logger.info(f"索引 {index_name} 已存在，跳过创建")
        except Exception as e:
            logger.error(f"创建索引时出错: {str(e)}")
            raise
    
    async def index_documents(self, index_name: str, documents: List[Dict[str, Any]]) -> None:
        """
        Index documents in Pinecone.
        
        Args:
            index_name: Name of the index
            documents: List of documents with text and metadata
        """
        try:
            await self._initialize()
            
            # 检查索引是否存在，如果不存在则创建
            if not await self.index_exists(index_name):
                # 确定嵌入维度
                test_embedding = await self._generate_embeddings(["test"])
                dimension = len(test_embedding[0])
                logger.info(f"将使用嵌入维度: {dimension}")
                
                await self.create_index(index_name, dimension)
            
            index = self.pc.Index(index_name)
            
            # 处理文档批次，优化批处理大小
            batch_size = 50  # 调整批处理大小以提高性能
            total_vectors = 0
            
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i+batch_size]
                batch_end = min(i+batch_size, len(documents))
                logger.info(f"处理文档批次 {i+1}-{batch_end} / {len(documents)}")
                
                # 生成嵌入，使用优化的嵌入生成方法
                text_batch = [doc["text"] for doc in batch]
                logger.info(f"生成 {len(text_batch)} 个文档的嵌入")
                embeddings = await self._generate_embeddings(text_batch)
                
                # 检查嵌入是否有效
                valid_vectors = 0
                vectors = []
                
                for j, embedding in enumerate(embeddings):
                    is_zeros = np.allclose(embedding, np.zeros_like(embedding), atol=1e-6)
                    if not is_zeros:
                        valid_vectors += 1
                        vectors.append({
                            "id": batch[j].get("id", f"doc_{i+j}"),
                            "values": embedding,
                            "metadata": batch[j].get("metadata", {})
                        })
                    else:
                        logger.warning(f"文档 {i+j} 生成了全零嵌入，跳过")
                
                # 只有在有有效向量时才上传
                if vectors:
                    # 添加重试机制
                    max_retries = 3
                    retry_count = 0
                    
                    while retry_count < max_retries:
                        try:
                            logger.info(f"上传 {len(vectors)} 个向量到索引 {index_name}")
                            index.upsert(vectors=vectors)
                            total_vectors += len(vectors)
                            logger.info(f"批次向量上传成功，有效向量: {valid_vectors}/{len(batch)}")
                            break
                        except Exception as e:
                            retry_count += 1
                            wait_time = 2 ** retry_count  # 指数退避
                            logger.warning(f"上传向量失败 (尝试 {retry_count}/{max_retries}): {str(e)}")
                            
                            if retry_count < max_retries:
                                logger.warning(f"等待 {wait_time} 秒后重试...")
                                await asyncio.sleep(wait_time)
                            else:
                                logger.error(f"上传向量失败，已达到最大重试次数")
                                raise
                else:
                    logger.warning(f"批次中没有有效向量，跳过上传")
            
            # 验证索引状态
            await asyncio.sleep(2)  # 等待索引更新
            stats = await self.get_index_stats(index_name)
            logger.info(f"索引完成，上传了 {total_vectors} 个向量，索引统计: {stats}")
            
        except Exception as e:
            logger.error(f"索引文档时出错: {str(e)}")
            raise
    
    async def query(self, index_name: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Query the Pinecone index for similar documents.
        
        Args:
            index_name: Name of the index
            query: Query string
            limit: Maximum number of results
            
        Returns:
            List of similar documents with text and metadata
        """
        try:
            await self._initialize()
            
            # 生成缓存键
            cache_key = f"{index_name}_{query}_{limit}"
            
            # 检查缓存
            current_time = time.time()
            if cache_key in self.query_cache:
                timestamp = self.cache_timestamps.get(cache_key, 0)
                if current_time - timestamp < self.cache_ttl:
                    logger.info(f"使用缓存结果，查询: '{query}'")
                    return self.query_cache[cache_key]
            
            if not await self.index_exists(index_name):
                logger.warning(f"索引 {index_name} 不存在，无法查询")
                return []
            
            # 检查索引是否为空
            if await self.index_is_empty(index_name):
                logger.warning(f"索引 {index_name} 为空（没有向量），查询将返回空结果")
                return []
            
            index = self.pc.Index(index_name)
            
            # 生成查询嵌入
            logger.info(f"生成查询嵌入: '{query}'")
            query_embedding = await self._generate_embeddings([query])
            
            # 检查嵌入是否有效
            is_zeros = np.allclose(query_embedding[0], np.zeros_like(query_embedding[0]), atol=1e-6)
            if is_zeros:
                logger.error(f"查询嵌入为全零向量，无法执行有效查询")
                return []
                
            logger.info(f"查询嵌入维度: {len(query_embedding[0])}")
            
            # 添加重试机制
            max_retries = 3
            retry_count = 0
            last_error = None
            
            while retry_count < max_retries:
                try:
                    # 查询Pinecone
                    logger.info(f"查询索引 {index_name}")
                    results = index.query(
                        vector=query_embedding[0],
                        top_k=limit,
                        include_metadata=True
                    )
                    
                    # 格式化结果
                    formatted_results = []
                    for match in results.get("matches", []):
                        formatted_results.append({
                            "id": match.get("id", ""),
                            "score": match.get("score", 0),
                            "metadata": match.get("metadata", {}),
                            "text": match.get("metadata", {}).get("text", "")
                        })
                    
                    logger.info(f"查询返回 {len(formatted_results)} 个结果")
                    
                    # 更新缓存
                    self.query_cache[cache_key] = formatted_results
                    self.cache_timestamps[cache_key] = current_time
                    
                    # 清理过期缓存
                    self._cleanup_cache()
                    
                    return formatted_results
                    
                except Exception as e:
                    retry_count += 1
                    last_error = e
                    wait_time = 2 ** retry_count  # 指数退避
                    logger.warning(f"查询索引失败 (尝试 {retry_count}/{max_retries}): {str(e)}")
                    
                    if retry_count < max_retries:
                        logger.warning(f"等待 {wait_time} 秒后重试...")
                        await asyncio.sleep(wait_time)
            
            # 如果所有重试都失败，抛出最后一个错误
            logger.error(f"查询索引失败，已达到最大重试次数: {max_retries}")
            raise last_error
            
        except Exception as e:
            logger.error(f"查询索引时出错: {str(e)}")
            return []
    
    def _cleanup_cache(self):
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = []
        
        for key, timestamp in self.cache_timestamps.items():
            if current_time - timestamp > self.cache_ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            if key in self.query_cache:
                del self.query_cache[key]
            if key in self.cache_timestamps:
                del self.cache_timestamps[key]
                
        if expired_keys:
            logger.info(f"清理了 {len(expired_keys)} 个过期缓存项")
    
    async def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        使用批量处理优化嵌入生成
        
        Args:
            texts: 要生成嵌入的文本列表
            
        Returns:
            嵌入向量列表
        """
        try:
            # 配置 API 密钥
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            
            if not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY == "your_default_api_key":
                logger.error("GOOGLE_API_KEY 未设置或使用默认值")
                raise ValueError("GOOGLE_API_KEY 未设置")
            
            logger.info(f"生成 {len(texts)} 个文本的嵌入")
            
            # 批量处理，使用异步协程并发处理
            batch_size = 20  # 调整批处理大小
            all_embeddings = []
            
            # 实现批量处理
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i+batch_size]
                batch_results = []
                
                # 添加重试机制
                for text in batch:
                    max_retries = 3
                    retry_count = 0
                    last_error = None
                    
                    while retry_count < max_retries:
                        try:
                            task_type = "retrieval_document" if len(text) > 50 else "retrieval_query"
                            result = genai.embed_content(
                                model="models/embedding-001",
                                content=text,
                                task_type=task_type
                            )
                            batch_results.append(result['embedding'])
                            break
                        except Exception as e:
                            retry_count += 1
                            last_error = e
                            wait_time = retry_count * 2  # 线性退避
                            logger.warning(f"生成嵌入失败 (尝试 {retry_count}/{max_retries}): {str(e)}")
                            
                            if retry_count < max_retries:
                                logger.warning(f"等待 {wait_time} 秒后重试...")
                                await asyncio.sleep(wait_time)
                    
                    # 如果所有重试都失败，使用零向量
                    if retry_count == max_retries:
                        logger.error(f"生成嵌入失败，使用零向量代替")
                        batch_results.append([0.0] * 768
                                             )
                
                all_embeddings.extend(batch_results)
                logger.info(f"处理了批次 {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}，当前总计 {len(all_embeddings)}/{len(texts)} 个嵌入")
            
            return all_embeddings
                
        except Exception as e:
            logger.error(f"生成嵌入时出错: {str(e)}")
            # 返回空向量
            logger.warning("返回空向量作为备用")
            return [[0.0] * 768 for _ in range(len(texts))]

async def process_and_index_files(index_name: str, file_paths: List[str]) -> None:
    """
    处理SEC文件并添加到Pinecone索引
    
    Args:
        index_name: 索引名称
        file_paths: SEC文件路径列表
    """
    try:
        logger.info(f"开始处理 {len(file_paths)} 个文件并添加到索引 {index_name}")
        
        # 这里需要实现文件处理逻辑
        # 例如，提取文本内容，分块，等等
        
        # 优化：并行处理文件
        async def process_file(file_path, file_idx):
            try:
                # 读取文件内容
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 优化的分块逻辑
                chunks = []
                # 分块 (这里使用更智能的分割方法)
                paragraphs = []
                current_paragraph = ""
                
                for line in content.split('\n'):
                    line = line.strip()
                    if not line and current_paragraph:
                        if len(current_paragraph) > 10:  # 忽略太短的段落
                            paragraphs.append(current_paragraph)
                        current_paragraph = ""
                    elif line:
                        current_paragraph += " " + line if current_paragraph else line
                
                # 添加最后一个段落
                if current_paragraph and len(current_paragraph) > 10:
                    paragraphs.append(current_paragraph)
                
                # 基于段落长度合并或分割
                doc_chunks = []
                current_chunk = ""
                
                for para in paragraphs:
                    # 如果段落太长，进一步分割
                    if len(para) > 2000:
                        # 先添加当前块
                        if current_chunk:
                            doc_chunks.append(current_chunk)
                            current_chunk = ""
                        
                        # 分割长段落
                        sentences = para.split(". ")
                        temp_chunk = ""
                        
                        for sent in sentences:
                            if not sent.strip():
                                continue
                                
                            if len(temp_chunk) + len(sent) < 1000:
                                temp_chunk += sent + ". "
                            else:
                                if temp_chunk:
                                    doc_chunks.append(temp_chunk)
                                temp_chunk = sent + ". "
                        
                        if temp_chunk:
                            doc_chunks.append(temp_chunk)
                    
                    # 正常段落，如果添加会导致当前块太大，就先保存当前块
                    elif len(current_chunk) + len(para) > 1000:
                        doc_chunks.append(current_chunk)
                        current_chunk = para
                    
                    # 否则添加到当前块
                    else:
                        current_chunk += "\n\n" + para if current_chunk else para
                
                # 添加最后一个块
                if current_chunk:
                    doc_chunks.append(current_chunk)
                
                # 创建文档
                result_chunks = []
                for j, text in enumerate(doc_chunks):
                    doc_id = f"file_{file_idx}_chunk_{j}"
                    result_chunks.append({
                        "id": doc_id,
                        "text": text,
                        "metadata": {
                            "source": file_path,
                            "chunk_id": j,
                            "file_id": file_idx,
                            "text": text
                        }
                    })
                
                logger.info(f"从文件 {file_path} 中提取了 {len(doc_chunks)} 个块")
                return result_chunks
                
            except Exception as e:
                logger.error(f"处理文件 {file_path} 时出错: {str(e)}")
                return []
        
        # 并行处理所有文件
        processing_tasks = [process_file(file_path, i) for i, file_path in enumerate(file_paths)]
        chunks_results = await asyncio.gather(*processing_tasks)
        
        # 合并所有块
        all_documents = []
        for chunks in chunks_results:
            all_documents.extend(chunks)
        
        logger.info(f"总共提取了 {len(all_documents)} 个文档块")
        
        # 创建Pinecone服务并索引文档
        service = PineconeService(api_key=settings.PINECONE_API_KEY)
        await service.index_documents(index_name, all_documents)
        
        logger.info(f"完成处理和索引 {len(all_documents)} 个文档")
    except Exception as e:
        logger.error(f"处理和索引文件时出错: {str(e)}")

async def main_indexing_flow(stock_symbol: str, sec_files: List[str]):
    """
    主索引流程
    
    Args:
        stock_symbol: 股票代号
        sec_files: SEC文件列表
    """
    try:
        # 初始化Pinecone服务
        service = PineconeService(api_key=settings.PINECONE_API_KEY)
        
        # 索引名称（转小写）
        index_name = stock_symbol.lower()
        
        # 检查索引是否存在
        exists = await service.index_exists(index_name)
        
        if exists:
            # 检查索引是否为空
            is_empty = await service.index_is_empty(index_name)
            
            if is_empty:
                logger.info(f"索引 {index_name} 存在但为空，需要添加文档")
                await process_and_index_files(index_name, sec_files)
            else:
                logger.info(f"索引 {index_name} 已存在且包含数据，跳过索引步骤")
        else:
            logger.info(f"索引 {index_name} 不存在，创建并添加文档")
            await process_and_index_files(index_name, sec_files)
        
        logger.info(f"索引流程完成")
    except Exception as e:
        logger.error(f"主索引流程出错: {str(e)}")

# 示例使用
if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("pinecone_indexing.log"),
            logging.StreamHandler()
        ]
    )
    
    # 示例文件列表
    example_files = [
        "./sec-edgar-filings/AAPL/10-K/0000320193-22-000108/full-submission.txt",
        "./sec-edgar-filings/AAPL/10-K/0000320193-23-000106/full-submission.txt",
        "./sec-edgar-filings/AAPL/10-K/0000320193-21-000105/full-submission.txt",
        "./sec-edgar-filings/AAPL/10-K/0000320193-20-000096/full-submission.txt",
        "./sec-edgar-filings/AAPL/10-K/0000320193-24-000123/full-submission.txt"
    ]
    
    # 运行主索引流程
    asyncio.run(main_indexing_flow("AAPL", example_files))