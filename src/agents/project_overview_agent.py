"""
项目概况Agent - 基于AutoGen (新版 autogen-agentchat API)

负责生成规划选址论证报告的第1章"项目概况"。
"""

import os
from typing import Dict, Any, Optional
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

from src.utils.logger import logger
from src.tools.knowledge_tools import (
    search_regulations,
    search_cases,
)


class ProjectOverviewAgent:
    """
    项目概况Agent

    使用AutoGen的AssistantAgent,专门负责生成项目概况章节内容。
    
    新版 API 使用方式:
    - AssistantAgent(name, model_client, system_message)
    - 通过 run() 或 run_stream() 方法调用
    
    Wave 5 更新:
    - 集成知识库检索工具
    - 支持检索法规标准和案例参考
    """
    
    def __init__(
        self,
        model_client: OpenAIChatCompletionClient,
        prompt_template_path: str = None
    ):
        """
        初始化项目概况Agent

        Args:
            model_client: OpenAIChatCompletionClient 实例
            prompt_template_path: 提示词模板路径,默认为templates/prompts/project_overview.md
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
                "project_overview.md"
            )
        
        # 加载system_message
        self.system_message = self._load_system_message(prompt_template_path)
        self.template_path = prompt_template_path
        
        # 创建AutoGen AssistantAgent (带知识库工具)
        self.agent = AssistantAgent(
            name="project_overview_agent",
            model_client=self.model_client,
            system_message=self.system_message,
            description="负责生成规划选址论证报告第1章'项目概况'的专业AI Agent",
            tools=[search_regulations, search_cases],
        )
        
        logger.info(f"项目概况Agent初始化完成")
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

    def _build_user_message(self, project_data: Dict[str, Any]) -> str:
        """
        构建用户消息

        Args:
            project_data: 项目数据字典

        Returns:
            格式化的用户消息字符串
        """
        lines = ["# 项目信息"]
        
        # 基本信息
        for key, value in project_data.items():
            if isinstance(value, dict):
                lines.append(f"\n## {key}")
                for k, v in value.items():
                    lines.append(f"- {k}：{v}")
            elif isinstance(value, list):
                lines.append(f"\n## {key}")
                for item in value:
                    lines.append(f"- {item}")
            else:
                lines.append(f"- {key}：{value}")
        
        # 添加任务指令
        lines.append("\n" + "=" * 60)
        lines.append("请根据以上项目信息，按照提示词模板的要求，")
        lines.append("生成第1章《项目概况》的完整内容。")
        lines.append("=" * 60)
        
        return "\n".join(lines)

    async def generate(self, project_data: Dict[str, Any]) -> str:
        """
        生成项目概况章节内容

        Args:
            project_data: 项目数据字典

        Returns:
            生成的章节内容 (Markdown格式)
        """
        logger.info("开始生成第1章：项目概况")
        
        # 构建用户消息
        user_message = self._build_user_message(project_data)
        logger.info(f"用户消息构建完成 ({len(user_message)} 字符)")
        
        # 调用 Agent
        result = await self.agent.run(task=user_message)
        
        # 提取响应内容
        if result and result.messages:
            # 获取最后一条消息的内容
            last_message = result.messages[-1]
            if isinstance(last_message, TextMessage):
                content = last_message.content
            else:
                content = str(last_message.content)
            
            logger.info(f"第1章生成成功，字数: {len(content)}")
            return content
        else:
            raise ValueError("Agent没有返回任何内容")

    async def generate_stream(self, project_data: Dict[str, Any]):
        """
        流式生成项目概况章节内容

        Args:
            project_data: 项目数据字典

        Yields:
            消息流
        """
        logger.info("开始流式生成第1章：项目概况")
        
        user_message = self._build_user_message(project_data)
        
        async for message in self.agent.run_stream(task=user_message):
            yield message


# 测试代码
if __name__ == "__main__":
    import asyncio
    
    async def test_agent():
        print("测试项目概况Agent初始化...")
        
        try:
            from src.core.autogen_config import get_model_client
            
            # 获取模型客户端
            model_client = get_model_client()
            
            # 初始化Agent
            agent = ProjectOverviewAgent(model_client)
            
            # 获取Agent信息
            info = agent.get_agent_info()
            print("\n✓ Agent初始化成功!")
            print(f"  Agent名称: {info['name']}")
            print(f"  提示词模板: {info['template_path']}")
            print(f"  System Message长度: {info['system_message_length']} 字符")
            
        except Exception as e:
            print(f"\n✗ Agent初始化失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(test_agent())