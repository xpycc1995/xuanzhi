"""
节约集约用地分析Agent - 基于AutoGen (新版 autogen-agentchat API)

负责生成规划选址论证报告的第5章"建设项目节约集约用地分析"。
"""

import os
from typing import Dict, Any, Optional
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

from src.models.land_use_data import LandUseData
from src.utils.logger import logger
from src.tools.knowledge_tools import (
    search_regulations,
    search_cases,
    search_technical_standards,
)


class LandUseAnalysisAgent:
    """
    节约集约用地分析Agent

    使用AutoGen的AssistantAgent，专门负责生成第5章"节约集约用地分析"内容。

    该Agent需要处理的数据包括：
    - 功能分区情况
    - 用地规模合理性
    - 采用的节地技术
    - 案例对比情况
    - 节约集约用地小结
    
    Wave 5 更新:
    - 集成知识库检索工具
    - 支持检索法规标准、案例参考和技术标准
    """

    def __init__(
        self,
        model_client: OpenAIChatCompletionClient,
        prompt_template_path: str = None
    ):
        """
        初始化节约集约用地分析Agent

        Args:
            model_client: OpenAIChatCompletionClient 实例
            prompt_template_path: 提示词模板路径，默认为templates/prompts/land_use_analysis.md
        """
        self.model_client = model_client

        # 设置默认提示词模板路径
        if prompt_template_path is None:
            # 获取项目根目录
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            prompt_template_path = os.path.join(
                project_root,
                "templates",
                "prompts",
                "land_use_analysis.md"
            )

        # 加载system_message
        self.system_message = self._load_system_message(prompt_template_path)
        self.template_path = prompt_template_path

        # 创建AutoGen AssistantAgent (带知识库工具)
        self.agent = AssistantAgent(
            name="land_use_analysis_agent",
            model_client=self.model_client,
            system_message=self.system_message,
            description="负责生成规划选址论证报告第5章'建设项目节约集约用地分析'的专业AI Agent",
            tools=[search_regulations, search_cases, search_technical_standards],
        )

        logger.info(f"节约集约用地分析Agent初始化完成")
        logger.info(f"  提示词模板: {prompt_template_path}")

    def _load_system_message(self, template_path: str) -> str:
        """
        加载提示词模板作为system_message

        Args:
            template_path: 提示词模板文件路径

        Returns:
            system_message字符串
        """
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                system_message = f.read()

            logger.info(f"提示词模板加载成功 ({len(system_message)} 字符)")
            return system_message

        except FileNotFoundError:
            raise FileNotFoundError(
                f"提示词模板文件不存在: {template_path}\n"
                f"请确保模板文件存在于正确位置。"
            )
        except Exception as e:
            raise RuntimeError(f"加载提示词模板失败: {str(e)}")

    def _validate_data(self, data: LandUseData):
        """
        验证输入数据

        Args:
            data: 节约集约用地分析数据

        Raises:
            ValueError: 数据验证失败
        """
        # Pydantic已经做了基本验证，这里做业务逻辑验证
        if not data.功能分区情况:
            raise ValueError("功能分区情况不能为空")

        if not data.用地规模合理性:
            raise ValueError("用地规模合理性数据不能为空")

        if not data.采用的节地技术:
            raise ValueError("节地技术数据不能为空")

        if not data.案例对比情况:
            raise ValueError("案例对比数据不能为空")

        logger.info("数据验证通过")

    def _build_user_message(
        self,
        land_use_data: LandUseData,
        context: str = None
    ) -> str:
        """
        构建发送给Agent的用户消息

        Args:
            land_use_data: 节约集约用地分析数据
            context: 可选的上下文信息

        Returns:
            格式化的用户消息字符串
        """
        lines = []

        # 添加项目基本信息
        lines.append("# 项目基本信息")
        for key, value in land_use_data.项目基本信息.items():
            lines.append(f"- {key}：{value}")

        # 添加功能分区情况
        lines.append("\n# 功能分区情况")
        for zone in land_use_data.功能分区情况:
            lines.append(f"\n## {zone.分区名称}")
            lines.append(f"- 面积：{zone.分区面积}平方米")
            lines.append(f"- 占比：{zone.占比}%")
            if zone.功能描述:
                lines.append(f"- 功能描述：{zone.功能描述}")
            if zone.用地依据:
                lines.append(f"- 用地依据：{zone.用地依据}")
            if zone.子分区:
                lines.append("- 子分区情况：")
                for sub in zone.子分区:
                    for k, v in sub.items():
                        lines.append(f"  - {k}：{v}")

        # 添加用地规模合理性
        lines.append("\n# 用地规模合理性")
        overall = land_use_data.用地规模合理性.总体指标
        lines.append(f"\n## 项目用地总体指标情况")
        lines.append(f"- 项目总用地面积：{overall.项目总用地面积}平方米")
        lines.append(f"- 建设规模：{overall.建设规模}")
        lines.append(f"- 标准依据：{overall.标准依据}")
        lines.append(f"- 标准要求范围：{overall.标准要求范围}")
        lines.append(f"- 是否符合要求：{'是' if overall.是否符合要求 else '否'}")
        if overall.对比分析:
            lines.append(f"- 对比分析：{overall.对比分析}")

        lines.append(f"\n## 各功能分区用地指标情况")
        for indicator in land_use_data.用地规模合理性.各分区指标:
            lines.append(f"\n### {indicator.区域名称}")
            lines.append(f"- 实际用地面积：{indicator.实际用地面积}平方米")
            lines.append(f"- 标准依据：{indicator.标准依据}")
            lines.append(f"- 标准指标值：{indicator.标准指标值}")
            lines.append(f"- 是否符合要求：{'是' if indicator.是否符合要求 else '否'}")
            if indicator.对比分析:
                lines.append(f"- 对比分析：{indicator.对比分析}")

        if land_use_data.用地规模合理性.辅助区用地占比:
            lines.append(f"\n## 辅助区用地占比分析")
            for key, value in land_use_data.用地规模合理性.辅助区用地占比.items():
                lines.append(f"- {key}：{value}")

        if land_use_data.用地规模合理性.综合评价:
            lines.append(f"\n## 综合评价")
            lines.append(land_use_data.用地规模合理性.综合评价)

        # 添加节地技术
        lines.append("\n# 采用的节地技术")
        lines.append(f"\n## 前期工作阶段")
        for measure in land_use_data.采用的节地技术.前期工作阶段措施:
            lines.append(f"\n### {measure.措施名称}")
            lines.append(f"- 措施描述：{measure.措施描述}")
            if measure.实施效果:
                lines.append(f"- 实施效果：{measure.实施效果}")

        lines.append(f"\n## 建设实施阶段")
        for measure in land_use_data.采用的节地技术.建设实施阶段措施:
            lines.append(f"\n### {measure.措施名称}")
            lines.append(f"- 措施描述：{measure.措施描述}")
            if measure.实施主体:
                lines.append(f"- 实施主体：{measure.实施主体}")
            if measure.实施效果:
                lines.append(f"- 实施效果：{measure.实施效果}")

        if land_use_data.采用的节地技术.综合评价:
            lines.append(f"\n## 节地技术综合评价")
            lines.append(land_use_data.采用的节地技术.综合评价)

        # 添加案例对比
        lines.append("\n# 案例对比情况")
        lines.append(f"\n## 本项目")
        project = land_use_data.案例对比情况.本项目
        lines.append(f"- 案例名称：{project.案例名称}")
        lines.append(f"- 建设规模：{project.建设规模}")
        lines.append(f"- 用地面积：{project.用地面积}平方米")
        lines.append(f"- 总投资：{project.总投资}万元")
        if project.采用技术:
            lines.append(f"- 采用技术：{project.采用技术}")

        lines.append(f"\n## 对比案例")
        for i, case in enumerate(land_use_data.案例对比情况.对比案例, 1):
            lines.append(f"\n### 案例{i}：{case.案例名称}")
            if case.案例地点:
                lines.append(f"- 案例地点：{case.案例地点}")
            lines.append(f"- 建设规模：{case.建设规模}")
            lines.append(f"- 用地面积：{case.用地面积}平方米")
            lines.append(f"- 总投资：{case.总投资}万元")
            if case.采用技术:
                lines.append(f"- 采用技术：{case.采用技术}")
            if case.数据来源:
                lines.append(f"- 数据来源：{case.数据来源}")

        lines.append(f"\n## 对比结论")
        lines.append(land_use_data.案例对比情况.对比结论)

        if land_use_data.案例对比情况.单位投资对比:
            lines.append(f"\n### 单位用地投资量对比")
            for key, value in land_use_data.案例对比情况.单位投资对比.items():
                lines.append(f"- {key}：{value}万元/平方米")

        # 添加小结
        if land_use_data.节约集约用地小结:
            lines.append(f"\n# 节约集约用地分析小结")
            lines.append(land_use_data.节约集约用地小结)

        # 添加数据来源
        if land_use_data.数据来源:
            lines.append(f"\n# 数据来源")
            lines.append(land_use_data.数据来源)

        # 添加任务指令
        lines.append("\n" + "=" * 60)
        lines.append("请根据以上提供的数据，严格按照提示词模板的要求，")
        lines.append("生成第5章《建设项目节约集约用地分析》的完整内容。")
        lines.append("=" * 60)

        user_message = "\n".join(lines)
        logger.info(f"用户消息构建完成 ({len(user_message)} 字符)")

        return user_message

    def get_agent(self) -> AssistantAgent:
        """
        获取AutoGen Agent实例

        Returns:
            AutoGen AssistantAgent实例
        """
        return self.agent

    def get_agent_info(self) -> Dict[str, Any]:
        """
        获取Agent信息

        Returns:
            Agent信息字典
        """
        return {
            "name": self.agent.name,
            "description": self.agent.description,
            "system_message_length": len(self.system_message),
            "template_path": self.template_path,
        }

    async def generate(
        self,
        land_use_data: LandUseData,
        context: str = None
    ) -> str:
        """
        生成第5章：节约集约用地分析

        Args:
            land_use_data: 节约集约用地分析数据（LandUseData模型）
            context: 可选的上下文信息（如前几章的摘要）

        Returns:
            生成的第5章内容（Markdown格式）
        """
        logger.info("开始生成第5章：节约集约用地分析")
        logger.info(f"  项目名称：{land_use_data.项目基本信息.get('项目名称', '未知')}")
        logger.info(f"  功能分区数量：{len(land_use_data.功能分区情况)}")
        logger.info(f"  对比案例数量：{len(land_use_data.案例对比情况.对比案例)}")

        try:
            # 1. 数据验证
            self._validate_data(land_use_data)

            # 2. 构建用户消息
            user_message = self._build_user_message(land_use_data, context)

            # 3. 调用Agent生成内容
            result = await self.agent.run(task=user_message)

            # 4. 提取响应内容
            if result and result.messages:
                last_message = result.messages[-1]
                if isinstance(last_message, TextMessage):
                    content = last_message.content
                else:
                    content = str(last_message.content)

                logger.info(f"第5章生成成功，字数: {len(content)}")
                return content
            else:
                raise ValueError("Agent没有返回任何内容")

        except Exception as e:
            logger.error(f"第5章生成失败: {str(e)}")
            raise

    async def generate_stream(
        self,
        land_use_data: LandUseData,
        context: str = None
    ):
        """
        流式生成第5章内容

        Args:
            land_use_data: 节约集约用地分析数据
            context: 可选的上下文信息

        Yields:
            消息流
        """
        logger.info("开始流式生成第5章：节约集约用地分析")

        self._validate_data(land_use_data)
        user_message = self._build_user_message(land_use_data, context)

        async for message in self.agent.run_stream(task=user_message):
            yield message


# 测试代码
if __name__ == "__main__":
    import asyncio

    async def test_agent():
        print("测试节约集约用地分析Agent初始化...")

        try:
            from src.core.autogen_config import get_model_client
            from src.models.land_use_data import get_sample_data

            # 获取模型客户端
            model_client = get_model_client()

            # 初始化Agent
            agent = LandUseAnalysisAgent(model_client)

            # 获取Agent信息
            info = agent.get_agent_info()
            print("\n✓ Agent初始化成功!")
            print(f"  Agent名称: {info['name']}")
            print(f"  模板路径: {info['template_path']}")
            print(f"  System Message长度: {info['system_message_length']} 字符")

            # 测试用户消息构建
            print("\n测试用户消息构建...")
            test_data = get_sample_data()
            user_message = agent._build_user_message(test_data)
            print(f"✓ 用户消息构建成功 ({len(user_message)} 字符)")

            # 显示前500字符
            print("\n用户消息预览：")
            print(user_message[:500])

        except Exception as e:
            print(f"\n✗ Agent初始化失败: {str(e)}")
            import traceback
            traceback.print_exc()

    asyncio.run(test_agent())