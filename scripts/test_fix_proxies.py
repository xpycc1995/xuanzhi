#!/usr/bin/env python3
"""测试修复 proxies 问题"""

import sys
import os
from dotenv import load_dotenv

load_dotenv(override=True)

import httpx

# 创建一个不使用 proxies 的 httpx 客户端
http_client = httpx.Client(
    follow_redirects=True,
    timeout=30.0,
    # 明确不传递 proxies 参数
)

from openai import OpenAI

# 使用自定义的 http 客户端
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    http_client=http_client,
)

print("✓ OpenAI 客户端创建成功（使用自定义 http_client）")

# 测试调用
try:
    response = client.chat.completions.create(
        model="qwen3.5-flash",
        messages=[
            {"role": "user", "content": "你好"}
        ],
        max_tokens=10,
    )
    print(f"✓ API 调用成功：{response.choices[0].message.content}")
except Exception as e:
    print(f"✗ API 调用失败：{e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✓ 测试通过!")
