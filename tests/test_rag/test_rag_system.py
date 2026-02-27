"""
RAG知识库系统单元测试
测试覆盖率目标: >80%
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.rag import (
    DocumentProcessor,
    TextChunker,
    BailianEmbedding,
    KnowledgeBase,
)
from src.rag.document_processor import Document, get_sample_documents
from src.rag.text_chunker import TextChunk, get_sample_chunks


# ============================================================================
# DocumentProcessor 测试
# ============================================================================

class TestDocumentProcessor:
    """DocumentProcessor单元测试"""
    
    def test_initialization(self):
        """测试初始化"""
        processor = DocumentProcessor()
        assert processor.encoding == 'utf-8'
        assert '.pdf' in processor.SUPPORTED_EXTENSIONS
        assert '.docx' in processor.SUPPORTED_EXTENSIONS
        assert '.md' in processor.SUPPORTED_EXTENSIONS
        assert '.txt' in processor.SUPPORTED_EXTENSIONS
    
    def test_supported_extensions(self):
        """测试支持的文件格式"""
        processor = DocumentProcessor()
        assert len(processor.SUPPORTED_EXTENSIONS) >= 4
    
    def test_parse_text_file(self, tmp_path):
        """测试文本文件解析"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("这是一个测试文档。\n包含多行内容。", encoding='utf-8')
        
        processor = DocumentProcessor()
        doc = processor.process_file(str(test_file))
        
        assert isinstance(doc, Document)
        assert "测试文档" in doc.content
        assert doc.doc_type == 'txt'
        assert doc.metadata['filename'] == 'test.txt'
    
    def test_parse_markdown_file(self, tmp_path):
        """测试Markdown文件解析"""
        test_file = tmp_path / "test.md"
        test_file.write_text("# 标题\n\n这是Markdown内容。", encoding='utf-8')
        
        processor = DocumentProcessor()
        doc = processor.process_file(str(test_file))
        
        assert "# 标题" in doc.content
        assert doc.doc_type == 'md'
    
    def test_file_not_found(self):
        """测试文件不存在异常"""
        processor = DocumentProcessor()
        
        with pytest.raises(FileNotFoundError):
            processor.process_file("/nonexistent/path/file.txt")
    
    def test_unsupported_format(self, tmp_path):
        """测试不支持的文件格式"""
        test_file = tmp_path / "test.xyz"
        test_file.write_text("test content", encoding='utf-8')
        
        processor = DocumentProcessor()
        
        with pytest.raises(ValueError, match="不支持的文件格式"):
            processor.process_file(str(test_file))
    
    def test_get_sample_documents(self):
        """测试示例文档获取"""
        samples = get_sample_documents()
        
        assert len(samples) >= 3
        assert all('content' in s for s in samples)
        assert all('metadata' in s for s in samples)


# ============================================================================
# TextChunker 测试
# ============================================================================

class TestTextChunker:
    """TextChunker单元测试"""
    
    def test_initialization(self):
        """测试初始化"""
        chunker = TextChunker()
        
        assert chunker.chunk_size == TextChunker.DEFAULT_CHUNK_SIZE
        assert chunker.overlap == TextChunker.DEFAULT_OVERLAP
    
    def test_custom_config(self):
        """测试自定义配置"""
        chunker = TextChunker(chunk_size=256, overlap=64)
        
        assert chunker.chunk_size == 256
        assert chunker.overlap == 64
    
    def test_invalid_config(self):
        """测试无效配置"""
        # chunk_size <= 0
        with pytest.raises(ValueError):
            TextChunker(chunk_size=0)
        
        # overlap < 0
        with pytest.raises(ValueError):
            TextChunker(overlap=-1)
        
        # overlap >= chunk_size
        with pytest.raises(ValueError):
            TextChunker(chunk_size=100, overlap=100)
    
    def test_chunk_short_text(self):
        """测试短文本分块"""
        chunker = TextChunker()
        text = "这是一段短文本。"
        
        chunks = chunker.chunk_text(text, source="test")
        
        assert len(chunks) == 1
        assert chunks[0].content == text
        # is_complete存储在metadata中
        assert chunks[0].metadata.get("is_complete") == True
    
    def test_chunk_long_text(self):
        """测试长文本分块"""
        chunker = TextChunker(chunk_size=100, overlap=20)
        text = "这是测试句子。" * 20
        
        chunks = chunker.chunk_text(text, source="test")
        
        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk.content) <= chunker.chunk_size + 50
    
    def test_chunk_empty_text(self):
        """测试空文本"""
        chunker = TextChunker()
        
        assert chunker.chunk_text("") == []
        assert chunker.chunk_text(None) == []
    
    def test_chunk_with_metadata(self):
        """测试带元数据的分块"""
        chunker = TextChunker()
        text = "测试文本内容。"
        metadata = {"source": "test.txt", "type": "regulation"}
        
        chunks = chunker.chunk_text(text, metadata=metadata, source="test.txt")
        
        assert chunks[0].metadata["source"] == "test.txt"
        assert chunks[0].metadata["type"] == "regulation"
    
    def test_get_chunk_info(self):
        """测试分块统计信息"""
        chunker = TextChunker(chunk_size=100, overlap=20)
        text = "测试内容。" * 50
        
        chunks = chunker.chunk_text(text)
        info = chunker.get_chunk_info(chunks)
        
        assert info["total_chunks"] > 0
        assert info["total_chars"] > 0
        assert info["avg_chunk_size"] > 0
    
    def test_get_sample_chunks(self):
        """测试示例块获取"""
        samples = get_sample_chunks()
        
        assert len(samples) >= 3


# ============================================================================
# BailianEmbedding 测试
# ============================================================================

class TestBailianEmbedding:
    """BailianEmbedding单元测试"""
    
    def test_initialization(self):
        """测试初始化"""
        embedding = BailianEmbedding()
        
        assert embedding.model == BailianEmbedding.DEFAULT_MODEL
        assert embedding.dimensions == BailianEmbedding.DEFAULT_DIMENSIONS
    
    def test_custom_config(self):
        """测试自定义配置"""
        embedding = BailianEmbedding(
            model="text-embedding-v3",
            dimensions=768,
            batch_size=10,
        )
        
        assert embedding.dimensions == 768
        assert embedding.batch_size == 10
    
    def test_missing_api_key(self, monkeypatch):
        """测试缺少API密钥"""
        monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)
        
        with pytest.raises(ValueError, match="未配置百炼API密钥"):
            BailianEmbedding()
    
    @pytest.mark.integration
    def test_embed_single(self):
        """测试单个文本向量生成（集成测试）"""
        embedding = BailianEmbedding()
        
        result = embedding.embed_single("测试文本")
        
        assert isinstance(result, list)
        assert len(result) == embedding.dimensions
    
    @pytest.mark.integration
    def test_embed_batch(self):
        """测试批量向量生成（集成测试）"""
        embedding = BailianEmbedding()
        texts = ["文本1", "文本2", "文本3"]
        
        results = embedding.embed(texts)
        
        assert len(results) == 3
        assert all(len(r) == embedding.dimensions for r in results)


# ============================================================================
# KnowledgeBase 测试 (使用Mock避免网络调用)
# ============================================================================

class TestKnowledgeBase:
    """KnowledgeBase单元测试"""
    
    def test_initialization(self, temp_chroma_dir):
        """测试初始化"""
        kb = KnowledgeBase(persist_dir=str(temp_chroma_dir))
        
        assert kb.collection_name == KnowledgeBase.DEFAULT_COLLECTION_NAME
        assert kb.count() >= 0
    
    def test_custom_collection_name(self, temp_chroma_dir):
        """测试自定义集合名称"""
        kb = KnowledgeBase(
            persist_dir=str(temp_chroma_dir),
            collection_name="test_collection",
        )
        
        assert kb.collection_name == "test_collection"
    
    def test_add_and_count_with_mock(self, temp_chroma_dir):
        """测试添加文档和计数 (使用Mock)"""
        # Mock embedding客户端 - 使用side_effect动态响应
        mock_embedding = Mock(spec=BailianEmbedding)
        mock_embedding.embed.side_effect = lambda texts: [[0.1] * 1024 for _ in texts]
        mock_embedding.embed_single.return_value = [0.1] * 1024
        
        # 使用唯一集合名称避免冲突
        kb = KnowledgeBase(
            persist_dir=str(temp_chroma_dir),
            collection_name="test_add_count",
            embedding_client=mock_embedding,
        )
        initial_count = kb.count()
        
        texts = ["测试文档1", "测试文档2"]
        count = kb.add_documents(texts)
        
        assert count == 2
        assert kb.count() == initial_count + 2
    
    def test_add_empty_documents(self, temp_chroma_dir):
        """测试添加空文档列表"""
        mock_embedding = Mock(spec=BailianEmbedding)
        kb = KnowledgeBase(
            persist_dir=str(temp_chroma_dir),
            embedding_client=mock_embedding,
        )
        
        count = kb.add_documents([])
        
        assert count == 0
    
    def test_search_with_mock(self, temp_chroma_dir):
        """测试检索功能 (使用Mock)"""
        mock_embedding = Mock(spec=BailianEmbedding)
        mock_embedding.embed.side_effect = lambda texts: [[0.1] * 1024 for _ in texts]
        mock_embedding.embed_single.return_value = [0.1] * 1024
        
        # 使用唯一集合名称
        kb = KnowledgeBase(
            persist_dir=str(temp_chroma_dir),
            collection_name="test_search",
            embedding_client=mock_embedding,
        )
        
        # 添加测试文档
        texts = [
            "规划选址应当符合城乡规划要求。",
            "项目建设用地应当节约集约用地。",
        ]
        kb.add_documents(texts)
        
        # 检索
        results = kb.search("城乡规划", n_results=2)
        
        assert len(results) > 0
        assert "content" in results[0]
    
    def test_delete_documents(self, temp_chroma_dir):
        """测试删除文档"""
        mock_embedding = Mock(spec=BailianEmbedding)
        mock_embedding.embed.side_effect = lambda texts: [[0.1] * 1024 for _ in texts]
        
        kb = KnowledgeBase(
            persist_dir=str(temp_chroma_dir),
            collection_name="test_delete",
            embedding_client=mock_embedding,
        )
        
        texts = ["文档1", "文档2"]
        ids = ["id1", "id2"]
        kb.add_documents(texts, ids=ids)
        
        count = kb.delete(ids=["id1"])
        
        assert count == 1
    
    def test_clear_all(self, temp_chroma_dir):
        """测试清空知识库"""
        mock_embedding = Mock(spec=BailianEmbedding)
        mock_embedding.embed.side_effect = lambda texts: [[0.1] * 1024 for _ in texts]
        
        kb = KnowledgeBase(
            persist_dir=str(temp_chroma_dir),
            collection_name="test_clear",
            embedding_client=mock_embedding,
        )
        
        texts = ["文档1", "文档2", "文档3"]
        kb.add_documents(texts)
        
        kb.delete()
        
        assert kb.count() == 0
    
    def test_get_stats(self, temp_chroma_dir):
        """测试获取统计信息"""
        kb = KnowledgeBase(persist_dir=str(temp_chroma_dir))
        
        stats = kb.get_stats()
        
        assert "collection_name" in stats
        assert "document_count" in stats
        assert "embedding_model" in stats
    
    def test_list_documents(self, temp_chroma_dir):
        """测试列出文档"""
        mock_embedding = Mock(spec=BailianEmbedding)
        mock_embedding.embed.side_effect = lambda texts: [[0.1] * 1024 for _ in texts]
        
        # 使用唯一集合名称
        kb = KnowledgeBase(
            persist_dir=str(temp_chroma_dir),
            collection_name="test_list",
            embedding_client=mock_embedding,
        )
        
        texts = ["文档1", "文档2"]
        kb.add_documents(texts)
        
        docs = kb.list_documents(limit=10)
        
        assert len(docs) >= 2


# ============================================================================
# 集成测试 (需要网络连接)
# ============================================================================

class TestRAGIntegration:
    """RAG系统集成测试"""
    
    @pytest.mark.integration
    def test_full_pipeline(self, temp_chroma_dir):
        """测试完整RAG流程"""
        # 1. 创建文档处理器
        processor = DocumentProcessor()
        
        # 2. 创建分块器
        chunker = TextChunker(chunk_size=200, overlap=50)
        
        # 3. 创建知识库
        kb = KnowledgeBase(persist_dir=str(temp_chroma_dir))
        
        # 4. 模拟文档处理和分块
        text = "规划选址应当符合城乡规划要求。" * 5
        chunks = chunker.chunk_text(text, source="test")
        
        # 5. 添加到知识库
        texts = [c.content for c in chunks]
        metadatas = [c.metadata for c in chunks]
        kb.add_documents(texts, metadatas=metadatas)
        
        # 6. 检索
        results = kb.search("城乡规划", n_results=3)
        
        assert len(results) > 0


# ============================================================================
# 测试入口
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])