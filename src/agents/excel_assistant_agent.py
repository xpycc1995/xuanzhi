"""
Excel辅助填写Agent - 基于AutoGen (新版 autogen-agentchat API)

负责读取Excel模板, 检索知识库, 自动填充空白字段。

核心功能:
- read_excel: 读取Excel模板, 识别空白字段
- search_knowledge_base: 从RAG知识库检索相关信息
- write_excel: 自动填充Excel字段
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

from src.tools.excel_tools import (
    read_excel,
    read_excel_all_sheets,
    search_knowledge_base,
    search_knowledge_base_for_field,
    write_excel,
    write_excel_batch,
)
from src.utils.logger import logger


# Excel助手系统提示词
EXCEL_ASSISTANT_SYSTEM_MESSAGE = """你是Excel辅助填写智能助手,专门帮助用户自动填充规划选址项目的Excel数据模板。

## 你的能力

你有三个核心工具:
1. **read_excel**: 读取Excel文件,获取字段列表和空白字段
2. **search_knowledge_base**: 从RAG知识库检索相关法规、案例、标准
3. **write_excel**: 写入Excel字段值

## 工作流程

当用户要求填充Excel时,按以下步骤操作:

### 第1步: 读取Excel
使用 `read_excel_all_sheets` 读取所有Sheet,了解:
- 有哪些Sheet
- 每个Sheet有多少字段
- 有多少空白字段需要填充

### 第2步: 识别空白字段
对每个Sheet使用 `read_excel`,获取详细的空白字段列表。

### 第3步: 检索知识库
对于每个空白字段:
- 使用 `search_knowledge_base` 检索相关信息
- 构建查询: "{字段名} 规划选址 项目建设"
- 如果检索到相关信息,提取建议值

### 第4步: 填充字段
- 如果检索到高置信度信息(相似度>0.7),使用 `write_excel` 填充
- 如果没有找到相关信息,标记为"待手动填写"

### 第5步: 汇总报告
完成后,输出:
- 成功填充字段数
- 未填充字段列表
- 建议手动填写的原因

## 重要规则

1. **不编造数据**: 只使用知识库检索到的信息
2. **标注来源**: 填充时注明信息来源
3. **保留格式**: 不修改Excel模板结构
4. **批量写入**: 优先使用 `write_excel_batch` 提高效率

## 响应格式

完成填充后,输出JSON格式报告:
```json
{
  "file": "文件路径",
  "total_fields": 总字段数,
  "filled_fields": 已填充数,
  "empty_fields": 未填充数,
  "details": [
    {
      "sheet": "Sheet名称",
      "field": "字段名",
      "status": "filled/manual_required",
      "value": "填充值或原因"
    }
  ]
}
```
"""


class ExcelAssistantAgent:
    """
    Excel辅助填写Agent
    
    使用AutoGen的AssistantAgent,配合FunctionTool实现Excel自动填充。
    
    使用方式:
    ```python
    agent = ExcelAssistantAgent(model_client)
    result = await agent.fill_excel("项目数据.xlsx")
    ```
    """
    
    def __init__(
        self,
        model_client: OpenAIChatCompletionClient,
        enable_search: bool = True
    ):
        """
        初始化Excel辅助Agent
        
        Args:
            model_client: OpenAIChatCompletionClient 实例
            enable_search: 是否启用百炼联网搜索 (默认True)
        """
        self.model_client = model_client
        self.enable_search = enable_search
        
        # 创建工具列表
        self.tools = [
            read_excel,
            read_excel_all_sheets,
            search_knowledge_base,
            search_knowledge_base_for_field,
            write_excel,
            write_excel_batch,
        ]
        
        # 创建AutoGen AssistantAgent
        self.agent = AssistantAgent(
            name="excel_assistant",
            model_client=self.model_client,
            system_message=EXCEL_ASSISTANT_SYSTEM_MESSAGE,
            tools=self.tools,
            description="Excel辅助填写智能助手,自动填充项目数据模板"
        )
        
        logger.info(f"ExcelAssistantAgent初始化完成")
        logger.info(f"  工具数量: {len(self.tools)}")
        logger.info(f"  联网搜索: {'启用' if enable_search else '禁用'}")
    
    def get_agent(self) -> AssistantAgent:
        """获取AutoGen Agent实例"""
        return self.agent
    
    def get_tools(self) -> List:
        """获取工具列表"""
        return self.tools
    
    async def fill_excel(
        self,
        file_path: str,
        output_path: Optional[str] = None,
        threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        自动填充Excel文件
        
        Args:
            file_path: Excel文件路径
            output_path: 输出路径 (默认覆盖原文件)
            threshold: 检索阈值 (默认0.7)
            
        Returns:
            填充结果报告
        """
        logger.info(f"开始填充Excel: {file_path}")
        
        # 构建任务消息
        output = output_path or file_path
        task = f"""请填充Excel文件: {file_path}

要求:
1. 读取所有Sheet的空白字段
2. 使用知识库检索相关信息
3. 填充置信度>{threshold}的字段
4. 输出填充报告

输出文件: {output}
"""
        
        # 调用Agent
        result = await self.agent.run(task=task)
        
        # 提取响应
        if result and result.messages:
            last_message = result.messages[-1]
            if isinstance(last_message, TextMessage):
                content = last_message.content
            else:
                content = str(last_message.content)
            
            logger.info(f"Excel填充完成")
            return {
                "success": True,
                "file": file_path,
                "output": output,
                "response": content
            }
        else:
            raise ValueError("Agent没有返回任何内容")
    
    async def analyze_excel(self, file_path: str) -> Dict[str, Any]:
        """
        分析Excel文件,返回空白字段报告
        
        Args:
            file_path: Excel文件路径
            
        Returns:
            分析报告
        """
        task = f"""请分析Excel文件: {file_path}

要求:
1. 读取所有Sheet
2. 统计空白字段
3. 输出分析报告 (不填充,只分析)
"""
        
        result = await self.agent.run(task=task)
        
        if result and result.messages:
            return {
                "success": True,
                "file": file_path,
                "analysis": result.messages[-1].content
            }
        else:
            raise ValueError("Agent没有返回任何内容")
    
    async def query_for_field(
        self,
        field_name: str,
        context: str = ""
    ) -> Dict[str, Any]:
        """
        为特定字段检索知识库
        
        Args:
            field_name: 字段名称
            context: 项目上下文
            
        Returns:
            检索结果
        """
        task = f"""请为字段 "{field_name}" 检索知识库。

项目上下文: {context if context else '无'}

要求:
1. 使用search_knowledge_base检索相关信息
2. 返回建议值和置信度
"""
        
        result = await self.agent.run(task=task)
        
        if result and result.messages:
            return {
                "success": True,
                "field": field_name,
                "suggestions": result.messages[-1].content
            }
        else:
            raise ValueError("Agent没有返回任何内容")


# 便捷函数
def create_excel_agent(
    model_client: Optional[OpenAIChatCompletionClient] = None,
    enable_search: bool = True
) -> ExcelAssistantAgent:
    """
    创建Excel辅助Agent
    
    Args:
        model_client: 模型客户端 (可选,自动加载)
        enable_search: 启用联网搜索
        
    Returns:
        ExcelAssistantAgent实例
    """
    if model_client is None:
        from src.core.autogen_config import get_model_client
        model_client = get_model_client()
    
    return ExcelAssistantAgent(model_client, enable_search)


# 测试代码
if __name__ == "__main__":
    import asyncio
    
    async def test_agent():
        print("测试ExcelAssistantAgent初始化...")
        
        try:
            from src.core.autogen_config import get_model_client
            
            model_client = get_model_client()
            agent = ExcelAssistantAgent(model_client)
            
            print("\n✓ Agent初始化成功!")
            print(f"  Agent名称: {agent.agent.name}")
            print(f"  工具数量: {len(agent.tools)}")
            print(f"  工具列表: {[t.__name__ for t in agent.tools]}")
            
        except Exception as e:
            print(f"\n✗ Agent初始化失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(test_agent())