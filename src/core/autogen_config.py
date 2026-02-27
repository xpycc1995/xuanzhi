"""
AutoGen LLM配置模块 (新版 autogen-agentchat API)

支持多种LLM提供商:
1. OpenAI GPT系列
2. 阿里云百炼 Qwen系列 (通过 OpenAI 兼容接口)
"""

import os
from typing import Optional
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelInfo


def get_model_client(
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    temperature: float = 0.7,
) -> OpenAIChatCompletionClient:
    """
    获取 OpenAIChatCompletionClient 模型客户端
    
    支持的配置方式:
    1. 阿里云百炼(推荐):
       - 环境变量: DASHSCOPE_API_KEY
       - 模型: qwen-plus, qwen-turbo, qwen-max 等
    
    2. OpenAI:
       - 环境变量: OPENAI_API_KEY
       - 模型: gpt-4, gpt-4o, gpt-3.5-turbo 等
    
    3. 自定义参数:
       - 直接传入 model, api_key, base_url

    Args:
        model: 模型名称，如果不指定则从环境变量读取
        api_key: API密钥，如果不指定则从环境变量读取
        base_url: API基础URL，用于自定义端点
        temperature: 温度参数，默认0.7

    Returns:
        OpenAIChatCompletionClient 实例
    """
    # 方法1: 阿里云百炼(优先)
    dashscope_key = api_key or os.getenv("DASHSCOPE_API_KEY")
    if dashscope_key:
        model_name = model or os.getenv("MODEL_NAME", "qwen-plus")
        dashscope_url = base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1"
        
        print(f"✓ 使用阿里云百炼模型: {model_name}")
        
        return OpenAIChatCompletionClient(
            model=model_name,
            api_key=dashscope_key,
            base_url=dashscope_url,
            temperature=temperature,
        model_info=ModelInfo(
                vision=False,
                function_calling=True,
                json_output=True,
                structured_output=True,
                family="unknown",
            ),
        )
    
    # 方法2: OpenAI
    openai_key = api_key or os.getenv("OPENAI_API_KEY")
    if openai_key:
        model_name = model or os.getenv("OPENAI_MODEL", "gpt-4o")
        openai_url = base_url  # OpenAI 默认不需要指定 base_url
        
        print(f"✓ 使用OpenAI模型: {model_name}")
        
        return OpenAIChatCompletionClient(
            model=model_name,
            api_key=openai_key,
            base_url=openai_url,
            temperature=temperature,
        )
    
    # 方法3: 抛出错误提示
    raise ValueError(
        f"无法加载LLM配置。请选择以下方式之一配置:\n"
        f"1. 阿里云百炼: 设置环境变量 DASHSCOPE_API_KEY\n"
        f"2. OpenAI: 设置环境变量 OPENAI_API_KEY\n"
        f"3. 直接传入 model, api_key, base_url 参数"
    )


def get_model_info() -> dict:
    """
    获取当前模型信息

    Returns:
        模型信息字典
    """
    dashscope_key = os.getenv("DASHSCOPE_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if dashscope_key:
        return {
            "provider": "阿里云百炼",
            "model": os.getenv("MODEL_NAME", "qwen-plus"),
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        }
    elif openai_key:
        return {
            "provider": "OpenAI",
            "model": os.getenv("OPENAI_MODEL", "gpt-4o"),
            "base_url": "https://api.openai.com/v1",
        }
    else:
        return {
            "provider": "未配置",
            "model": "未知",
            "base_url": "未知",
        }


# 导出常量
DEFAULT_MODEL = "qwen-plus"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TIMEOUT = 300

# 预定义的模型客户端缓存
_model_client_cache: Optional[OpenAIChatCompletionClient] = None


def get_cached_model_client() -> OpenAIChatCompletionClient:
    """
    获取缓存的模型客户端(单例模式)

    Returns:
        OpenAIChatCompletionClient 实例
    """
    global _model_client_cache
    if _model_client_cache is None:
        _model_client_cache = get_model_client()
    return _model_client_cache


# ============================================================================
# 兼容旧版 API 的适配器
# ============================================================================

def get_llm_config() -> dict:
    """
    获取LLM配置 (兼容旧版 API)
    
    注意: 新版 autogen-agentchat 不再使用 llm_config 字典，
    此函数仅用于向后兼容。推荐直接使用 get_model_client()。

    Returns:
        包含 model_client 的配置字典
    """
    print("⚠️  警告: get_llm_config() 已废弃，推荐使用 get_model_client()")
    
    model_client = get_model_client()
    model_info = get_model_info()
    
    return {
        "model_client": model_client,
        "model_name": model_info["model"],
        "provider": model_info["provider"],
        "temperature": DEFAULT_TEMPERATURE,
    }


def get_config_list() -> list:
    """
    获取配置列表 (兼容旧版 API)
    
    注意: 新版 autogen-agentchat 不再使用 config_list，
    此函数仅用于向后兼容。

    Returns:
        配置列表
    """
    print("⚠️  警告: get_config_list() 已废弃，推荐使用 get_model_client()")
    
    model_info = get_model_info()
    
    dashscope_key = os.getenv("DASHSCOPE_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    api_key = dashscope_key or openai_key
    
    return [{
        "model": model_info["model"],
        "api_key": api_key,
        "base_url": model_info["base_url"],
    }]


if __name__ == "__main__":
    # 测试配置加载
    print("测试AutoGen配置加载...")
    
    try:
        # 测试新版 API
        client = get_model_client()
        info = get_model_info()
        print("\n✓ 新版 API 测试成功")
        print(f"  提供商: {info['provider']}")
        print(f"  模型: {info['model']}")
        print(f"  Base URL: {info['base_url']}")
        
        # 测试兼容旧版 API
        print("\n测试兼容旧版 API...")
        config = get_llm_config()
        print(f"  model_client 类型: {type(config['model_client']).__name__}")
        
    except Exception as e:
        print(f"✗ 配置加载失败: {str(e)}")