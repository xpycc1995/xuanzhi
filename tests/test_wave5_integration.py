"""
Wave 5 集成测试 - Agent集成知识库

测试目标:
1. 测试知识库工具模块 (knowledge_tools.py)
2. 测试Agent集成知识库工具
3. 测试AutoGenOrchestrator知识库支持
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock


# =============================================================================
# 测试知识库工具模块
# =============================================================================

class TestKnowledgeTools:
    """测试 src/tools/knowledge_tools.py"""
    
    @patch("src.tools.knowledge_tools._get_retriever")
    def test_search_knowledge_base_success(self, mock_get_retriever):
        """测试通用知识库检索 - 成功"""
        # Mock Retriever
        mock_retriever = Mock()
        mock_result = Mock()
        mock_result.content = "城乡规划法规定..."
        mock_result.score = 0.85
        mock_result.metadata = {"source": "test.pdf"}
        mock_retriever.search.return_value = [mock_result]
        mock_get_retriever.return_value = mock_retriever
        
        from src.tools.knowledge_tools import search_knowledge_base
        
        result = search_knowledge_base("城乡规划", n_results=5)
        data = json.loads(result)
        
        assert data["success"] is True
        assert data["count"] == 1
        assert len(data["results"]) == 1
        assert data["results"][0]["content"] == "城乡规划法规定..."
        assert data["results"][0]["score"] == 0.85
    
    @patch("src.tools.knowledge_tools._get_retriever")
    def test_search_knowledge_base_no_results(self, mock_get_retriever):
        """测试通用知识库检索 - 无结果"""
        mock_retriever = Mock()
        mock_retriever.search.return_value = []
        mock_get_retriever.return_value = mock_retriever
        
        from src.tools.knowledge_tools import search_knowledge_base
        
        result = search_knowledge_base("不存在的查询", n_results=5)
        data = json.loads(result)
        
        assert data["success"] is True
        assert data["count"] == 0
        assert "未找到" in data["message"]
    
    @patch("src.tools.knowledge_tools._get_retriever")
    def test_search_knowledge_base_error(self, mock_get_retriever):
        """测试通用知识库检索 - 错误处理"""
        mock_get_retriever.side_effect = Exception("连接失败")
        
        from src.tools.knowledge_tools import search_knowledge_base
        
        result = search_knowledge_base("测试查询")
        data = json.loads(result)
        
        assert data["success"] is False
        assert "检索失败" in data["message"]
    
    @patch("src.tools.knowledge_tools._get_retriever")
    def test_search_regulations(self, mock_get_retriever):
        """测试法规检索"""
        mock_retriever = Mock()
        mock_result = Mock()
        mock_result.content = "土地管理法第十二条..."
        mock_result.score = 0.9
        mock_result.metadata = {"source": "law.pdf", "original_filename": "土地管理法.pdf"}
        mock_retriever.search.return_value = [mock_result]
        mock_get_retriever.return_value = mock_retriever
        
        from src.tools.knowledge_tools import search_regulations
        
        result = search_regulations("土地管理")
        data = json.loads(result)
        
        assert data["success"] is True
        assert data["count"] == 1
        assert "土地管理法" in data["results"][0]["content"]
        # 验证查询被增强
        call_args = mock_retriever.search.call_args
        assert "法规" in call_args[1]["query"] or "标准" in call_args[1]["query"]
    
    @patch("src.tools.knowledge_tools._get_retriever")
    def test_search_cases(self, mock_get_retriever):
        """测试案例检索"""
        mock_retriever = Mock()
        mock_result = Mock()
        mock_result.content = "某污水处理厂选址案例..."
        mock_result.score = 0.8
        mock_result.metadata = {"source": "case.pdf", "original_filename": "案例集.pdf"}
        mock_retriever.search.return_value = [mock_result]
        mock_get_retriever.return_value = mock_retriever
        
        from src.tools.knowledge_tools import search_cases
        
        result = search_cases("污水处理厂选址")
        data = json.loads(result)
        
        assert data["success"] is True
        assert "案例" in data["message"]
    
    @patch("src.tools.knowledge_tools._get_retriever")
    def test_search_technical_standards(self, mock_get_retriever):
        """测试技术标准检索"""
        mock_retriever = Mock()
        mock_result = Mock()
        mock_result.content = "建设用地指标标准..."
        mock_result.score = 0.85
        mock_result.metadata = {"source": "standard.pdf"}
        mock_retriever.search.return_value = [mock_result]
        mock_get_retriever.return_value = mock_retriever
        
        from src.tools.knowledge_tools import search_technical_standards
        
        result = search_technical_standards("用地指标")
        data = json.loads(result)
        
        assert data["success"] is True
        assert "技术标准" in data["message"]
    
    @patch("src.tools.knowledge_tools._get_retriever")
    def test_get_knowledge_base_stats(self, mock_get_retriever):
        """测试获取知识库统计"""
        mock_retriever = Mock()
        mock_retriever.get_stats.return_value = {
            "document_count": 100,
            "chunk_size": 512,
        }
        mock_get_retriever.return_value = mock_retriever
        
        from src.tools.knowledge_tools import get_knowledge_base_stats
        
        result = get_knowledge_base_stats()
        data = json.loads(result)
        
        assert data["success"] is True
        assert data["stats"]["document_count"] == 100


# =============================================================================
# 测试Agent集成知识库
# =============================================================================

class TestAgentKnowledgeIntegration:
    """测试Agent集成知识库工具"""
    
    def test_project_overview_agent_has_tools(self):
        """测试ProjectOverviewAgent有知识库工具"""
        from src.agents.project_overview_agent import ProjectOverviewAgent
        
        # 验证工具导入
        agent_module = __import__("src.agents.project_overview_agent", fromlist=[""])
        assert hasattr(agent_module, "search_regulations")
        assert hasattr(agent_module, "search_cases")
    
    def test_site_selection_agent_has_tools(self):
        """测试SiteSelectionAgent有知识库工具"""
        from src.agents.site_selection_agent import SiteSelectionAgent
        
        agent_module = __import__("src.agents.site_selection_agent", fromlist=[""])
        assert hasattr(agent_module, "search_regulations")
        assert hasattr(agent_module, "search_cases")
        assert hasattr(agent_module, "search_technical_standards")
    
    def test_compliance_analysis_agent_has_tools(self):
        """测试ComplianceAnalysisAgent有知识库工具"""
        from src.agents.compliance_analysis_agent import ComplianceAnalysisAgent
        
        agent_module = __import__("src.agents.compliance_analysis_agent", fromlist=[""])
        assert hasattr(agent_module, "search_regulations")
        assert hasattr(agent_module, "search_cases")
    
    def test_rationality_analysis_agent_has_tools(self):
        """测试RationalityAnalysisAgent有知识库工具"""
        from src.agents.rationality_analysis_agent import RationalityAnalysisAgent
        
        agent_module = __import__("src.agents.rationality_analysis_agent", fromlist=[""])
        assert hasattr(agent_module, "search_regulations")
        assert hasattr(agent_module, "search_cases")
        assert hasattr(agent_module, "search_technical_standards")
    
    def test_land_use_analysis_agent_has_tools(self):
        """测试LandUseAnalysisAgent有知识库工具"""
        from src.agents.land_use_analysis_agent import LandUseAnalysisAgent
        
        agent_module = __import__("src.agents.land_use_analysis_agent", fromlist=[""])
        assert hasattr(agent_module, "search_regulations")
        assert hasattr(agent_module, "search_cases")
        assert hasattr(agent_module, "search_technical_standards")
    
    def test_conclusion_agent_has_tools(self):
        """测试ConclusionAgent有知识库工具"""
        from src.agents.conclusion_agent import ConclusionAgent
        
        agent_module = __import__("src.agents.conclusion_agent", fromlist=[""])
        assert hasattr(agent_module, "search_regulations")
        assert hasattr(agent_module, "search_cases")
    
    @patch("src.core.autogen_config.get_model_client")
    def test_agent_initialization_with_tools(self, mock_get_client):
        """测试Agent初始化时传入工具"""
        from src.agents.project_overview_agent import ProjectOverviewAgent
        from src.tools.knowledge_tools import search_regulations, search_cases
        
        # Mock model client with proper model_info
        mock_client = Mock()
        mock_client.model_info = {"function_calling": True, "json_output": True}
        mock_get_client.return_value = mock_client
        
        # 创建Agent
        agent = ProjectOverviewAgent(mock_client)
        
        # 验证AssistantAgent被正确创建
        assert agent.agent is not None
        assert agent.agent.name == "project_overview_agent"


# =============================================================================
# 测试AutoGenOrchestrator知识库支持
# =============================================================================

class TestOrchestratorKnowledgeSupport:
    """测试AutoGenOrchestrator知识库支持"""
    
    @patch("src.core.autogen_config.get_model_client")
    @patch("src.core.autogen_config.get_model_info")
    def test_orchestrator_has_retriever_property(self, mock_get_info, mock_get_client):
        """测试Orchestrator有retriever属性"""
        from src.services.autogen_orchestrator import AutoGenOrchestrator
        
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_get_info.return_value = {"provider": "test", "model": "test-model"}
        
        orchestrator = AutoGenOrchestrator()
        
        assert hasattr(orchestrator, "_retriever")
        assert orchestrator._retriever is None  # 延迟初始化
    
    @patch("src.core.autogen_config.get_model_client")
    @patch("src.core.autogen_config.get_model_info")
    @patch("src.services.autogen_orchestrator.get_retriever")
    def test_orchestrator_get_retriever(self, mock_get_retriever, mock_get_info, mock_get_client):
        """测试Orchestrator获取retriever"""
        from src.services.autogen_orchestrator import AutoGenOrchestrator
        
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_get_info.return_value = {"provider": "test", "model": "test-model"}
        mock_retriever = Mock()
        mock_get_retriever.return_value = mock_retriever
        
        orchestrator = AutoGenOrchestrator()
        retriever = orchestrator.get_retriever()
        
        assert retriever is mock_retriever
        mock_get_retriever.assert_called_once()
    
    @patch("src.core.autogen_config.get_model_client")
    @patch("src.core.autogen_config.get_model_info")
    def test_orchestrator_set_retriever(self, mock_get_info, mock_get_client):
        """测试Orchestrator设置retriever"""
        from src.services.autogen_orchestrator import AutoGenOrchestrator
        from src.rag.retriever import Retriever
        
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_get_info.return_value = {"provider": "test", "model": "test-model"}
        
        mock_retriever = Mock(spec=Retriever)
        
        orchestrator = AutoGenOrchestrator()
        orchestrator.set_retriever(mock_retriever)
        
        assert orchestrator._retriever is mock_retriever


# =============================================================================
# 测试工具导出
# =============================================================================

class TestToolsExport:
    """测试工具模块导出"""
    
    def test_knowledge_tools_export(self):
        """测试knowledge_tools导出"""
        from src.tools import (
            kb_search,
            search_regulations,
            search_cases,
            search_technical_standards,
            get_knowledge_base_stats,
            KNOWLEDGE_TOOLS,
        )
        
        assert callable(kb_search)
        assert callable(search_regulations)
        assert callable(search_cases)
        assert callable(search_technical_standards)
        assert callable(get_knowledge_base_stats)
        assert isinstance(KNOWLEDGE_TOOLS, list)
        assert len(KNOWLEDGE_TOOLS) == 5


# =============================================================================
# 端到端测试 (需要真实API)
# =============================================================================

@pytest.mark.integration
class TestEndToEndKnowledgeIntegration:
    """端到端测试 - 需要真实环境和API"""
    
    @pytest.mark.skip(reason="需要真实API密钥和知识库数据")
    def test_full_workflow_with_knowledge_base(self):
        """测试完整工作流程"""
        # 1. 初始化知识库
        # 2. 添加文档
        # 3. 创建Agent
        # 4. 检索知识
        # 5. 生成内容
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])