"""
检索服务 - 高级知识检索接口

功能:
- 封装KnowledgeBase提供易用的高级检索接口
- 支持文档摄取和检索一体化
- 提供批量处理和统计功能
"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

from .knowledge_base import KnowledgeBase
from .document_processor import DocumentProcessor, Document
from .text_chunker import TextChunker, TextChunk

logger = logging.getLogger(__name__)


class RetrievalResult:
    """检索结果数据结构"""
    
    def __init__(
        self,
        content: str,
        score: float,
        metadata: Dict[str, Any],
        doc_id: str,
    ):
        self.content = content
        self.score = score  # 相似度分数 (0-1, 越高越相似)
        self.metadata = metadata
        self.doc_id = doc_id
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "content": self.content,
            "score": self.score,
            "metadata": self.metadata,
            "doc_id": self.doc_id,
        }
    
    def __repr__(self) -> str:
        return f"RetrievalResult(score={self.score:.3f}, content={self.content[:50]}...)"


class Retriever:
    """
    高级检索服务
    
    功能:
    - 文档摄取: 处理文件/目录并添加到知识库
    - 语义检索: 支持阈值过滤的高级检索
    - 知识库管理: 统计、清空等操作
    
    默认配置:
    - chunk_size: 512字符
    - overlap: 128字符
    - n_results: 5
    - threshold: 0.7
    """
    
    DEFAULT_N_RESULTS = 5
    DEFAULT_THRESHOLD = 0.7
    
    def __init__(
        self,
        persist_dir: Optional[str] = None,
        collection_name: str = "xuanzhi_knowledge",
        chunk_size: int = 512,
        overlap: int = 128,
    ):
        """
        初始化检索服务
        
        Args:
            persist_dir: 向量数据库持久化目录
            collection_name: 集合名称
            chunk_size: 文本分块大小
            overlap: 分块重叠大小
        """
        # 初始化组件
        self.knowledge_base = KnowledgeBase(
            persist_dir=persist_dir,
            collection_name=collection_name,
        )
        self.document_processor = DocumentProcessor()
        self.text_chunker = TextChunker(
            chunk_size=chunk_size,
            overlap=overlap,
        )
        
        # 配置
        self.chunk_size = chunk_size
        self.overlap = overlap
        
        logger.info(
            f"Retriever初始化: collection={collection_name}, "
            f"chunk_size={chunk_size}, overlap={overlap}"
        )
    
    def ingest_file(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        摄取单个文件到知识库
        
        Args:
            file_path: 文件路径
            metadata: 额外元数据
            
        Returns:
            添加的文档块数量
        """
        logger.info(f"开始摄取文件: {file_path}")
        
        # 解析文档
        document = self.document_processor.process_file(file_path)
        
        # 分块
        chunks = self.text_chunker.chunk_document(document)
        
        if not chunks:
            logger.warning(f"文件无有效内容: {file_path}")
            return 0
        
        # 准备数据
        texts = [chunk.content for chunk in chunks]
        metadatas = [
            {
                **chunk.metadata,
                "source": chunk.source,
                "chunk_id": chunk.chunk_id,
                "original_filename": document.metadata.get("filename", "unknown"),
                **(metadata or {}),
            }
            for chunk in chunks
        ]
        
        # 添加到知识库
        count = self.knowledge_base.add_documents(
            texts=texts,
            metadatas=metadatas,
        )
        
        logger.info(f"文件摄取完成: {file_path}, 添加{count}个块")
        return count
    
    def ingest_directory(
        self,
        dir_path: str,
        recursive: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, int]:
        """
        摄取目录下的所有文件
        
        Args:
            dir_path: 目录路径
            recursive: 是否递归处理子目录
            metadata: 额外元数据
            
        Returns:
            文件路径到添加块数的映射
        """
        logger.info(f"开始摄取目录: {dir_path}")
        
        # 解析目录下所有文档
        documents = self.document_processor.process_directory(
            dir_path=dir_path,
            recursive=recursive,
        )
        
        results = {}
        total_chunks = 0
        
        for document in documents:
            # 分块
            chunks = self.text_chunker.chunk_document(document)
            
            if not chunks:
                continue
            
            # 准备数据
            texts = [chunk.content for chunk in chunks]
            metadatas = [
                {
                    **chunk.metadata,
                    "source": chunk.source,
                    "chunk_id": chunk.chunk_id,
                    "original_filename": document.metadata.get("filename", "unknown"),
                    **(metadata or {}),
                }
                for chunk in chunks
            ]
            
            # 添加到知识库
            count = self.knowledge_base.add_documents(
                texts=texts,
                metadatas=metadatas,
            )
            
            results[document.source] = count
            total_chunks += count
        
        logger.info(
            f"目录摄取完成: {dir_path}, "
            f"处理{len(documents)}个文件, 添加{total_chunks}个块"
        )
        
        return results
    
    def search(
        self,
        query: str,
        n_results: int = DEFAULT_N_RESULTS,
        threshold: Optional[float] = None,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievalResult]:
        """
        语义检索
        
        Args:
            query: 查询文本
            n_results: 返回结果数量
            threshold: 相似度阈值 (0-1), None则不过滤
            where: 元数据过滤条件
            
        Returns:
            检索结果列表
        """
        if threshold is not None:
            # 使用带阈值过滤的检索
            raw_results = self.knowledge_base.search_with_threshold(
                query=query,
                threshold=threshold,
                n_results=n_results * 2,  # 多取一些再过滤
                where=where,
            )
        else:
            raw_results = self.knowledge_base.search(
                query=query,
                n_results=n_results,
                where=where,
            )
        
        # 转换为RetrievalResult
        results = []
        for r in raw_results[:n_results]:
            # ChromaDB距离转相似度
            score = 1 - r.get("distance", 0)
            results.append(RetrievalResult(
                content=r.get("content", ""),
                score=score,
                metadata=r.get("metadata", {}),
                doc_id=r.get("id", ""),
            ))
        
        logger.info(
            f"检索完成: query='{query[:30]}...', "
            f"n_results={len(results)}, threshold={threshold}"
        )
        
        return results
    
    def search_with_context(
        self,
        query: str,
        n_results: int = DEFAULT_N_RESULTS,
        threshold: float = DEFAULT_THRESHOLD,
    ) -> str:
        """
        检索并返回上下文字符串 (用于LLM提示词)
        
        Args:
            query: 查询文本
            n_results: 返回结果数量
            threshold: 相似度阈值
            
        Returns:
            格式化的上下文字符串
        """
        results = self.search(
            query=query,
            n_results=n_results,
            threshold=threshold,
        )
        
        if not results:
            return "未找到相关知识。"
        
        # 构建上下文
        context_parts = ["以下是相关知识库内容:\n"]
        
        for i, result in enumerate(results, 1):
            context_parts.append(f"\n[文档{i}] (相似度: {result.score:.2f})")
            context_parts.append(result.content)
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def clear(self) -> int:
        """
        清空知识库
        
        Returns:
            删除的文档数量
        """
        count = self.knowledge_base.count()
        self.knowledge_base.delete()
        logger.info(f"知识库已清空: 删除{count}个文档")
        return count
    
    def count(self) -> int:
        """
        获取知识库文档数量
        
        Returns:
            文档数量
        """
        return self.knowledge_base.count()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        kb_stats = self.knowledge_base.get_stats()
        
        return {
            **kb_stats,
            "chunk_size": self.chunk_size,
            "overlap": self.overlap,
        }
    
    def list_documents(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        列出知识库中的文档
        
        Args:
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            文档列表
        """
        return self.knowledge_base.list_documents(
            limit=limit,
            offset=offset,
        )


def get_retriever(
    persist_dir: Optional[str] = None,
    collection_name: str = "xuanzhi_knowledge",
) -> Retriever:
    """
    获取Retriever实例 (便捷函数)
    
    Args:
        persist_dir: 持久化目录
        collection_name: 集合名称
        
    Returns:
        Retriever实例
    """
    return Retriever(
        persist_dir=persist_dir,
        collection_name=collection_name,
    )


if __name__ == "__main__":
    # 测试
    print("测试Retriever服务...")
    
    retriever = Retriever()
    print(f"知识库统计: {retriever.get_stats()}")
    
    # 测试检索
    results = retriever.search("城乡规划", n_results=3)
    for r in results:
        print(f"  - {r}")