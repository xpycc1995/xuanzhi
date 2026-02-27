"""
AutoGen 编排器 - 协调多个 Agent 生成报告章节

使用新版 autogen-agentchat API 实现多 Agent 协作。
"""

import os
import asyncio
from typing import Dict, Any, Optional

from autogen_ext.models.openai import OpenAIChatCompletionClient

from src.core.autogen_config import get_model_client, get_model_info
from src.agents.project_overview_agent import ProjectOverviewAgent
from src.agents.site_selection_agent import SiteSelectionAgent
from src.agents.compliance_analysis_agent import ComplianceAnalysisAgent
from src.agents.rationality_analysis_agent import RationalityAnalysisAgent
from src.agents.land_use_analysis_agent import LandUseAnalysisAgent
from src.agents.conclusion_agent import ConclusionAgent

class AutoGenOrchestrator:
    """
    AutoGen 编排器
    
    协调多个专业 Agent 生成规划选址论证报告的各个章节。
    
    新版 API 使用方式:
    - 每个 Agent 独立初始化，传入 model_client
    - 通过 async 方法 generate() 调用 Agent
    - 支持流式输出 generate_stream()
    """
    
    def __init__(
        self,
        model_client: Optional[OpenAIChatCompletionClient] = None,
        temperature: float = 0.7,
    ):
        """
        初始化编排器
        
        Args:
            model_client: OpenAIChatCompletionClient 实例，如果不提供则自动创建
            temperature: 温度参数，默认 0.7
        """
        # 获取或创建模型客户端
        if model_client is None:
            self.model_client = get_model_client(temperature=temperature)
        else:
            self.model_client = model_client
        
        # 延迟初始化 Agent
        self._agents: Dict[str, Any] = {}
        
        # 获取模型信息
        model_info = get_model_info()
        logger.info(f"AutoGen 编排器初始化完成")
        logger.info(f"  提供商: {model_info['provider']}")
        logger.info(f"  模型: {model_info['model']}")
    
    def _initialize_agents(self):
        """
        延迟初始化 Agent
        """
        if not self._agents:
            logger.info("初始化 Agent...")
            
            # 项目概况 Agent
            try:
                self._agents["project_overview"] = ProjectOverviewAgent(self.model_client)
                logger.info("  ✓ 项目概况 Agent 初始化成功")
            except Exception as e:
                logger.warning(f"  ✗ 项目概况 Agent 初始化失败: {str(e)}")
            
            # 选址分析 Agent
            try:
                self._agents["site_selection"] = SiteSelectionAgent(self.model_client)
                logger.info("  ✓ 选址分析 Agent 初始化成功")
            except Exception as e:
                logger.warning(f"  ✗ 选址分析 Agent 初始化失败: {str(e)}")
            
            # 合规分析 Agent
            try:
                self._agents["compliance_analysis"] = ComplianceAnalysisAgent(self.model_client)
                logger.info("  ✓ 合规分析 Agent 初始化成功")
            except Exception as e:
                logger.warning(f"  ✗ 合规分析 Agent 初始化失败: {str(e)}")
            
            # 选址合理性分析 Agent
            try:
                self._agents["rationality_analysis"] = RationalityAnalysisAgent(self.model_client)
                logger.info("  ✓ 选址合理性分析 Agent 初始化成功")
            except Exception as e:
                logger.warning(f"  ✗ 选址合理性分析 Agent 初始化失败: {str(e)}")
            
            # 节约集约用地分析 Agent
            try:
                self._agents["land_use_analysis"] = LandUseAnalysisAgent(self.model_client)
                logger.info("  ✓ 节约集约用地分析 Agent 初始化成功")
            except Exception as e:
                logger.warning(f"  ✗ 节约集约用地分析 Agent 初始化失败: {str(e)}")
            
            # 结论与建议 Agent
            try:
                self._agents["conclusion"] = ConclusionAgent(self.model_client)
                logger.info("  ✓ 结论与建议 Agent 初始化成功")
            except Exception as e:
                logger.warning(f"  ✗ 结论与建议 Agent 初始化失败: {str(e)}")
    
    def get_agent(self, agent_name: str) -> Any:
        """
        获取指定的 Agent
        
        Args:
            agent_name: Agent 名称 (project_overview, site_selection, compliance_analysis)
        
        Returns:
            Agent 实例
        """
        self._initialize_agents()
        
        if agent_name not in self._agents:
            raise ValueError(f"未知的 Agent: {agent_name}")
        
        return self._agents[agent_name]
    
    def generate_chapter_1(self, project_data: Dict[str, Any]) -> str:
        """
        生成第1章：项目概况
        
        Args:
            project_data: 项目数据字典
        
        Returns:
            生成的章节内容 (Markdown 格式)
        """
        logger.info("=" * 60)
        logger.info("生成第1章：项目概况")
        logger.info("=" * 60)
        
        self._initialize_agents()
        
        if "project_overview" not in self._agents:
            raise RuntimeError("项目概况 Agent 未初始化")
        
        agent = self._agents["project_overview"]
        
        # 使用 asyncio 运行异步方法
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 如果已经在异步上下文中，使用 create_task
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    agent.generate(project_data)
                )
                content = future.result()
        else:
            # 否则直接运行
            content = asyncio.run(agent.generate(project_data))
        
        logger.info(f"✓ 第1章生成完成，字数: {len(content)}")
        return content
    
    def generate_chapter_2(
        self,
        site_data: Any,
        context: Optional[str] = None
    ) -> str:
        """
        生成第2章：建设项目选址可行性分析
        
        Args:
            site_data: 选址分析数据 (SiteSelectionData 模型)
            context: 可选的上下文信息
        
        Returns:
            生成的章节内容 (Markdown 格式)
        """
        logger.info("=" * 60)
        logger.info("生成第2章：建设项目选址可行性分析")
        logger.info("=" * 60)
        
        self._initialize_agents()
        
        if "site_selection" not in self._agents:
            raise RuntimeError("选址分析 Agent 未初始化")
        
        agent = self._agents["site_selection"]
        
        # 使用 asyncio 运行异步方法
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    agent.generate(site_data, context)
                )
                content = future.result()
        else:
            content = asyncio.run(agent.generate(site_data, context))
        
        logger.info(f"✓ 第2章生成完成，字数: {len(content)}")
        return content
    
    def generate_chapter_3(
        self,
        compliance_data: Any,
        context: Optional[str] = None
    ) -> str:
        """
        生成第3章：建设项目合法合规性分析
        
        Args:
            compliance_data: 合法合规性分析数据 (ComplianceData 模型)
            context: 可选的上下文信息
        
        Returns:
            生成的章节内容 (Markdown 格式)
        """
        logger.info("=" * 60)
        logger.info("生成第3章：建设项目合法合规性分析")
        logger.info("=" * 60)
        
        self._initialize_agents()
        
        if "compliance_analysis" not in self._agents:
            raise RuntimeError("合规分析 Agent 未初始化")
        
        agent = self._agents["compliance_analysis"]
        
        # 使用 asyncio 运行异步方法
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    agent.generate(compliance_data, context)
                )
                content = future.result()
        else:
            content = asyncio.run(agent.generate(compliance_data, context))
        
        logger.info(f"✓ 第3章生成完成，字数: {len(content)}")
        return content
    
    def generate_chapter_4(
        self,
        rationality_data: Any,
        context: Optional[str] = None
    ) -> str:
        """
        生成第4章：建设项目选址合理性分析
        
        Args:
            rationality_data: 选址合理性分析数据 (RationalityData 模型)
            context: 可选的上下文信息
        
        Returns:
            生成的章节内容 (Markdown 格式)
        """
        logger.info("=" * 60)
        logger.info("生成第4章：建设项目选址合理性分析")
        logger.info("=" * 60)
        
        self._initialize_agents()
        
        if "rationality_analysis" not in self._agents:
            raise RuntimeError("选址合理性分析 Agent 未初始化")
        
        agent = self._agents["rationality_analysis"]
        
        # 使用 asyncio 运行异步方法
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    agent.generate(rationality_data, context)
                )
                content = future.result()
        else:
            content = asyncio.run(agent.generate(rationality_data, context))
        
        logger.info(f"✓ 第4章生成完成，字数: {len(content)}")
        return content
    
    def generate_chapter_5(
        self,
        land_use_data: Any,
        context: Optional[str] = None
    ) -> str:
        """
        生成第5章：建设项目节约集约用地分析
        
        Args:
            land_use_data: 节约集约用地分析数据 (LandUseData 模型)
            context: 可选的上下文信息
        
        Returns:
            生成的章节内容 (Markdown 格式)
        """
        logger.info("=" * 60)
        logger.info("生成第5章：建设项目节约集约用地分析")
        logger.info("=" * 60)
        
        self._initialize_agents()
        
        if "land_use_analysis" not in self._agents:
            raise RuntimeError("节约集约用地分析 Agent 未初始化")
        
        agent = self._agents["land_use_analysis"]
        
        # 使用 asyncio 运行异步方法
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    agent.generate(land_use_data, context)
                )
                content = future.result()
        else:
            content = asyncio.run(agent.generate(land_use_data, context))
        
        logger.info(f"✓ 第5章生成完成，字数: {len(content)}")
        return content
    
    def generate_chapter_6(
        self,
        conclusion_data: Any,
        context: Optional[str] = None
    ) -> str:
        """
        生成第6章：结论与建议
        
        Args:
            conclusion_data: 结论与建议数据 (ConclusionData 模型)
            context: 可选的上下文信息（前5章结论摘要）
        
        Returns:
            生成的章节内容 (Markdown 格式)
        """
        logger.info("=" * 60)
        logger.info("生成第6章：结论与建议")
        logger.info("=" * 60)
        
        self._initialize_agents()
        
        if "conclusion" not in self._agents:
            raise RuntimeError("结论与建议 Agent 未初始化")
        
        agent = self._agents["conclusion"]
        
        # 使用 asyncio 运行异步方法
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    agent.generate(conclusion_data, context)
                )
                content = future.result()
        else:
            content = asyncio.run(agent.generate(conclusion_data, context))
        
        logger.info(f"✓ 第6章生成完成，字数: {len(content)}")
        return content
    def generate_from_excel(self, excel_path: str) -> Dict[str, str]:
        """
        从 Excel 文件生成所有章节
        
        Args:
            excel_path: Excel 文件路径
        
        Returns:
            章节内容字典 {"1": "第一章内容", "2": "第二章内容", ...}
        """
        logger.info(f"从 Excel 生成报告: {excel_path}")
        
        # 延迟导入，避免循环依赖
        from src.services.excel_parser import ExcelParser
        
        chapters = {}
        
        try:
            # 解析 Excel 数据
            parser = ExcelParser(excel_path)
            
            # 生成第1章
            try:
                project_data = parser.parse_project_overview()
                chapters["1"] = self.generate_chapter_1(project_data)
            except Exception as e:
                logger.error(f"第1章生成失败: {str(e)}")
                chapters["1"] = f"[第1章生成失败: {str(e)}]"
            
            # 生成第2章
            try:
                site_data = parser.parse_site_selection()
                context = chapters.get("1", "")[:500]  # 第1章摘要
                chapters["2"] = self.generate_chapter_2(site_data, context)
            except Exception as e:
                logger.error(f"第2章生成失败: {str(e)}")
                chapters["2"] = f"[第2章生成失败: {str(e)}]"
            
            # 生成第3章
            try:
                compliance_data = parser.parse_compliance()
                context = chapters.get("2", "")[:500]  # 第2章摘要
                chapters["3"] = self.generate_chapter_3(compliance_data, context)
            except Exception as e:
                logger.error(f"第3章生成失败: {str(e)}")
                chapters["3"] = f"[第3章生成失败: {str(e)}]"
            
        finally:
            parser.close()
        
        return chapters
    
    def generate_full_report(
        self,
        excel_path: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        从 Excel 文件生成完整报告
        
        Args:
            excel_path: Excel 文件路径
            output_path: 输出路径，如果不指定则使用默认路径
        
        Returns:
            生成的 Word 文档路径
        """
        logger.info("=" * 60)
        logger.info("开始生成完整报告")
        logger.info("=" * 60)
        
        # 生成所有章节
        chapters = self.generate_from_excel(excel_path)
        
        # 延迟导入，避免循环依赖
        from src.services.excel_parser import ExcelParser
        from src.services.document_service import DocumentService
        
        # 获取项目数据用于文档生成
        parser = ExcelParser(excel_path)
        try:
            project_data = parser.parse_project_overview()
        finally:
            parser.close()
        
        # 生成 Word 文档
        doc_service = DocumentService()
        report_path = doc_service.generate_report(
            project_data=project_data,
            chapters=chapters,
            output_path=output_path
        )
        
        logger.info("=" * 60)
        logger.info(f"✓ 完整报告生成成功: {report_path}")
        logger.info("=" * 60)
        
        return report_path


# ============================================================================
# 兼容旧版 API
# ============================================================================

def create_orchestrator(llm_config: Dict[str, Any]) -> AutoGenOrchestrator:
    """
    创建编排器 (兼容旧版 API)
    
    注意: 新版 autogen-agentchat 不再使用 llm_config 字典，
    此函数仅用于向后兼容。
    
    Args:
        llm_config: 旧版 LLM 配置字典
    
    Returns:
        AutoGenOrchestrator 实例
    """
    logger.warning("⚠️  create_orchestrator(llm_config) 已废弃，推荐直接使用 AutoGenOrchestrator()")
    
    # 尝试从 llm_config 提取 model_client
    model_client = llm_config.get("model_client")
    if model_client is None:
        model_client = get_model_client()
    
    return AutoGenOrchestrator(model_client=model_client)


if __name__ == "__main__":
    # 测试编排器初始化
    print("测试 AutoGen 编排器初始化...")
    
    try:
        orchestrator = AutoGenOrchestrator()
        print("\n✓ 编排器初始化成功!")
        print(f"  已注册的 Agent: {list(orchestrator._agents.keys())}")
        
    except Exception as e:
        print(f"\n✗ 编排器初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()