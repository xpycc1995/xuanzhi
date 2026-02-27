"""
RAG知识库模块 - 向量检索增强生成

核心组件:
- DocumentProcessor: 多格式文档处理器
- TextChunker: 文本分块器
- BailianEmbedding: 百炼Embedding客户端
- KnowledgeBase: 知识库管理器
"""

from .document_processor import DocumentProcessor, Document
from .text_chunker import TextChunker, TextChunk
from .embedding import BailianEmbedding, get_embedding_function
from .knowledge_base import KnowledgeBase

__all__ = [
    "DocumentProcessor",
    "Document",
    "TextChunker",
    "TextChunk",
    "BailianEmbedding",
    "KnowledgeBase",
    "get_embedding_function",
]