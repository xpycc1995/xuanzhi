"""
Excel智能体 - 混合模式版

核心策略:
1. Python直接检索知识库（可靠性100%）
2. 构建填充值列表
3. 让模型只调用写入工具（简化决策）

这种混合模式避免了模型"忘记"调用工具的问题。
"""

import os
import json
import re
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

from src.services.data_validator import DataValidator, ValidationReport
from src.services.excel_parser import ExcelParser
from src.tools.excel_tools import (
    search_knowledge_base,
    write_excel_batch,
)
from src.utils.logger import logger


# 系统提示词 - 极简版，只关注写入
EXCEL_AGENT_SYSTEM_MESSAGE = """你是Excel数据写入助手。

## 你的唯一任务

调用 write_excel_batch 工具写入数据。

## 工具

### write_excel_batch(file_path, updates)
写入Excel字段。
- file_path: Excel文件路径
- updates: 更新列表，格式 [{"sheet": "Sheet名", "field": "字段名", "value": "值"}]

## 示例

```
write_excel_batch(
    file_path="/path/to/file.xlsx",
    updates=[{"sheet": "项目基本信息", "field": "建设单位", "value": "汉川市水利和湖泊局"}]
)
```
"""


class ExcelAgent:
    """
    Excel智能体 - 混合模式版
    
    核心策略:
    1. Python直接检索知识库（可靠性100%）
    2. 构建填充值列表
    3. 让模型只调用写入工具
    
    使用方式:
    ```python
    agent = ExcelAgent(model_client)
    result = await agent.fill_excel("项目数据.xlsx")
    ```
    """
    
    def __init__(
        self,
        model_client: OpenAIChatCompletionClient,
        validator: Optional[DataValidator] = None
    ):
        self.model_client = model_client
        self.validator = validator or DataValidator()
        
        self.tools = [write_excel_batch]  # 只保留写入工具
        
        self.agent = AssistantAgent(
            name="excel_agent",
            model_client=self.model_client,
            system_message=EXCEL_AGENT_SYSTEM_MESSAGE,
            tools=self.tools,
            description="Excel数据写入助手"
        )
        
        logger.info(f"ExcelAgent初始化完成，工具数: {len(self.tools)}")
    
    def get_agent(self) -> AssistantAgent:
        return self.agent
    
    def validate_excel(self, file_path: str) -> ValidationReport:
        parser = ExcelParser(file_path)
        report = self.validator.validate_all(parser)
        parser.close()
        return report
    
    def get_missing_fields(self, file_path: str) -> Dict[str, List[str]]:
        parser = ExcelParser(file_path)
        missing = self.validator.fill_missing_fields(parser)
        parser.close()
        return missing
    
    def _search_knowledge(self, project_name: str, field_name: str, threshold: float = 0.7) -> tuple:
        """
        从知识库检索字段值 (线程池方式解决异步问题)
        
        Returns:
            (value, source, confidence)
        """
        import concurrent.futures
        
        def _do_search():
            from src.rag import get_retriever
            
            retriever = get_retriever()
            query = f"{project_name} {field_name}"
            
            try:
                results = retriever.search(query, n_results=3, threshold=threshold)
                
                if not results:
                    return ("待补充", "未找到", 0.0)
                
                best = results[0]
                content = best.content
                
                # 提取特定字段值
                value = self._extract_value(field_name, content)
                
                if value:
                    return (value, "知识库", best.score)
                
                # 无法提取特定值，返回高置信度的摘要
                if best.score >= 0.75:
                    return (content[:100], "知识库摘要", best.score)
                
                return ("待补充", "置信度不足", best.score)
                
            except Exception as e:
                logger.error(f"检索失败: {str(e)}")
                return ("待补充", f"错误: {str(e)}", 0.0)
        
        # 在线程池中运行同步代码
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(_do_search)
                return future.result(timeout=30)
        except Exception as e:
            logger.error(f"线程执行失败: {str(e)}")
            return ("待补充", f"错误: {str(e)}", 0.0)
    
    def _extract_value(self, field_name: str, content: str) -> Optional[str]:
        """从检索结果中提取特定字段值"""
        
        # 字段名映射到正则模式
        patterns = {
            "建设单位": r'建设单位[：:]\s*(.+?)(?:\n|$)',
            "项目名称": r'项目名称[：:]\s*(.+?)(?:\n|$)',
            "项目代码": r'项目代码[：:]\s*(.+?)(?:\n|$)',
            "建设性质": r'建设性质[：:]\s*(.+?)(?:\n|$)',
            "建设依据": r'建设依据[：:]\s*(.+?)(?:\n|$)',
            "项目投资": r'项目投资[：:]\s*(.+?)(?:\n|$)',
            "建设工期": r'建设工期[：:]\s*(.+?)(?:\n|$)',
            "建设内容": r'建设内容[：:]\s*(.+?)(?:\n|$)',
            "项目选址": r'项目选址[：:]\s*(.+?)(?:\n|$)',
        }
        
        # 直接匹配
        if field_name in patterns:
            match = re.search(patterns[field_name], content)
            if match:
                return match.group(1).strip()
        
        # 通用模式：字段名：值
        generic_pattern = rf'{field_name}[：:]\s*(.+?)(?:\n|$)'
        match = re.search(generic_pattern, content)
        if match:
            return match.group(1).strip()
        
        return None
    
    async def _write_batch(
        self,
        file_path: str,
        updates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        让模型调用写入工具
        
        Args:
            file_path: Excel文件路径
            updates: 更新列表
            
        Returns:
            写入结果
        """
        updates_json = json.dumps(updates, ensure_ascii=False, indent=2)
        
        task = f"""请调用 write_excel_batch 工具写入以下数据。

文件路径: {file_path}

数据:
```json
{updates_json}
```

请执行写入操作。"""
        
        result = await self.agent.run(task=task)
        
        if result and result.messages:
            return {
                "success": True,
                "updates": updates,
                "response": result.messages[-1].content if hasattr(result.messages[-1], 'content') else str(result.messages[-1])
            }
        
        return {
            "success": False,
            "error": "Agent未返回结果"
        }
    
    async def fill_excel(
        self,
        file_path: str,
        output_path: Optional[str] = None,
        threshold: float = 0.7,
        batch_size: int = 10,
        auto_fill_default: bool = True
    ) -> Dict[str, Any]:
        """
        自动填充Excel文件 - 混合模式
        
        流程:
        1. Python检索知识库获取填充值
        2. 让模型调用写入工具
        
        Args:
            file_path: Excel文件路径
            output_path: 输出路径，默认覆盖原文件
            threshold: 检索阈值 (0-1)
            batch_size: 每批次字段数量
            auto_fill_default: 未找到信息时是否填充"待补充"
            
        Returns:
            填充结果报告
        """
        logger.info(f"开始填充Excel: {file_path}")
        
        # 步骤1: 获取缺失字段
        parser = ExcelParser(file_path)
        report = self.validator.validate_all(parser)
        parser.close()
        
        missing_fields = report.get_missing_fields()
        total_missing = sum(len(fields) for fields in missing_fields.values())
        
        logger.info(f"发现 {total_missing} 个缺失字段")
        
        if total_missing == 0:
            return {
                "success": True,
                "file": file_path,
                "total_missing": 0,
                "message": "数据已完整，无需填充"
            }
        
        # 步骤2: 获取项目名称
        parser = ExcelParser(file_path)
        try:
            project_info = parser.parse_project_overview()
            project_name = project_info.项目名称 if hasattr(project_info, '项目名称') else ""
        except:
            project_name = ""
        finally:
            parser.close()
        
        output_file = output_path or file_path
        
        # 步骤3: 检索知识库，构建填充值
        logger.info("正在从知识库检索...")
        
        all_updates = []
        search_details = []
        
        for sheet_name, fields in missing_fields.items():
            for field in fields:
                value, source, confidence = self._search_knowledge(project_name, field, threshold)
                
                all_updates.append({
                    "sheet": sheet_name,
                    "field": field,
                    "value": value
                })
                
                search_details.append({
                    "sheet": sheet_name,
                    "field": field,
                    "value": value,
                    "source": source,
                    "confidence": round(confidence, 3)
                })
                
                logger.info(f"  {sheet_name}.{field}: {value[:30]}... (置信度: {confidence:.2f})")
        
        # 步骤4: 分批写入
        logger.info(f"开始写入，共 {len(all_updates)} 个字段")
        
        batches = []
        for i in range(0, len(all_updates), batch_size):
            batches.append(all_updates[i:i + batch_size])
        
        write_results = []
        for i, batch in enumerate(batches):
            logger.info(f"写入批次 {i+1}/{len(batches)}, 字段数: {len(batch)}")
            
            result = await self._write_batch(output_file, batch)
            write_results.append(result)
        
        # 步骤5: 汇总结果
        success_count = sum(1 for r in write_results if r.get("success"))
        
        return {
            "success": success_count == len(batches),
            "file": file_path,
            "output": output_file,
            "total_missing": total_missing,
            "total_filled": len([d for d in search_details if d["value"] != "待补充"]),
            "search_details": search_details,
            "write_results": write_results,
            "message": f"填充完成: {success_count}/{len(batches)} 批次成功"
        }
    
    async def analyze_excel(self, file_path: str) -> Dict[str, Any]:
        """分析Excel文件"""
        report = self.validate_excel(file_path)
        
        return {
            "success": True,
            "file": file_path,
            "total_sheets": report.total_sheets,
            "total_fields": report.total_fields,
            "valid_fields": report.valid_fields,
            "missing_fields": report.missing_fields,
            "completion_rate": f"{report.completion_rate:.1f}%",
            "is_complete": report.is_complete,
            "missing_by_sheet": report.get_missing_fields(),
            "markdown_report": report.to_markdown()
        }
    
    async def query_for_field(
        self,
        field_name: str,
        context: str = ""
    ) -> Dict[str, Any]:
        """为特定字段检索知识库"""
        value, source, confidence = self._search_knowledge(context, field_name)
        
        return {
            "success": True,
            "field": field_name,
            "value": value,
            "source": source,
            "confidence": confidence
        }


def create_excel_agent(
    model_client: Optional[OpenAIChatCompletionClient] = None
) -> ExcelAgent:
    """创建Excel智能体"""
    if model_client is None:
        from src.core.autogen_config import get_model_client
        model_client = get_model_client()
    
    return ExcelAgent(model_client)


# 兼容旧版API
ExcelAssistantAgent = ExcelAgent


if __name__ == "__main__":
    import asyncio
    
    async def test_agent():
        print("测试ExcelAgent...")
        
        try:
            from src.core.autogen_config import get_model_client
            
            model_client = get_model_client()
            agent = ExcelAgent(model_client)
            
            print(f"\n✓ Agent初始化成功!")
            print(f"  工具数量: {len(agent.tools)}")
            
            # 测试检索
            print("\n测试知识库检索...")
            value, source, conf = agent._search_knowledge("汉川市万福低闸", "建设单位")
            print(f"  建设单位: {value} (来源: {source}, 置信度: {conf})")
            
        except Exception as e:
            print(f"\n✗ 测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(test_agent())