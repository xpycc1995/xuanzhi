"""
pytest配置文件 - RAG知识库系统测试
"""

import sys
import os
import pytest
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def test_data_dir():
    """测试数据目录"""
    return project_root / "tests" / "test_data"


@pytest.fixture
def temp_chroma_dir(tmp_path):
    """临时ChromaDB目录 (每个测试独立)"""
    chroma_dir = tmp_path / "chroma_db"
    chroma_dir.mkdir(exist_ok=True)
    return chroma_dir


@pytest.fixture
def sample_documents():
    """示例文档数据"""
    return [
        {
            "content": "规划选址应当符合城乡规划要求，避开地质灾害易发区。",
            "metadata": {"source": "test_doc_1.txt", "type": "regulation"},
        },
        {
            "content": "项目建设用地应当节约集约用地，严格控制用地规模。",
            "metadata": {"source": "test_doc_2.txt", "type": "regulation"},
        },
        {
            "content": "选址论证报告应当包括项目概况、选址分析、合规性分析等章节。",
            "metadata": {"source": "test_doc_3.txt", "type": "guideline"},
        },
    ]


@pytest.fixture
def sample_chunks():
    """示例文本块"""
    return [
        "规划选址应当符合城乡规划要求。",
        "项目建设用地应当节约集约用地。",
        "选址论证报告应当包括项目概况。",
    ]


# 异步测试支持
@pytest.fixture
def event_loop_policy():
    """异步事件循环策略"""
    import asyncio
    return asyncio.DefaultEventLoopPolicy()