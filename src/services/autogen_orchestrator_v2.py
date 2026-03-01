"""
AutoGen编排器增强版 - 方案A轻量级改进

集成WorkflowExecutor、并行执行、进度追踪和性能指标。
保持向后兼容，原有API不变。
"""

import asyncio
import time
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

from autogen_ext.models.openai import OpenAIChatCompletionClient

from src.utils.logger import logger
from src.core.autogen_config import get_model_client, get_model_info
from src.agents.project_overview_agent import ProjectOverviewAgent
from src.agents.site_selection_agent import SiteSelectionAgent
from src.agents.compliance_analysis_agent import ComplianceAnalysisAgent
from src.agents.rationality_analysis_agent import RationalityAnalysisAgent
from src.agents.land_use_analysis_agent import LandUseAnalysisAgent
from src.agents.conclusion_agent import ConclusionAgent
from src.rag.retriever import Retriever, get_retriever

# 导入新组件
from src.services.orchestrator_config import (
    AgentConfig,
    OrchestratorConfig,
    DEFAULT_AGENT_CONFIGS,
    PARALLEL_GROUPS,
    get_agent_config,
    AGENT_NAME_TO_CHAPTER,
    AGENT_NAME_TO_CHINESE,
)
from src.services.execution_metrics import (
    ExecutionMetrics,
    ProgressTracker,
    ExecutionStatus,
    create_console_progress_callback,
)
from src.services.error_handler import ErrorHandler, handle_agent_error


class AutoGenOrchestratorV2:
    """
    AutoGen编排器增强版（方案A）
    
    核心改进：
    1. 并行执行 - 第2、3章并行，第4、5章并行
    2. 配置化管理 - AgentConfig定义执行参数
    3. 进度追踪 - 实时显示执行进度
    4. 性能指标 - 收集执行时间和重试次数
    5. 错误恢复 - 指数退避重试机制
    
    保持向后兼容：
    - 所有原有方法保留
    - 新增generate_full_report_v2()使用新架构
    """
    
    def __init__(
        self,
        model_client: Optional[OpenAIChatCompletionClient] = None,
        temperature: float = 0.7,
        config: Optional[OrchestratorConfig] = None,
    ):
        """
        初始化增强版编排器
        
        Args:
            model_client: 模型客户端
            temperature: 温度参数
            config: 编排器配置
        """
        # 模型客户端
        if model_client is None:
            self.model_client = get_model_client(temperature=temperature)
        else:
            self.model_client = model_client
        
        # 配置
        self.config = config or OrchestratorConfig()
        
        # Agent存储
        self._agents: Dict[str, Any] = {}
        self._agent_configs: Dict[str, AgentConfig] = {
            cfg.name: cfg for cfg in DEFAULT_AGENT_CONFIGS
        }
        
        # 知识库
        self._retriever: Optional[Retriever] = None
        
        # 新组件
        self._metrics: Optional[ExecutionMetrics] = None
        self._progress: Optional[ProgressTracker] = None
        self._error_handler = ErrorHandler(
            max_retries=self.config.max_retries,
            backoff_base=self.config.retry_backoff_base,
            backoff_max=self.config.retry_backoff_max,
        )
        
        # 初始化日志
        model_info = get_model_info()
        logger.info("=" * 60)
        logger.info("AutoGen编排器增强版(V2)初始化完成")
        logger.info(f"  提供商: {model_info['provider']}")
        logger.info(f"  模型: {model_info['model']}")
        logger.info(f"  执行模式: {self.config.mode.value}")
        logger.info(f"  最大重试: {self.config.max_retries}")
        logger.info("=" * 60)
    
    def _initialize_agents(self):
        """延迟初始化Agent"""
        if self._agents:
            return
        
        logger.info("初始化Agent...")
        
        agent_classes = {
            "project_overview": ProjectOverviewAgent,
            "site_selection": SiteSelectionAgent,
            "compliance_analysis": ComplianceAnalysisAgent,
            "rationality_analysis": RationalityAnalysisAgent,
            "land_use_analysis": LandUseAnalysisAgent,
            "conclusion": ConclusionAgent,
        }
        
        for name, agent_class in agent_classes.items():
            try:
                self._agents[name] = agent_class(self.model_client)
                logger.info(f"  ✓ {name} Agent初始化成功")
            except Exception as e:
                logger.error(f"  ✗ {name} Agent初始化失败: {e}")
                raise
    
    def get_agent(self, name: str) -> Any:
        """获取Agent实例"""
        self._initialize_agents()
        if name not in self._agents:
            raise ValueError(f"未知的Agent: {name}")
        return self._agents[name]
    
    def get_retriever(self) -> Retriever:
        """获取知识库检索服务"""
        if self._retriever is None:
            self._retriever = get_retriever()
        return self._retriever
    
    def set_retriever(self, retriever: Retriever):
        """
        设置知识库检索服务
        
        Args:
            retriever: Retriever 实例
        """
        self._retriever = retriever
        logger.info("知识库检索服务已设置")
    # ==========================================================================
    # 核心：并行执行工作流
    # ==========================================================================
    
    async def execute_workflow(
        self,
        excel_path: str,
        enable_progress: bool = True,
        progress_callback: Optional[Any] = None,
        selected_chapters: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        执行完整工作流（并行优化版）
        
        执行顺序：
        1. 第1章（项目概况）- 单独执行
        2. 第2、3章并行（选址分析、合规分析）
        3. 第4、5章并行（合理性分析、节地分析）
        4. 第6章（结论）- 单独执行
        
        Args:
            excel_path: Excel文件路径
            enable_progress: 是否启用进度追踪
            progress_callback: 进度回调函数
            selected_chapters: 指定生成的章节列表，如 ['1', '2', '3']。None表示全部
            
        Returns:
            执行结果字典
        """
        from src.services.excel_parser import ExcelParser
        
        # 初始化
        self._initialize_agents()
        
        # 创建性能指标收集器
        self._metrics = ExecutionMetrics()
        self._metrics.start(f"workflow_{int(time.time())}")
        
        # 创建进度追踪器
        if enable_progress:
            self._progress = ProgressTracker(total_steps=6)
            if progress_callback:
                self._progress.register_callback(progress_callback)
            else:
                self._progress.register_callback(create_console_progress_callback())
            self._progress.start()
        
        results: Dict[str, str] = {}
        chapters_data: Dict[str, Any] = {}
        
        try:
            # 解析Excel
            logger.info("解析Excel数据...")
            parser = ExcelParser(excel_path)
            try:
                chapters_data = {
                    "project_overview": parser.parse_project_overview(),
                    "site_selection": parser.parse_site_selection(),
                    "compliance_analysis": parser.parse_compliance(),
                    "rationality_analysis": parser.parse_rationality(),
                    "land_use_analysis": parser.parse_land_use(),
                    "conclusion": parser.parse_conclusion(),
                }
            finally:
                parser.close()
            
            # 按并行组执行
            for group_idx, group in enumerate(PARALLEL_GROUPS, 1):
                # 过滤掉不在selected_chapters中的agent
                if selected_chapters:
                    filtered_group = [
                        agent_name for agent_name in group
                        if AGENT_NAME_TO_CHAPTER.get(agent_name) in selected_chapters
                    ]
                    if not filtered_group:
                        continue  # 这一组的章节都被跳过
                    group = filtered_group
                
                group_names = [AGENT_NAME_TO_CHINESE.get(n, n) for n in group]
                logger.info(f"\n执行第{group_idx}组: {' + '.join(group_names)}")
                if len(group) == 1:
                    # 单Agent顺序执行
                    agent_name = group[0]
                    data = chapters_data[agent_name]
                    result = await self._execute_agent(
                        agent_name=agent_name,
                        data=data,
                        context=None,
                    )
                    chapter_num = AGENT_NAME_TO_CHAPTER[agent_name]
                    results[chapter_num] = result
                    logger.info(f"存储结果: {agent_name} -> 章节{chapter_num}, 类型: {type(result)}, 长度: {len(str(result)) if result else 0}")
                else:
                    tasks = []
                    for agent_name in group:
                        context = self._build_context(agent_name, results)
                        data = chapters_data[agent_name]
                        task = self._execute_agent_async(
                            agent_name=agent_name,
                            data=data,
                            context=context,
                        )
                        tasks.append((agent_name, task))
                    
                    # 等待所有并行任务完成
                    parallel_results = await asyncio.gather(
                        *[task for _, task in tasks],
                        return_exceptions=True
                    )
                    
                    # 处理结果
                    for (agent_name, _), result in zip(tasks, parallel_results):
                        chapter_num = AGENT_NAME_TO_CHAPTER[agent_name]
                        if isinstance(result, Exception):
                            logger.error(f"{agent_name} 执行失败: {result}")
                            results[chapter_num] = f"[生成失败: {result}]"
                        else:
                            results[chapter_num] = result
            
            # 记录完成
            self._metrics.end()
            if self._progress:
                logger.info("\n" + "=" * 60)
                logger.info("所有章节生成完成！")
            
            return {
                "success": True,
                "chapters": results,
                "metrics": self._metrics.get_summary(),
            }
            
        except Exception as e:
            import traceback
            logger.error(f"工作流执行失败: {e}\n{traceback.format_exc()}")
            if self._metrics:
                self._metrics.end()
            raise
    
    async def _execute_agent(
        self,
        agent_name: str,
        data: Any,
        context: Optional[str] = None,
    ) -> str:
        """
        执行单个Agent（同步包装）
        
        Args:
            agent_name: Agent名称
            data: 输入数据
            context: 上下文信息
            
        Returns:
            生成的内容
        """
        config = self._agent_configs[agent_name]
        chinese_name = AGENT_NAME_TO_CHINESE.get(agent_name, agent_name)
        
        # 更新进度
        if self._progress:
            self._progress.update_step_start(chinese_name)
        
        # 记录开始
        if self._metrics:
            self._metrics.record_start(agent_name)
        
        # 执行（带重试）
        last_error = None
        for attempt in range(config.retry):
            try:
                agent = self.get_agent(agent_name)
                
                # 调试：打印agent类型和generate方法
                logger.debug(f"Agent {agent_name}: type={type(agent)}, has_generate={hasattr(agent, 'generate')}, generate_type={type(agent.generate) if hasattr(agent, 'generate') else None}")
                
                # 特殊处理：只有project_overview_agent需要字典，其他Agent需要Pydantic对象
                if agent_name == "project_overview" and hasattr(data, 'model_dump'):
                    data = data.model_dump()
                
                # 调用Agent生成
                # 调用Agent生成
                if hasattr(agent, 'generate'):
                    if asyncio.iscoroutinefunction(agent.generate):
                        result = await asyncio.wait_for(
                            agent.generate(data),  # 只传递data参数
                            timeout=config.timeout
                        )
                    else:
                        result = agent.generate(data)  # 只传递data参数
                else:
                    raise RuntimeError(f"Agent {agent_name} 没有generate方法")
                # 记录成功
                if self._metrics:
                    try:
                        self._metrics.record_end(agent_name, len(str(result)))
                    except Exception as e:
                        logger.error(f"记录指标失败: {e}, result type: {type(result)}, result value: {result}")
                if self._progress:
                    self._progress.update_step_complete(chinese_name)
                
                # 调试：记录返回值
                logger.debug(f"Agent {agent_name} 返回值类型: {type(result)}, 长度: {len(str(result)) if result else 0}")
                return result
            except Exception as e:
                last_error = e
                
                # 判断是否重试
                if attempt < config.retry - 1 and self._error_handler.should_retry(e, attempt):
                    delay = self._error_handler.calculate_backoff(attempt + 1)
                    logger.warning(f"{agent_name} 失败，{delay:.1f}秒后重试: {e}")
                    
                    if self._metrics:
                        self._metrics.record_retry(agent_name)
                    if self._progress:
                        self._progress.update_step_retry(chinese_name, attempt + 1)
                    
                    await asyncio.sleep(delay)
                else:
                    break
        
        # 记录失败
        error_msg = str(last_error)
        if self._metrics:
            self._metrics.record_failure(agent_name, error_msg)
        if self._progress:
            self._progress.update_step_failed(chinese_name, error_msg)
        
        raise last_error
    
    async def _execute_agent_async(
        self,
        agent_name: str,
        data: Any,
        context: Optional[str] = None,
    ) -> str:
        """异步执行Agent的包装"""
        return await self._execute_agent(agent_name, data, context)
    
    def _build_context(self, agent_name: str, results: Dict[str, str]) -> Optional[str]:
        """
        构建上下文信息
        
        根据依赖关系，从前面的章节提取摘要作为上下文。
        
        Args:
            agent_name: 当前Agent名称
            results: 已完成的章节结果
            
        Returns:
            上下文字符串
        """
        config = self._agent_configs.get(agent_name)
        if not config or not config.dependencies:
            return None
        
        contexts = []
        for dep in config.dependencies:
            chapter_num = AGENT_NAME_TO_CHAPTER.get(dep)
            if chapter_num and chapter_num in results:
                content = results[chapter_num]
                if not content:  # 检查None或空字符串
                    logger.warning(f"章节{chapter_num}的内容为空，跳过上下文构建")
                    continue
                # 取前500字符作为摘要
                summary = content[:500] if len(content) > 500 else content
                dep_chinese = AGENT_NAME_TO_CHINESE.get(dep, dep)
                contexts.append(f"## {dep_chinese}\n{summary}\n")
        
        return "\n".join(contexts) if contexts else None
    
    # ==========================================================================
    # 公共API（保持向后兼容）
    # ==========================================================================
    
    def generate_full_report_v2(
        self,
        excel_path: str,
        output_path: Optional[str] = None,
        enable_progress: bool = True,
    ) -> str:
        """
        生成完整报告（增强版）
        
        使用并行执行优化，支持进度追踪。
        
        Args:
            excel_path: Excel文件路径
            output_path: 输出路径
            enable_progress: 是否显示进度
            
        Returns:
            生成的Word文档路径
        """
        logger.info("=" * 60)
        logger.info("开始生成完整报告（增强版）")
        logger.info("=" * 60)
        
        # 执行工作流
        result = self._run_async(
            self.execute_workflow(excel_path, enable_progress)
        )
        
        if not result["success"]:
            raise RuntimeError("工作流执行失败")
        
        chapters = result["chapters"]
        
        # 生成Word文档
        from src.services.excel_parser import ExcelParser
        from src.services.document_service import DocumentService
        
        parser = ExcelParser(excel_path)
        try:
            project_data = parser.parse_project_overview()
        finally:
            parser.close()
        
        doc_service = DocumentService()
        report_path = doc_service.generate_report(
            project_data=project_data,
            chapters=chapters,
            output_path=output_path
        )
        
        # 打印性能摘要
        if self._metrics:
            self._metrics.print_summary()
        
        logger.info("=" * 60)
        logger.info(f"✓ 报告生成成功: {report_path}")
        logger.info("=" * 60)
        
        return report_path
    
    def get_metrics(self) -> Optional[Dict[str, Any]]:
        """获取性能指标"""
        if self._metrics:
            return self._metrics.get_summary()
        return None
    
    def get_progress(self) -> Optional[Dict[str, Any]]:
        """获取当前进度"""
        if self._progress:
            return self._progress.get_progress()
        return None
    
    def _run_async(self, coro):
        """安全地运行异步协程（兼容代码）"""
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result()
        except RuntimeError:
            return asyncio.run(coro)


# ==========================================================================
# 便捷函数
# ==========================================================================

def create_orchestrator_v2(
    model_client: Optional[OpenAIChatCompletionClient] = None,
    temperature: float = 0.7,
    **kwargs
) -> AutoGenOrchestratorV2:
    """
    创建增强版编排器
    
    Args:
        model_client: 模型客户端
        temperature: 温度参数
        **kwargs: 其他配置参数
        
    Returns:
        AutoGenOrchestratorV2实例
    """
    config = OrchestratorConfig(**kwargs)
    return AutoGenOrchestratorV2(
        model_client=model_client,
        temperature=temperature,
        config=config,
    )


# 测试代码
if __name__ == "__main__":
    print("测试 AutoGenOrchestratorV2...")
    
    try:
        # 创建编排器
        orchestrator = create_orchestrator_v2()
        print("\n✓ 编排器初始化成功")
        
        # 打印配置
        print(f"\n配置信息:")
        print(f"  模式: {orchestrator.config.mode.value}")
        print(f"  最大重试: {orchestrator.config.max_retries}")
        print(f"  退避基数: {orchestrator.config.retry_backoff_base}")
        
        # 打印并行组
        print(f"\n并行执行组:")
        for i, group in enumerate(PARALLEL_GROUPS, 1):
            names = [AGENT_NAME_TO_CHINESE.get(n, n) for n in group]
            print(f"  第{i}组: {' + '.join(names)}")
        
        print("\n✅ 测试完成")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
