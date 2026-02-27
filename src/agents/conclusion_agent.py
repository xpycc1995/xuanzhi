"""
结论与建议Agent - 基于AutoGen (新版 autogen-agentchat API)

负责生成规划选址论证报告的第6章"结论与建议"。
"""

import os
from typing import Dict, Any, Optional
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

from src.models.conclusion_data import ConclusionData
from src.utils.logger import logger


class ConclusionAgent:
    """
    结论与建议Agent

    使用AutoGen的AssistantAgent，专门负责生成第6章"结论与建议"内容。

    该Agent需要处理的数据包括：
    - 6.1 综合论证结论
      - 项目概述（从第1章提取）
      - 综合论证一览表（表6-1）
      - 最终可行性结论
    - 6.2 主要建议（固定5条）
    """

    def __init__(
        self,
        model_client: OpenAIChatCompletionClient,
        prompt_template_path: str = None
    ):
        """
        初始化结论与建议Agent

        Args:
            model_client: OpenAIChatCompletionClient 实例
            prompt_template_path: 提示词模板路径，默认为templates/prompts/conclusion.md
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
                "conclusion.md"
            )

        # 加载system_message
        self.system_message = self._load_system_message(prompt_template_path)
        self.template_path = prompt_template_path

        # 创建AutoGen AssistantAgent
        self.agent = AssistantAgent(
            name="conclusion_agent",
            model_client=self.model_client,
            system_message=self.system_message,
            description="负责生成规划选址论证报告第6章'结论与建议'的专业AI Agent"
        )

        logger.info(f"结论与建议Agent初始化完成")
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

    def _validate_data(self, data: ConclusionData):
        """
        验证输入数据

        Args:
            data: 结论与建议数据

        Raises:
            ValueError: 数据验证失败
        """
        # Pydantic已经做了基本验证，这里做业务逻辑验证
        if not data.项目基本信息:
            raise ValueError("项目基本信息不能为空")

        if not data.综合论证结论:
            raise ValueError("综合论证结论不能为空")

        if len(data.建议列表) != 5:
            raise ValueError(f"建议列表必须包含5条建议，当前有{len(data.建议列表)}条")

        logger.info("数据验证通过")

    def _build_user_message(
        self,
        conclusion_data: ConclusionData,
        context: str = None
    ) -> str:
        """
        构建发送给Agent的用户消息

        Args:
            conclusion_data: 结论与建议数据
            context: 可选的上下文信息（前5章结论摘要）

        Returns:
            格式化的用户消息字符串
        """
        lines = []

        # 添加上下文信息（如有）
        if context:
            lines.append("# 前置章节结论摘要")
            lines.append(context)
            lines.append("")

        # 添加项目基本信息
        lines.append("# 项目基本信息")
        for key, value in conclusion_data.项目基本信息.items():
            lines.append(f"- {key}：{value}")

        # 添加合法合规性结论
        lines.append("\n# 合法合规性结论")
        lines.append(f"- 法律法规结论：{conclusion_data.合法合规性结论.法律法规结论}")

        lines.append("\n## 三线协调结论")
        for key, value in conclusion_data.合法合规性结论.三线结论.items():
            lines.append(f"- {key}：{value}")

        lines.append("\n## 国土空间规划结论")
        for key, value in conclusion_data.合法合规性结论.国土空间规划结论.items():
            lines.append(f"- {key}：{value}")

        lines.append("\n## 专项规划结论")
        for key, value in conclusion_data.合法合规性结论.专项规划结论.items():
            lines.append(f"- {key}：{value}")

        if conclusion_data.合法合规性结论.其他规划结论:
            lines.append("\n## 其他规划结论")
            for key, value in conclusion_data.合法合规性结论.其他规划结论.items():
                lines.append(f"- {key}：{value}")

        if conclusion_data.合法合规性结论.城乡总体规划结论:
            lines.append(f"\n## 城乡总体规划结论：{conclusion_data.合法合规性结论.城乡总体规划结论}")

        lines.append(f"\n## 综合结论：{conclusion_data.合法合规性结论.综合结论}")

        # 添加选址合理性结论
        lines.append("\n# 选址合理性结论")
        lines.append(f"- 环境影响结论：{conclusion_data.选址合理性结论.环境影响结论}")
        lines.append(f"- 矿产资源结论：{conclusion_data.选址合理性结论.矿产资源结论}")
        lines.append(f"- 地质灾害结论：{conclusion_data.选址合理性结论.地质灾害结论}")

        if conclusion_data.选址合理性结论.社会稳定结论:
            lines.append(f"- 社会稳定结论：{conclusion_data.选址合理性结论.社会稳定结论}")

        if conclusion_data.选址合理性结论.节能结论:
            lines.append(f"- 节能结论：{conclusion_data.选址合理性结论.节能结论}")

        lines.append(f"- 综合结论：{conclusion_data.选址合理性结论.综合结论}")

        # 添加节约集约用地结论
        lines.append("\n# 节约集约用地结论")
        lines.append(f"- 功能分区结论：{conclusion_data.节约集约用地结论.功能分区结论}")
        lines.append(f"- 用地规模结论：{conclusion_data.节约集约用地结论.用地规模结论}")
        lines.append(f"- 节地技术结论：{conclusion_data.节约集约用地结论.节地技术结论}")
        lines.append(f"- 综合结论：{conclusion_data.节约集约用地结论.综合结论}")

        # 添加综合论证结论
        lines.append("\n# 综合论证结论")
        lines.append(conclusion_data.综合论证结论)

        # 添加建议列表
        lines.append("\n# 主要建议")
        for suggestion in conclusion_data.建议列表:
            lines.append(f"（{suggestion.序号}）{suggestion.内容}")

        # 添加任务指令
        lines.append("\n" + "=" * 60)
        lines.append("请根据以上提供的结论数据，严格按照提示词模板的要求，")
        lines.append("生成第6章《结论与建议》的完整内容。")
        lines.append("确保：")
        lines.append("1. 包含6.1综合论证结论和6.2主要建议两部分")
        lines.append("2. 表6-1格式规范，数据与前5章结论一致")
        lines.append("3. 正好5条建议，编号（1）到（5）")
        lines.append("4. 综合论证结论明确可行")
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
        conclusion_data: ConclusionData,
        context: str = None
    ) -> str:
        """
        生成第6章：结论与建议

        Args:
            conclusion_data: 结论与建议数据（ConclusionData模型）
            context: 可选的上下文信息（如前5章的摘要）

        Returns:
            生成的第6章内容（Markdown格式）
        """
        logger.info("开始生成第6章：结论与建议")
        logger.info(f"  项目名称：{conclusion_data.项目基本信息.get('项目名称', '未知')}")
        logger.info(f"  建议数量：{len(conclusion_data.建议列表)}")

        try:
            # 1. 数据验证
            self._validate_data(conclusion_data)

            # 2. 构建用户消息
            user_message = self._build_user_message(conclusion_data, context)

            # 3. 调用Agent生成内容
            result = await self.agent.run(task=user_message)

            # 4. 提取响应内容
            if result and result.messages:
                last_message = result.messages[-1]
                if isinstance(last_message, TextMessage):
                    content = last_message.content
                else:
                    content = str(last_message.content)

                logger.info(f"第6章生成成功，字数: {len(content)}")
                return content
            else:
                raise ValueError("Agent没有返回任何内容")

        except Exception as e:
            logger.error(f"第6章生成失败: {str(e)}")
            raise

    async def generate_stream(
        self,
        conclusion_data: ConclusionData,
        context: str = None
    ):
        """
        流式生成第6章内容

        Args:
            conclusion_data: 结论与建议数据
            context: 可选的上下文信息

        Yields:
            消息流
        """
        logger.info("开始流式生成第6章：结论与建议")

        self._validate_data(conclusion_data)
        user_message = self._build_user_message(conclusion_data, context)

        async for message in self.agent.run_stream(task=user_message):
            yield message


# 测试代码
if __name__ == "__main__":
    import asyncio

    async def test_agent():
        print("测试结论与建议Agent初始化...")

        try:
            from src.core.autogen_config import get_model_client
            from src.models.conclusion_data import get_sample_data

            # 获取模型客户端
            model_client = get_model_client()

            # 初始化Agent
            agent = ConclusionAgent(model_client)

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