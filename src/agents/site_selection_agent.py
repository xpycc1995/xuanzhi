"""
选址分析Agent - 基于AutoGen (新版 autogen-agentchat API)

负责生成规划选址论证报告的第2章"建设项目选址可行性分析"。
"""

import os
from typing import Dict, Any, Optional
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

from src.models.site_selection_data import SiteSelectionData
from src.utils.logger import logger


class SiteSelectionAgent:
    """
    选址分析Agent

    使用AutoGen的AssistantAgent，专门负责生成第2章"选址可行性分析"内容。

    该Agent需要处理复杂的选址数据，包括：
    - 备选方案信息
    - 场地自然条件
    - 外部配套条件
    - 选址敏感条件
    - 施工运营条件
    - 规划影响条件
    - 征求意见情况
    - 方案比选
    """

    def __init__(
        self,
        model_client: OpenAIChatCompletionClient,
        prompt_template_path: str = None
    ):
        """
        初始化选址分析Agent

        Args:
            model_client: OpenAIChatCompletionClient 实例
            prompt_template_path: 提示词模板路径，默认为templates/prompts/site_selection.md
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
                "site_selection.md"
            )

        # 加载system_message
        self.system_message = self._load_system_message(prompt_template_path)
        self.template_path = prompt_template_path

        # 创建AutoGen AssistantAgent
        self.agent = AssistantAgent(
            name="site_selection_agent",
            model_client=self.model_client,
            system_message=self.system_message,
            description="负责生成规划选址论证报告第2章'建设项目选址可行性分析'的专业AI Agent"
        )

        logger.info(f"选址分析Agent初始化完成")
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

    def _validate_data(self, data: SiteSelectionData):
        """
        验证输入数据

        Args:
            data: 选址分析数据

        Raises:
            ValueError: 数据验证失败
        """
        # Pydantic已经做了基本验证，这里做业务逻辑验证
        if not data.备选方案 or len(data.备选方案) < 2:
            raise ValueError("至少需要2个备选方案")

        if not data.选址原则 or len(data.选址原则) < 5:
            raise ValueError("至少需要5条选址原则")

        logger.info("数据验证通过")

    def _build_user_message(
        self,
        project_data: SiteSelectionData,
        context: str = None
    ) -> str:
        """
        构建发送给Agent的用户消息

        Args:
            project_data: 选址分析数据
            context: 可选的上下文信息

        Returns:
            格式化的用户消息字符串
        """
        lines = []

        # 添加项目基本信息
        lines.append("# 项目基本信息")
        for key, value in project_data.项目基本信息.items():
            lines.append(f"{key}：{value}")

        # 添加选址原则
        lines.append("\n# 选址原则")
        for i, principle in enumerate(project_data.选址原则, 1):
            lines.append(f"{i}. {principle}")

        # 添加备选方案
        lines.append("\n# 备选方案")
        for alt in project_data.备选方案:
            lines.append(f"\n## {alt.方案名称}")
            lines.append(f"- 方案编号：{alt.方案编号}")
            lines.append(f"- 位置：{alt.位置}")
            lines.append(f"- 面积：{alt.面积}平方米")

            if alt.四至范围:
                lines.append(f"- 四至范围：")
                for direction, desc in alt.四至范围.items():
                    lines.append(f"  - {direction}：{desc}")

            if alt.土地利用现状:
                lines.append(f"- 土地利用现状：")
                for land_type, area in alt.土地利用现状.items():
                    lines.append(f"  - {land_type}：{area}")

            lines.append(f"- 是否占用耕地：{'是' if alt.是否占用耕地 else '否'}")
            lines.append(f"- 是否占用永久基本农田：{'是' if alt.是否占用永久基本农田 else '否'}")
            lines.append(f"- 是否涉及未利用地：{'是' if alt.是否涉及未利用地 else '否'}")
            lines.append(f"- 建设内容：{alt.建设内容}")

            if alt.工艺流程:
                lines.append(f"- 工艺流程：{alt.工艺流程}")
            if alt.出水标准:
                lines.append(f"- 出水标准：{alt.出水标准}")

        # 添加场地自然条件
        lines.append("\n# 场地自然条件")
        conditions = project_data.场地自然条件
        lines.append(f"## 地形地貌")
        for key, value in conditions.地形地貌.items():
            lines.append(f"- {key}：{value}")

        lines.append(f"\n## 气候")
        for key, value in conditions.气候.items():
            lines.append(f"- {key}：{value}")

        lines.append(f"\n## 区域地质构造")
        for key, value in conditions.区域地质构造.items():
            lines.append(f"- {key}：{value}")

        lines.append(f"\n## 水文地质条件")
        for key, value in conditions.水文地质条件.items():
            lines.append(f"- {key}：{value}")

        lines.append(f"\n## 工程地质")
        for key, value in conditions.工程地质.items():
            lines.append(f"- {key}：{value}")

        lines.append(f"\n## 地震")
        for key, value in conditions.地震.items():
            lines.append(f"- {key}：{value}")

        # 添加外部配套条件
        lines.append("\n# 外部配套条件")
        ext_conditions = project_data.外部配套条件
        lines.append(f"- 周边建筑物：{ext_conditions.周边建筑物}")
        lines.append(f"- 供水：{ext_conditions.供水}")
        lines.append(f"- 供电：{ext_conditions.供电}")
        lines.append(f"- 通讯：{ext_conditions.通讯}")
        lines.append(f"- 交通：{ext_conditions.交通}")
        lines.append(f"- 建材来源：{ext_conditions.建材来源}")
        lines.append(f"- 是否压覆文物：{'是' if ext_conditions.是否压覆文物 else '否'}")
        lines.append(f"- 是否影响防洪：{'是' if ext_conditions.是否影响防洪 else '否'}")

        # 添加选址敏感条件
        lines.append("\n# 选址敏感条件")
        sensitive = project_data.选址敏感条件
        lines.append(f"## 历史保护情况")
        for key, value in sensitive.历史保护.items():
            lines.append(f"- {key}：{'是' if value else '否'}")

        lines.append(f"\n## 生态保护情况")
        for key, value in sensitive.生态保护.items():
            lines.append(f"- {key}：{value}")

        lines.append(f"\n## 矿产资源情况")
        for key, value in sensitive.矿产资源.items():
            lines.append(f"- {key}：{'是' if value else '否'}")

        lines.append(f"\n## 安全防护情况")
        for key, value in sensitive.安全防护.items():
            lines.append(f"- {key}：{'是' if value else '否'}")

        lines.append(f"\n## 重要设施影响")
        for key, value in sensitive.重要设施.items():
            lines.append(f"- {key}：{value}")

        lines.append(f"\n## 占用耕地和永久基本农田情况")
        for key, value in sensitive.耕地和基本农田.items():
            lines.append(f"- {key}：{'是' if value else '否'}")

        lines.append(f"\n## 占用生态保护红线情况")
        for key, value in sensitive.生态保护红线.items():
            lines.append(f"- {key}：{'是' if value else '否'}")

        # 添加施工运营条件
        lines.append("\n# 施工运营条件")
        construction = project_data.施工运营条件
        lines.append(f"- 方案一总投资：{construction.方案一总投资}")
        lines.append(f"- 方案二总投资：{construction.方案二总投资}")
        lines.append(f"- 政府支持：{construction.政府支持}")
        lines.append(f"- 群众支持：{construction.群众支持}")
        if construction.征地拆迁:
            lines.append(f"- 征地拆迁：{construction.征地拆迁}")
        lines.append(f"- 施工难度：{construction.施工难度}")
        lines.append(f"- 材料供应：{construction.材料供应}")

        # 添加规划影响
        lines.append("\n# 规划影响条件")
        planning = project_data.规划影响
        lines.append(f"- 是否符合国土空间总体规划：{'是' if planning.是否符合国土空间总体规划 else '否'}")
        lines.append(f"- 是否列入重点项目库：{'是' if planning.是否列入重点项目库 else '否'}")
        if planning.重点项目库名称:
            lines.append(f"- 重点项目库名称：{planning.重点项目库名称}")
        lines.append(f"- 对区域发展作用：{planning.对区域发展作用}")

        # 添加征求意见情况
        lines.append("\n# 征求意见情况")
        for opinion in project_data.征求意见情况:
            lines.append(f"\n## {opinion.部门}意见")
            lines.append(f"- 日期：{opinion.日期}")
            lines.append(f"- 复函标题：《{opinion.复函标题}》")
            lines.append(f"- 结论：{opinion.结论}")

        # 添加方案比选
        lines.append("\n# 方案比选")
        comparison = project_data.方案比选
        lines.append(f"## 比选因子")
        for i, factor in enumerate(comparison.比选因子, 1):
            lines.append(f"{i}. {factor}")

        lines.append(f"\n## 推荐方案")
        lines.append(f"- 推荐方案：{comparison.推荐方案}")

        lines.append(f"\n## 推荐理由")
        for i, reason in enumerate(comparison.推荐理由, 1):
            lines.append(f"{i}. {reason}")

        # 添加数据来源
        if project_data.数据来源:
            lines.append(f"\n# 数据来源")
            lines.append(project_data.数据来源)

        # 添加任务指令
        lines.append("\n" + "=" * 60)
        lines.append("请根据以上提供的数据，严格按照提示词模板的要求，")
        lines.append("生成第2章《建设项目选址可行性分析》的完整内容。")
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
        project_data: SiteSelectionData,
        context: str = None
    ) -> str:
        """
        生成第2章：选址可行性分析

        Args:
            project_data: 选址分析数据（SiteSelectionData模型）
            context: 可选的上下文信息（如第1章的摘要）

        Returns:
            生成的第2章内容（Markdown格式）
        """
        logger.info("开始生成第2章：选址可行性分析")
        logger.info(f"  项目名称：{project_data.项目基本信息.get('项目名称', '未知')}")
        logger.info(f"  备选方案数量：{len(project_data.备选方案)}")

        try:
            # 1. 数据验证
            self._validate_data(project_data)

            # 2. 构建用户消息
            user_message = self._build_user_message(project_data, context)

            # 3. 调用Agent生成内容
            result = await self.agent.run(task=user_message)

            # 4. 提取响应内容
            if result and result.messages:
                last_message = result.messages[-1]
                if isinstance(last_message, TextMessage):
                    content = last_message.content
                else:
                    content = str(last_message.content)

                logger.info(f"第2章生成成功，字数: {len(content)}")
                return content
            else:
                raise ValueError("Agent没有返回任何内容")

        except Exception as e:
            logger.error(f"第2章生成失败: {str(e)}")
            raise

    async def generate_stream(
        self,
        project_data: SiteSelectionData,
        context: str = None
    ):
        """
        流式生成第2章内容

        Args:
            project_data: 选址分析数据
            context: 可选的上下文信息

        Yields:
            消息流
        """
        logger.info("开始流式生成第2章：选址可行性分析")

        self._validate_data(project_data)
        user_message = self._build_user_message(project_data, context)

        async for message in self.agent.run_stream(task=user_message):
            yield message


# 测试代码
if __name__ == "__main__":
    import asyncio

    async def test_agent():
        print("测试选址分析Agent初始化...")

        try:
            from src.core.autogen_config import get_model_client
            from src.models.site_selection_data import get_sample_data

            # 获取模型客户端
            model_client = get_model_client()

            # 初始化Agent
            agent = SiteSelectionAgent(model_client)

            # 获取Agent信息
            info = agent.get_agent_info()
            print("\nOK - Agent初始化成功!")
            print(f"  Agent名称: {info['name']}")
            print(f"  模板路径: {info['template_path']}")
            print(f"  System Message长度: {info['system_message_length']} 字符")

            # 测试用户消息构建
            print("\n测试用户消息构建...")
            test_data = get_sample_data()
            user_message = agent._build_user_message(test_data)
            print(f"OK - 用户消息构建成功 ({len(user_message)} 字符)")

            # 显示前500字符
            print("\n用户消息预览：")
            print(user_message[:500])

        except Exception as e:
            print(f"\nERROR - Agent初始化失败: {str(e)}")
            import traceback
            traceback.print_exc()

    asyncio.run(test_agent())