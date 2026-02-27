#!/usr/bin/env python3
"""
测试 autogen-agentchat 新版 API 配置

验证新版 autogen-agentchat 0.7.x 的配置是否正确。
"""

import sys
import os
import asyncio
from dotenv import load_dotenv

load_dotenv(override=True)

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.utils.logger import setup_logger, logger

setup_logger()

logger.info("测试 autogen-agentchat 新版 API 配置...")

async def test_new_api():
    """测试新版 API"""
    try:
        from autogen_agentchat.agents import AssistantAgent
        from autogen_agentchat.messages import TextMessage
        from autogen_ext.models.openai import OpenAIChatCompletionClient
        
        # 获取 API 配置
        dashscope_key = os.getenv("DASHSCOPE_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if dashscope_key:
            model_name = os.getenv("MODEL_NAME", "qwen-plus")
            base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
            logger.info(f"使用阿里云百炼模型: {model_name}")
        elif openai_key:
            model_name = os.getenv("OPENAI_MODEL", "gpt-4o")
            base_url = None
            dashscope_key = openai_key
            logger.info(f"使用 OpenAI 模型: {model_name}")
        else:
            raise ValueError("请设置 DASHSCOPE_API_KEY 或 OPENAI_API_KEY 环境变量")
        
        # 创建模型客户端
        model_client = OpenAIChatCompletionClient(
            model=model_name,
            api_key=dashscope_key,
            base_url=base_url,
        )
        
        logger.info("✓ 模型客户端创建成功")
        
        # 创建 AssistantAgent
        agent = AssistantAgent(
            name="test_assistant",
            model_client=model_client,
            system_message="你是一个专业的助手，请用简洁的语言回答问题。",
        )
        
        logger.info("✓ AssistantAgent 创建成功")
        
        # 测试对话
        logger.info("测试对话...")
        result = await agent.run(task="你好，请用一句话介绍你自己。")
        
        if result and result.messages:
            last_message = result.messages[-1]
            if isinstance(last_message, TextMessage):
                logger.info(f"✓ 对话成功!")
                logger.info(f"  响应: {last_message.content[:100]}...")
            else:
                logger.info(f"✓ 对话成功!")
                logger.info(f"  响应类型: {type(last_message).__name__}")
        else:
            raise ValueError("Agent 没有返回任何内容")
        
        # 关闭模型客户端
        await model_client.close()
        
        logger.info("✓ 测试成功!")
        return True
        
    except Exception as e:
        logger.error(f"✗ 测试失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    success = asyncio.run(test_new_api())
    
    if success:
        print("\n✓ autogen-agentchat 新版 API 配置测试通过!")
    else:
        print("\n✗ autogen-agentchat 新版 API 配置测试失败!")
        sys.exit(1)


if __name__ == "__main__":
    main()