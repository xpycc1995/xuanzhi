"""
Wave 4: Excel智能体测试

测试内容:
- ExcelAssistantAgent初始化
- 工具加载
- read_excel/write_excel功能
- search_knowledge_base功能
- Agent异步调用
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

# 添加项目根目录
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def sample_excel_content():
    """创建测试用Excel内容"""
    return {
        "sheet_name": "项目基本信息",
        "fields": [
            {"name": "项目名称", "value": "测试项目", "is_empty": False},
            {"name": "建设单位", "value": "", "is_empty": True},
            {"name": "项目地点", "value": "杭州市", "is_empty": False},
            {"name": "用地面积", "value": "", "is_empty": True},
        ]
    }


@pytest.fixture
def mock_workbook():
    """模拟Excel工作簿"""
    mock_wb = MagicMock()
    mock_sheet = MagicMock()
    
    # 模拟数据行
    mock_sheet.iter_rows.return_value = [
        ("项目名称", "测试项目"),
        ("建设单位", None),
        ("项目地点", "杭州市"),
        ("用地面积", None),
    ]
    mock_sheet.__iter__ = lambda self: iter([])
    
    mock_wb.__getitem__ = lambda self, key: mock_sheet
    mock_wb.sheetnames = ["项目基本信息"]
    
    return mock_wb


@pytest.fixture
def mock_model_client():
    """模拟模型客户端"""
    client = MagicMock()
    client.model = "qwen-plus"
    return client


# =============================================================================
# 测试: 工具模块 (excel_tools)
# =============================================================================

class TestExcelTools:
    """测试Excel工具函数"""
    
    def test_read_excel_file_not_found(self):
        """测试读取不存在的文件"""
        from src.tools.excel_tools import read_excel
        
        result_json = read_excel("nonexistent_file.xlsx")
        result = json.loads(result_json)
        
        assert "error" in result
        assert "不存在" in result["error"]
    
    def test_read_excel_all_sheets_file_not_found(self):
        """测试读取所有Sheet时文件不存在"""
        from src.tools.excel_tools import read_excel_all_sheets
        
        result_json = read_excel_all_sheets("nonexistent_file.xlsx")
        result = json.loads(result_json)
        
        assert "error" in result
    
    def test_search_knowledge_base_mock(self):
        """测试知识库检索 (mock)"""
        from src.tools.excel_tools import search_knowledge_base
        
        # 使用mock避免实际API调用 (导入在函数内部,patch src.rag)
        with patch("src.rag.get_retriever") as mock_get_retriever:
            mock_retriever = MagicMock()
            mock_retriever.search.return_value = []
            mock_get_retriever.return_value = mock_retriever
            
            result_json = search_knowledge_base("测试查询")
            result = json.loads(result_json)
            
            assert "query" in result
            assert result["query"] == "测试查询"
    
    def test_write_excel_file_not_found(self):
        """测试写入不存在的文件"""
        from src.tools.excel_tools import write_excel
        
        result_json = write_excel(
            file_path="nonexistent.xlsx",
            sheet_name="Sheet1",
            field_name="项目名称",
            field_value="测试值"
        )
        result = json.loads(result_json)
        
        assert "error" in result
    
    def test_get_excel_tools(self):
        """测试获取工具列表"""
        from src.tools.excel_tools import get_excel_tools
        
        tools = get_excel_tools()
        
        assert len(tools) == 6
        assert all(hasattr(t, '__name__') for t in tools)
    
    def test_tool_descriptions(self):
        """测试工具描述"""
        from src.tools.excel_tools import TOOL_DESCRIPTIONS
        
        assert "read_excel" in TOOL_DESCRIPTIONS
        assert "search_knowledge_base" in TOOL_DESCRIPTIONS
        assert "write_excel" in TOOL_DESCRIPTIONS
        
        for tool_name, desc in TOOL_DESCRIPTIONS.items():
            assert "description" in desc
            assert "parameters" in desc


# =============================================================================
# 测试: ExcelAssistantAgent
# =============================================================================

class TestExcelAssistantAgent:
    """测试ExcelAssistantAgent"""
    
    def test_agent_initialization(self, mock_model_client):
        """测试Agent初始化"""
        from src.agents.excel_assistant_agent import ExcelAssistantAgent
        
        agent = ExcelAssistantAgent(mock_model_client)
        
        assert agent.agent.name == "excel_assistant"
        assert len(agent.tools) == 6
        assert agent.enable_search == True
    
    def test_agent_get_tools(self, mock_model_client):
        """测试获取工具列表"""
        from src.agents.excel_assistant_agent import ExcelAssistantAgent
        
        agent = ExcelAssistantAgent(mock_model_client)
        tools = agent.get_tools()
        
        assert len(tools) == 6
        tool_names = [t.__name__ for t in tools]
        assert "read_excel" in tool_names
        assert "write_excel" in tool_names
        assert "search_knowledge_base" in tool_names
    
    def test_agent_get_agent(self, mock_model_client):
        """测试获取AutoGen Agent实例"""
        from src.agents.excel_assistant_agent import ExcelAssistantAgent
        
        agent = ExcelAssistantAgent(mock_model_client)
        autogen_agent = agent.get_agent()
        
        assert autogen_agent is not None
        assert autogen_agent.name == "excel_assistant"
    
    def test_create_excel_agent_function(self):
        """测试便捷创建函数"""
        from src.agents.excel_assistant_agent import create_excel_agent
        
        # patch正确的导入路径
        with patch("src.core.autogen_config.get_model_client") as mock_get_client:
            mock_get_client.return_value = MagicMock()
            
            agent = create_excel_agent()
            
            assert agent is not None
            assert agent.agent.name == "excel_assistant"


# =============================================================================
# 测试: 异步调用
# =============================================================================

class TestAsyncOperations:
    """测试异步操作"""
    
    @pytest.mark.asyncio
    async def test_fill_excel_mock(self, mock_model_client):
        """测试填充Excel (mock)"""
        from src.agents.excel_assistant_agent import ExcelAssistantAgent
        
        agent = ExcelAssistantAgent(mock_model_client)
        
        # Mock Agent的run方法
        async def mock_run(task):
            mock_result = MagicMock()
            mock_message = MagicMock()
            mock_message.content = "填充完成"
            mock_result.messages = [mock_message]
            return mock_result
        
        agent.agent.run = mock_run
        
        result = await agent.fill_excel("test.xlsx")
        
        assert result["success"] == True
        assert "response" in result
    
    @pytest.mark.asyncio
    async def test_analyze_excel_mock(self, mock_model_client):
        """测试分析Excel (mock)"""
        from src.agents.excel_assistant_agent import ExcelAssistantAgent
        
        agent = ExcelAssistantAgent(mock_model_client)
        
        async def mock_run(task):
            mock_result = MagicMock()
            mock_message = MagicMock()
            mock_message.content = "分析结果"
            mock_result.messages = [mock_message]
            return mock_result
        
        agent.agent.run = mock_run
        
        result = await agent.analyze_excel("test.xlsx")
        
        assert result["success"] == True
        assert "analysis" in result
    
    @pytest.mark.asyncio
    async def test_query_for_field_mock(self, mock_model_client):
        """测试字段检索 (mock)"""
        from src.agents.excel_assistant_agent import ExcelAssistantAgent
        
        agent = ExcelAssistantAgent(mock_model_client)
        
        async def mock_run(task):
            mock_result = MagicMock()
            mock_message = MagicMock()
            mock_message.content = "检索结果"
            mock_result.messages = [mock_message]
            return mock_result
        
        agent.agent.run = mock_run
        
        result = await agent.query_for_field("项目名称", "杭州市")
        
        assert result["success"] == True
        assert "suggestions" in result


# =============================================================================
# 测试: 系统消息
# =============================================================================

class TestSystemMessage:
    """测试系统消息"""
    
    def test_system_message_content(self):
        """测试系统消息内容"""
        from src.agents.excel_assistant_agent import EXCEL_ASSISTANT_SYSTEM_MESSAGE
        
        assert "read_excel" in EXCEL_ASSISTANT_SYSTEM_MESSAGE
        assert "search_knowledge_base" in EXCEL_ASSISTANT_SYSTEM_MESSAGE
        assert "write_excel" in EXCEL_ASSISTANT_SYSTEM_MESSAGE
        assert "不编造数据" in EXCEL_ASSISTANT_SYSTEM_MESSAGE
    
    def test_system_message_workflow(self):
        """测试工作流说明"""
        from src.agents.excel_assistant_agent import EXCEL_ASSISTANT_SYSTEM_MESSAGE
        
        # 检查工作流步骤
        assert "第1步" in EXCEL_ASSISTANT_SYSTEM_MESSAGE
        assert "第2步" in EXCEL_ASSISTANT_SYSTEM_MESSAGE
        assert "第3步" in EXCEL_ASSISTANT_SYSTEM_MESSAGE
        assert "第4步" in EXCEL_ASSISTANT_SYSTEM_MESSAGE
        assert "第5步" in EXCEL_ASSISTANT_SYSTEM_MESSAGE


# =============================================================================
# 集成测试 (需要API)
# =============================================================================

@pytest.mark.integration
class TestIntegration:
    """集成测试 - 需要真实API"""
    
    @pytest.mark.skipif(
        not os.environ.get("DASHSCOPE_API_KEY"),
        reason="需要DASHSCOPE_API_KEY"
    )
    def test_real_agent_initialization(self):
        """测试真实Agent初始化"""
        from src.agents.excel_assistant_agent import create_excel_agent
        
        agent = create_excel_agent()
        
        assert agent.agent.name == "excel_assistant"
        assert len(agent.tools) == 6


# =============================================================================
# 运行测试
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])