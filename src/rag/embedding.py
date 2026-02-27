"""
百炼Embedding API集成
使用阿里云百炼text-embedding-v3模型 (1024维向量)
"""

import os
import asyncio
from typing import List, Optional
import logging
import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class BailianEmbedding:
    """
    百炼Embedding API封装
    
    使用text-embedding-v3模型，支持1024/768/512维度
    通过OpenAI兼容接口调用
    """
    
    # API配置
    DEFAULT_MODEL = "text-embedding-v3"
    DEFAULT_DIMENSIONS = 1024
    API_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        dimensions: int = DEFAULT_DIMENSIONS,
        batch_size: int = 10,
    ):
        """
        初始化Embedding客户端
        
        Args:
            api_key: 百炼API密钥，不传则从环境变量读取
            model: 模型名称
            dimensions: 向量维度 (1024, 768, 512)
            batch_size: 批量处理大小
            
        Raises:
            ValueError: API密钥未配置
        """
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "未配置百炼API密钥。请设置DASHSCOPE_API_KEY环境变量，"
                "或在初始化时传入api_key参数。"
            )
        
        self.model = model
        self.dimensions = dimensions
        self.batch_size = batch_size
        
        logger.info(
            f"BailianEmbedding初始化: model={model}, "
            f"dimensions={dimensions}, batch_size={batch_size}"
        )
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        同步获取文本向量
        
        Args:
            texts: 文本列表
            
        Returns:
            向量列表
        """
        return asyncio.run(self.embed_async(texts))
    
    async def embed_async(self, texts: List[str]) -> List[List[float]]:
        """
        异步获取文本向量
        
        Args:
            texts: 文本列表
            
        Returns:
            向量列表
        """
        if not texts:
            return []
        
        # 批量处理
        all_embeddings = []
        
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            batch_embeddings = await self._embed_batch(batch)
            all_embeddings.extend(batch_embeddings)
        
        return all_embeddings
    
    async def _embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        批量获取向量
        
        Args:
            texts: 一批文本
            
        Returns:
            向量列表
        """
        url = f"{self.API_BASE_URL}/embeddings"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "input": texts,
            "dimensions": self.dimensions,
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    # 按index排序确保顺序正确
                    items = sorted(data.get("data", []), key=lambda x: x.get("index", 0))
                    return [item.get("embedding", []) for item in items]
                else:
                    logger.error(
                        f"Embedding API调用失败: {response.status_code} - {response.text}"
                    )
                    raise RuntimeError(
                        f"Embedding API调用失败: {response.status_code}"
                    )
                    
            except httpx.TimeoutException:
                logger.error("Embedding API请求超时")
                raise RuntimeError("Embedding API请求超时")
            except Exception as e:
                logger.error(f"Embedding API异常: {e}")
                raise
    
    def embed_single(self, text: str) -> List[float]:
        """
        获取单个文本的向量
        
        Args:
            text: 文本内容
            
        Returns:
            向量
        """
        embeddings = self.embed([text])
        return embeddings[0] if embeddings else []
    
    async def embed_single_async(self, text: str) -> List[float]:
        """
        异步获取单个文本的向量
        
        Args:
            text: 文本内容
            
        Returns:
            向量
        """
        embeddings = await self.embed_async([text])
        return embeddings[0] if embeddings else []


def get_embedding_function():
    """
    获取ChromaDB兼容的embedding函数
    
    Returns:
        可用于ChromaDB的embedding函数
    """
    embedding_client = BailianEmbedding()
    
    def embedding_function(texts: List[str]) -> List[List[float]]:
        """ChromaDB兼容的embedding函数"""
        return embedding_client.embed(texts)
    
    return embedding_function


if __name__ == "__main__":
    # 测试
    print("测试百炼Embedding API...")
    
    client = BailianEmbedding()
    test_texts = ["测试文本1", "测试文本2"]
    
    embeddings = client.embed(test_texts)
    
    print(f"✅ 成功获取{len(embeddings)}个向量")
    print(f"   向量维度: {len(embeddings[0]) if embeddings else 0}")