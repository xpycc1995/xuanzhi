"""
阿里云百炼API测试脚本

验证DASHSCOPE_API_KEY配置是否正确,测试模型调用。
使用新版 autogen-agentchat API。
"""

import os
import sys
import io
import asyncio
from dotenv import load_dotenv

# 加载环境变量（override=True 强制覆盖系统环境变量）
load_dotenv(override=True)

# 修复 Windows 控制台编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def test_qwen_connection():
    """测试阿里云百炼连接"""

    print("=" * 60)
    print("阿里云百炼API连接测试")
    print("=" * 60)

    # 检查API密钥
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("\n✗ 错误: 未找到DASHSCOPE_API_KEY环境变量")
        print("\n请先配置API密钥:")
        print("1. 复制 .env.example 为 .env")
        print("2. 在.env中设置 DASHSCOPE_API_KEY=sk-your-key")
        return False

    print(f"\n✓ API密钥已配置: {api_key[:10]}...{api_key[-4:]}")

    # 获取模型名称
    model_name = os.getenv("MODEL_NAME", "qwen-plus")
    print(f"✓ 使用模型: {model_name}")

    # 创建客户端
    from openai import OpenAI
    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    # 测试消息
    test_messages = [
        {
            "role": "user",
            "content": "你好!请用一句话介绍你自己。"
        }
    ]

    print("\n发送测试消息...")

    try:
        # 调用API
        completion = client.chat.completions.create(
            model=model_name,
            messages=test_messages,
            stream=True
        )

        # 打印响应
        print("\n" + "=" * 20 + "模型回复" + "=" * 20)

        full_response = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                full_response += content

        print("\n" + "=" * 60)
        print(f"\n✓ API调用成功!")
        print(f"  响应长度: {len(full_response)} 字符")
        print(f"\n可以开始使用系统了!")

        return True

    except Exception as e:
        print("\n" + "=" * 60)
        print(f"\n✗ API调用失败: {str(e)}")
        print("\n可能的原因:")
        print("1. API密钥错误或已过期")
        print("2. 模型名称不正确")
        print("3. 账户余额不足")
        print("4. 网络连接问题")

        return False


def test_autogen_config():
    """测试AutoGen配置"""
    from src.core.autogen_config import get_model_client, get_model_info

    print("\n" + "=" * 60)
    print("AutoGen配置测试 (新版 API)")
    print("=" * 60)

    try:
        model_client = get_model_client()
        info = get_model_info()

        print(f"\n✓ AutoGen配置加载成功!")
        print(f"  提供商: {info['provider']}")
        print(f"  模型: {info['model']}")
        print(f"  Base URL: {info['base_url']}")

        return True

    except Exception as e:
        print(f"\n✗ AutoGen配置失败: {str(e)}")
        return False


async def test_autogen_agent():
    """测试AutoGen Agent (新版 API)"""
    print("\n" + "=" * 60)
    print("AutoGen Agent 测试 (新版 API)")
    print("=" * 60)

    try:
        from autogen_agentchat.agents import AssistantAgent
        from autogen_agentchat.messages import TextMessage
        from src.core.autogen_config import get_model_client

        # 获取模型客户端
        model_client = get_model_client()

        # 创建测试 Agent
        agent = AssistantAgent(
            name="test_assistant",
            model_client=model_client,
            system_message="你是一个专业的助手，请用简洁的语言回答问题。",
        )

        print("\n✓ AssistantAgent 创建成功")

        # 测试对话
        print("\n发送测试消息...")
        result = await agent.run(task="你好，请用一句话介绍你自己。")

        if result and result.messages:
            last_message = result.messages[-1]
            if isinstance(last_message, TextMessage):
                print(f"\n✓ Agent 对话成功!")
                print(f"  响应: {last_message.content[:100]}...")
            else:
                print(f"\n✓ Agent 对话成功!")
                print(f"  响应类型: {type(last_message).__name__}")
        else:
            raise ValueError("Agent 没有返回任何内容")

        # 关闭模型客户端
        await model_client.close()

        return True

    except Exception as e:
        print(f"\n✗ AutoGen Agent 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""

    print("\n阿里云百炼 + AutoGen (新版 API) 配置验证\n")

    # 测试1: API连接
    api_ok = test_qwen_connection()

    # 测试2: AutoGen配置
    autogen_ok = test_autogen_config()

    # 测试3: AutoGen Agent
    agent_ok = asyncio.run(test_autogen_agent()) if api_ok and autogen_ok else False

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    if api_ok and autogen_ok and agent_ok:
        print("\n✓ 所有测试通过!")
        print("\n下一步:")
        print("  运行 python scripts/test_mvp.py 开始使用系统")
    else:
        print("\n✗ 部分测试失败")
        if not api_ok:
            print("  - API连接失败,请检查配置")
        if not autogen_ok:
            print("  - AutoGen配置失败")
        if not agent_ok:
            print("  - AutoGen Agent测试失败")

    print()


if __name__ == "__main__":
    main()