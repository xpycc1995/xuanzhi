"""
知识库核心模块 - ChromaDB封装
提供向量存储、检索和管理功能
"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
import chromadb
from chromadb.config import Settings

from .embedding import BailianEmbedding, get_embedding_function

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """
    知识库管理器 - ChromaDB封装
    
    功能:
    - 文档向量存储
    - 语义相似度检索
    - 知识库管理（初始化、清空、统计）
    
    默认配置:
    - 存储路径: data/chroma_db/
    - 集合名称: xuanzhi_knowledge
    - 嵌入模型: 百炼text-embedding-v3
    """
    
    DEFAULT_PERSIST_DIR = "data/chroma_db"
    DEFAULT_COLLECTION_NAME = "xuanzhi_knowledge"
    
    def __init__(
        self,
        persist_dir: Optional[str] = None,
        collection_name: str = DEFAULT_COLLECTION_NAME,
        embedding_client: Optional[BailianEmbedding] = None,
    ):
        """
        初始化知识库
        
        Args:
            persist_dir: 向量数据库持久化目录
            collection_name: 集合名称
            embedding_client: Embedding客户端，不传则自动创建
        """
        self.persist_dir = persist_dir or os.getenv(
            "CHROMA_PERSIST_DIR", self.DEFAULT_PERSIST_DIR
        )
        self.collection_name = collection_name
        
        # 确保目录存在
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
        
        # 初始化Embedding客户端
        self.embedding_client = embedding_client or BailianEmbedding()
        
        # 初始化ChromaDB客户端
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )
        
        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        
        logger.info(
            f"KnowledgeBase初始化: persist_dir={self.persist_dir}, "
            f"collection={self.collection_name}, "
            f"现有文档数={self.count()}"
        )
    
    def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> int:
        """
        添加文档到知识库
        
        Args:
            texts: 文本列表
            metadatas: 元数据列表
            ids: 文档ID列表，不传则自动生成
            
        Returns:
            添加的文档数量
        """
        if not texts:
            return 0
        
        # 生成ID
        if ids is None:
            existing_count = self.count()
            ids = [f"doc_{existing_count + i}" for i in range(len(texts))]
        
        # 生成向量
        logger.info(f"正在为{len(texts)}个文档生成向量...")
        embeddings = self.embedding_client.embed(texts)
        
        # 准备元数据 (ChromaDB要求非空)
        if metadatas is None:
            metadatas = [{"source": "unknown"} for _ in texts]
        else:
            # 确保每个metadata至少有一个字段
            metadatas = [
                {"source": "provided", **m} if not m else m
                for m in metadatas
            ]
        
        # 添加到集合
        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
        )
        
        logger.info(f"成功添加{len(texts)}个文档到知识库")
        return len(texts)
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        语义相似度检索
        
        Args:
            query: 查询文本
            n_results: 返回结果数量
            where: 元数据过滤条件
            
        Returns:
            检索结果列表
        """
        # 生成查询向量
        query_embedding = self.embedding_client.embed_single(query)
        
        # 执行检索
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"],
        )
        
        # 格式化结果
        formatted_results = []
        
        if results and results.get("documents"):
            for i, doc in enumerate(results["documents"][0]):
                result = {
                    "content": doc,
                    "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                    "distance": results["distances"][0][i] if results.get("distances") else 0,
                    "id": results["ids"][0][i] if results.get("ids") else "",
                }
                formatted_results.append(result)
        
        logger.info(
            f"检索完成: query='{query[:30]}...', "
            f"n_results={len(formatted_results)}"
        )
        
        return formatted_results
    
    def search_with_threshold(
        self,
        query: str,
        threshold: float = 0.7,
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        带相似度阈值的检索
        
        Args:
            query: 查询文本
            threshold: 相似度阈值 (余弦距离，越小越相似)
            n_results: 最大返回结果数量
            where: 元数据过滤条件
            
        Returns:
            相似度超过阈值的结果列表
        """
        results = self.search(query, n_results=n_results, where=where)
        
        # ChromaDB使用余弦距离，转换为相似度
        # 距离 = 1 - 相似度，所以阈值判断: 1 - distance >= threshold
        filtered_results = [
            r for r in results
            if (1 - r["distance"]) >= threshold
        ]
        
        logger.info(
            f"阈值过滤: 原始结果={len(results)}, "
            f"阈值={threshold}, 过滤后={len(filtered_results)}"
        )
        
        return filtered_results
    
    def delete(self, ids: Optional[List[str]] = None) -> int:
        """
        删除文档
        
        Args:
            ids: 要删除的文档ID列表，None则清空全部
            
        Returns:
            删除的文档数量
        """
        if ids:
            count = len(ids)
            self.collection.delete(ids=ids)
        else:
            count = self.count()
            # 清空集合
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        
        logger.info(f"删除了{count}个文档")
        return count
    
    def count(self) -> int:
        """
        获取文档数量
        
        Returns:
            文档数量
        """
        return self.collection.count()
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        获取单个文档
        
        Args:
            doc_id: 文档ID
            
        Returns:
            文档内容，不存在返回None
        """
        results = self.collection.get(
            ids=[doc_id],
            include=["documents", "metadatas"],
        )
        
        if results and results.get("documents"):
            return {
                "id": doc_id,
                "content": results["documents"][0],
                "metadata": results["metadatas"][0] if results.get("metadatas") else {},
            }
        
        return None
    
    def list_documents(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        列出文档
        
        Args:
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            文档列表
        """
        results = self.collection.get(
            limit=limit,
            offset=offset,
            include=["documents", "metadatas"],
        )
        
        documents = []
        
        if results and results.get("ids"):
            for i, doc_id in enumerate(results["ids"]):
                documents.append({
                    "id": doc_id,
                    "content": results["documents"][i] if results.get("documents") else "",
                    "metadata": results["metadatas"][i] if results.get("metadatas") else {},
                })
        
        return documents
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取知识库统计信息
        
        Returns:
            统计信息字典
        """
        return {
            "collection_name": self.collection_name,
            "persist_dir": self.persist_dir,
            "document_count": self.count(),
            "embedding_model": self.embedding_client.model,
            "embedding_dimensions": self.embedding_client.dimensions,
        }


def get_sample_knowledge_base() -> KnowledgeBase:
    """
    创建示例知识库（用于测试）
    
    Returns:
        包含示例数据的KnowledgeBase实例
    """
    kb = KnowledgeBase()
    
    # 添加示例文档
    texts = [
        "规划选址应当符合城乡规划要求，避开地质灾害易发区。",
        "项目建设用地应当节约集约用地，严格控制用地规模。",
        "选址论证报告应当包括项目概况、选址分析等章节。",
    ]
    
    metadatas = [
        {"source": "regulation_1.txt", "type": "regulation"},
        {"source": "regulation_2.txt", "type": "regulation"},
        {"source": "guideline_1.txt", "type": "guideline"},
    ]
    
    kb.add_documents(texts=texts, metadatas=metadatas)
    
    return kb


if __name__ == "__main__":
    # 测试
    print("测试知识库...")
    
    kb = KnowledgeBase()
    print(f"知识库统计: {kb.get_stats()}")