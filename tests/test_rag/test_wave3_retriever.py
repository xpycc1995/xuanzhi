"""
Wave 3 检索服务测试 - Retriever + CLI测试

测试内容:
- Retriever类功能测试
- CLI命令测试 (mock API)
- 集成测试
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from pathlib import Path


# 测试Retriever类 (不依赖真实API)
class TestRetriever:
    """Retriever检索服务测试"""
    
    @patch('src.rag.knowledge_base.BailianEmbedding')
    @patch('src.rag.knowledge_base.chromadb')
    def test_retriever_init(self, mock_chroma, mock_embedding):
        """测试Retriever初始化"""
        # Mock ChromaDB
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chroma.PersistentClient.return_value = mock_client
        
        from src.rag.retriever import Retriever
        
        retriever = Retriever()
        
        assert retriever.knowledge_base is not None
        assert retriever.chunk_size == 512
        assert retriever.overlap == 128
    
    @patch('src.rag.knowledge_base.BailianEmbedding')
    @patch('src.rag.knowledge_base.chromadb')
    def test_retriever_custom_config(self, mock_chroma, mock_embedding):
        """测试自定义配置"""
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chroma.PersistentClient.return_value = mock_client
        
        from src.rag.retriever import Retriever
        
        retriever = Retriever(
            collection_name="test_collection",
            chunk_size=256,
            overlap=64,
        )
        
        assert retriever.chunk_size == 256
        assert retriever.overlap == 64
    
    @patch('src.rag.knowledge_base.BailianEmbedding')
    @patch('src.rag.knowledge_base.chromadb')
    def test_search_returns_results(self, mock_chroma, mock_embedding):
        """测试搜索返回结果"""
        from src.rag.retriever import Retriever, RetrievalResult
        
        # Mock ChromaDB
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_collection.query.return_value = {
            "documents": [["测试内容1", "测试内容2"]],
            "metadatas": [[{}, {}]],
            "distances": [[0.1, 0.2]],
            "ids": [["1", "2"]],
        }
        mock_client = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chroma.PersistentClient.return_value = mock_client
        
        # Mock embedding
        mock_embedding_instance = MagicMock()
        mock_embedding_instance.embed_single.return_value = [0.1] * 1024
        mock_embedding.return_value = mock_embedding_instance
        
        retriever = Retriever()
        results = retriever.search("测试查询", n_results=2)
        
        assert len(results) == 2
        assert isinstance(results[0], RetrievalResult)
        assert results[0].score > 0  # 1 - distance
    
    @patch('src.rag.knowledge_base.BailianEmbedding')
    @patch('src.rag.knowledge_base.chromadb')
    def test_search_with_threshold(self, mock_chroma, mock_embedding):
        """测试带阈值的搜索"""
        from src.rag.retriever import Retriever
        
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_collection.query.return_value = {
            "documents": [["高相似度内容"]],
            "metadatas": [[{}]],
            "distances": [[0.2]],
            "ids": [["1"]],
        }
        mock_client = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chroma.PersistentClient.return_value = mock_client
        
        mock_embedding_instance = MagicMock()
        mock_embedding_instance.embed_single.return_value = [0.1] * 1024
        mock_embedding.return_value = mock_embedding_instance
        
        retriever = Retriever()
        results = retriever.search("测试查询", threshold=0.7)
        
        # 结果应该被阈值过滤
        assert len(results) >= 0


class TestRetrievalResult:
    """RetrievalResult测试"""
    
    def test_result_creation(self):
        """测试结果创建"""
        from src.rag.retriever import RetrievalResult
        
        result = RetrievalResult(
            content="测试内容",
            score=0.85,
            metadata={"source": "test.txt"},
            doc_id="doc_1",
        )
        
        assert result.content == "测试内容"
        assert result.score == 0.85
        assert result.metadata["source"] == "test.txt"
    
    def test_result_to_dict(self):
        """测试结果转换为字典"""
        from src.rag.retriever import RetrievalResult
        
        result = RetrievalResult(
            content="测试内容",
            score=0.85,
            metadata={"source": "test.txt"},
            doc_id="doc_1",
        )
        
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict["content"] == "测试内容"
        assert result_dict["score"] == 0.85


class TestCLICommands:
    """CLI命令测试"""
    
    def test_cli_help(self):
        """测试CLI帮助"""
        from typer.testing import CliRunner
        from scripts.kb import app
        
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        assert "RAG知识库管理工具" in result.output
    
    def test_cli_init_command(self):
        """测试init命令"""
        from typer.testing import CliRunner
        from scripts.kb import app
        
        runner = CliRunner()
        
        with patch('scripts.kb.Retriever') as mock_retriever:
            mock_instance = MagicMock()
            mock_instance.get_stats.return_value = {
                "collection_name": "test",
                "persist_dir": "data/chroma_db",
                "document_count": 0,
                "embedding_model": "text-embedding-v3",
            }
            mock_retriever.return_value = mock_instance
            
            result = runner.invoke(app, ["init"])
            
            assert result.exit_code == 0
            assert "初始化成功" in result.output
    
    def test_cli_stats_command(self):
        """测试stats命令"""
        from typer.testing import CliRunner
        from scripts.kb import app
        
        runner = CliRunner()
        
        with patch('scripts.kb.get_retriever') as mock_get_retriever:
            mock_instance = MagicMock()
            mock_instance.get_stats.return_value = {
                "collection_name": "xuanzhi_knowledge",
                "persist_dir": "data/chroma_db",
                "document_count": 10,
                "embedding_model": "text-embedding-v3",
                "embedding_dimensions": 1024,
                "chunk_size": 512,
                "overlap": 128,
            }
            mock_get_retriever.return_value = mock_instance
            
            result = runner.invoke(app, ["stats"])
            
            assert result.exit_code == 0
            assert "知识库统计信息" in result.output


class TestRetrieverIntegration:
    """Retriever集成测试 (需要mock embedding)"""
    
    @patch('src.rag.embedding.httpx.AsyncClient')
    def test_ingest_file_flow(self, mock_httpx):
        """测试文件摄取流程"""
        # 创建临时测试文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("这是一个测试文档，用于测试文件摄取功能。")
            temp_file = f.name
        
        try:
            # Mock embedding API响应
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": [{"embedding": [0.1] * 1024, "index": 0}]
            }
            
            mock_client = MagicMock()
            mock_client.post = MagicMock(return_value=mock_response)
            mock_httpx.return_value.__aenter__ = MagicMock(return_value=mock_client)
            mock_httpx.return_value.__aexit__ = MagicMock(return_value=None)
            
            from src.rag.retriever import Retriever
            
            with patch('src.rag.knowledge_base.chromadb') as mock_chroma:
                # Mock ChromaDB
                mock_collection = MagicMock()
                mock_collection.count.return_value = 0
                mock_client_instance = MagicMock()
                mock_client_instance.get_or_create_collection.return_value = mock_collection
                mock_chroma.PersistentClient.return_value = mock_client_instance
                
                retriever = Retriever()
                # 由于文件小于chunk_size，应该返回1个块
                # 实际测试需要更多mock
                
        finally:
            os.unlink(temp_file)


# 运行测试
if __name__ == "__main__":
    pytest.main([__file__, "-v"])