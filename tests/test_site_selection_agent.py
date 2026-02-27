"""
选址分析Agent单元测试

测试内容:
1. Agent初始化
2. 数据验证
3. 用户消息构建
4. 表格数据提取
5. 章节生成(Mock LLM)
"""

import pytest
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Windows编码问题修复
if sys.platform == 'win32':
    sys.stdout = __import__('io').TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.models.site_selection_data import (
    SiteSelectionData,
    SiteAlternative,
    SiteNaturalConditions,
    SiteExternalConditions,
    SiteSensitiveConditions,
    ConstructionConditions,
    PlanningImpact,
    ConsultationOpinion,
    SchemeComparison,
    get_sample_data
)
from src.agents.site_selection_agent import SiteSelectionAgent


class TestSiteSelectionData:
    """测试选址分析数据模型"""

    def test_sample_data_creation(self):
        """测试示例数据创建"""
        data = get_sample_data()

        assert data is not None
        assert isinstance(data, SiteSelectionData)
        assert len(data.备选方案) == 2
        assert len(data.选址原则) >= 5
        assert len(data.征求意见情况) >= 3

    def test_data_validation(self):
        """测试数据验证"""
        # 测试备选方案数量验证
        data = get_sample_data()
        assert len(data.备选方案) == 2

        # 测试选址原则数量
        assert len(data.选址原则) >= 5
        assert len(data.选址原则) <= 10

    def test_formatted_data(self):
        """测试格式化数据输出"""
        data = get_sample_data()
        formatted = data.get_formatted_data()

        assert formatted is not None
        assert isinstance(formatted, str)
        assert "项目基本信息" in formatted
        assert "选址原则" in formatted
        assert "备选方案" in formatted

    def test_json_serialization(self):
        """测试JSON序列化"""
        data = get_sample_data()
        json_str = data.json()

        assert json_str is not None
        assert isinstance(json_str, str)
        assert len(json_str) > 0

        # 验证可以反序列化
        parsed = SiteSelectionData.parse_raw(json_str)
        assert parsed.项目基本信息 == data.项目基本信息


class TestSiteSelectionAgent:
    """测试选址分析Agent"""

    @pytest.fixture
    def llm_config(self):
        """创建测试用的LLM配置"""
        return {
            "config_list": [{"model": "qwen-plus", "api_key": "test-key"}],
            "temperature": 0.7,
            "cache_seed": 42,
        }

    @pytest.fixture
    def sample_data(self):
        """获取示例数据"""
        return get_sample_data()

    def test_agent_initialization(self, llm_config):
        """测试Agent初始化"""
        agent = SiteSelectionAgent(llm_config)

        assert agent is not None
        assert agent.agent is not None
        assert agent.agent.name == "site_selection_agent"
        assert len(agent.system_message) > 0

    def test_agent_info(self, llm_config):
        """测试Agent信息获取"""
        agent = SiteSelectionAgent(llm_config)
        info = agent.get_agent_info()

        assert info is not None
        assert info["name"] == "site_selection_agent"
        assert "description" in info
        assert "system_message_length" in info

    def test_user_message_building(self, llm_config, sample_data):
        """测试用户消息构建"""
        agent = SiteSelectionAgent(llm_config)
        message = agent._build_user_message(sample_data)

        assert message is not None
        assert isinstance(message, str)
        assert len(message) > 0

        # 验证消息包含关键信息
        assert "项目基本信息" in message
        assert "选址原则" in message
        assert "备选方案" in message
        assert "场地自然条件" in message
        assert "外部配套条件" in message
        assert "选址敏感条件" in message
        assert "施工运营条件" in message
        assert "规划影响条件" in message
        assert "征求意见情况" in message
        assert "方案比选" in message

    def test_data_validation_success(self, llm_config, sample_data):
        """测试数据验证成功"""
        agent = SiteSelectionAgent(llm_config)

        # 应该不抛出异常
        agent._validate_data(sample_data)

    def test_data_validation_failure_alternatives(self, llm_config):
        """测试数据验证失败(备选方案数量不足)"""
        agent = SiteSelectionAgent(llm_config)
        data = get_sample_data()

        # 修改为只有一个备选方案
        data.备选方案 = [data.备选方案[0]]

        with pytest.raises(ValueError, match="至少需要2个备选方案"):
            agent._validate_data(data)

    def test_data_validation_failure_principles(self, llm_config):
        """测试数据验证失败(选址原则数量不足)"""
        agent = SiteSelectionAgent(llm_config)
        data = get_sample_data()

        # 修改为只有4条选址原则
        data.选址原则 = data.选址原则[:4]

        with pytest.raises(ValueError, match="至少需要5条选址原则"):
            agent._validate_data(data)

    def test_message_contains_all_sections(self, llm_config, sample_data):
        """测试消息包含所有必要章节"""
        agent = SiteSelectionAgent(llm_config)
        message = agent._build_user_message(sample_data)

        # 验证包含所有9个主要章节的数据
        required_sections = [
            "地形地貌",
            "气候",
            "区域地质构造",
            "水文地质条件",
            "工程地质",
            "地震",
            "历史保护情况",
            "生态保护情况",
            "矿产资源情况",
            "安全防护情况",
            "占用耕地",
            "生态保护红线",
        ]

        for section in required_sections:
            assert section in message, f"消息缺少章节: {section}"


class TestDocumentServiceTables:
    """测试文档服务表格生成"""

    @pytest.fixture
    def document_service(self):
        """创建文档服务实例"""
        from src.services.document_service import DocumentService
        return DocumentService()

    @pytest.fixture
    def sample_data(self):
        """获取示例数据"""
        return get_sample_data()

    def test_land_use_table_data_extraction(self, document_service, sample_data):
        """测试土地利用表格数据提取"""
        # 提取两个方案的土地利用数据
        scheme1 = sample_data.备选方案[0]
        scheme2 = sample_data.备选方案[1]

        land_use1 = scheme1.土地利用现状
        land_use2 = scheme2.土地利用现状

        assert land_use1 is not None
        assert land_use2 is not None
        assert len(land_use1) > 0
        assert len(land_use2) > 0

    def test_investment_table_data(self, sample_data):
        """测试投资数据获取"""
        construction = sample_data.施工运营条件

        assert construction.方案一总投资 is not None
        assert construction.方案二总投资 is not None

    def test_comparison_table_data(self, sample_data):
        """测试对比表格数据"""
        scheme1 = sample_data.备选方案[0]
        scheme2 = sample_data.备选方案[1]

        # 验证面积数据
        assert scheme1.面积 > 0
        assert scheme2.面积 > 0

        # 验证占用情况
        assert isinstance(scheme1.是否占用耕地, bool)
        assert isinstance(scheme2.是否占用耕地, bool)


class TestOrchestrator:
    """测试编排器"""

    @pytest.fixture
    def llm_config(self):
        """创建测试用的LLM配置"""
        return {
            "config_list": [{"model": "qwen-plus", "api_key": "test-key"}],
            "temperature": 0.7,
        }

    def test_orchestrator_initialization(self, llm_config):
        """测试编排器初始化"""
        from src.services.autogen_orchestrator import AutoGenOrchestrator

        orchestrator = AutoGenOrchestrator(llm_config)

        assert orchestrator is not None
        assert len(orchestrator.agents) >= 1
        assert "project_overview" in orchestrator.agents

    def test_agent_info(self, llm_config):
        """测试Agent信息获取"""
        from src.services.autogen_orchestrator import AutoGenOrchestrator

        orchestrator = AutoGenOrchestrator(llm_config)
        agents_info = orchestrator.get_agent_info()

        assert agents_info is not None
        assert len(agents_info) >= 1


# 运行测试的入口
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])