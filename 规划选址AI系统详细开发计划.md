规划选址论证报告AI系统

详细开发计划书

含本地RAG知识库完整实现方案

核心功能：Excel辅助填写 + 本地知识库 + 联网搜索

技术栈：AutoGen + ChromaDB + 百炼Qwen

开发周期：4周


2026年2月


# 目录

(提示：首次打开请右键点击目录，选择"更新域"刷新页码)


项目概述	3

本地RAG知识库详解	4

什么是RAG	4

需要哪些组件	5

向量模型选择	6

完整架构图	7

详细开发计划	8

第一阶段：知识库搭建	8

第二阶段：Excel智能体	9

第三阶段：系统集成	10

第四阶段：Web界面	11

核心代码实现	12

成本与性能分析	15



本项目基于AutoGen框架，实现规划选址论证报告的AI智能编制。目前已完成6个章节Agent开发 + RAG知识库模块 + Excel智能体，下一步核心任务是实现Agent集成知识库。

## 当前开发进度

| 阶段 | 状态 | 完成时间 |
|------|------|----------|
| 第一阶段：知识库搭建 | ✅ 已完成 | 2026-02-27 |
| 第二阶段：Excel智能体 | ✅ 已完成 | 2026-02-27 |
| 第三阶段：系统集成 | ⏳ 待开发 | - |
| 第四阶段：Web界面 | ⏳ 待开发 | - |

## 核心功能

## 简化架构

采用"1个主Agent + 6个工具"的简洁设计：


# 本地RAG知识库详解

## 什么是RAG

RAG（Retrieval-Augmented Generation，检索增强生成）是一种将外部知识检索与大模型生成结合的技术。简单来说，就是让AI在回答问题前，先从你的文档中找到相关内容，然后基于这些内容生成答案。

## 需要哪些组件

## ✅ 已实现组件 (Wave 1-4)

| 组件 | 文件 | 状态 | 说明 |
|------|------|------|------|
| 向量数据库 | src/rag/knowledge_base.py | ✅ | ChromaDB封装，支持向量存储/检索 |
| 向量模型 | src/rag/embedding.py | ✅ | 百炼text-embedding-v3，1024维 |
| 文档处理 | src/rag/document_processor.py | ✅ | PDF/Word/MD/TXT解析 |
| 文本分块 | src/rag/text_chunker.py | ✅ | 重叠滑动窗口，512字符块，128重叠 |
| 检索服务 | src/rag/retriever.py | ✅ | 高级检索，Top-K，阈值过滤 |
| CLI知识库 | scripts/kb.py | ✅ | init/add/query/stats/list/clear |
| Excel工具 | src/tools/excel_tools.py | ✅ | read/write/search_knowledge_base |
| Excel智能体 | src/agents/excel_assistant_agent.py | ✅ | 自动填充Agent |
| CLI填充 | scripts/fill_excel.py | ✅ | analyze/fill/query |
| 单元测试 | tests/ | ✅ | 54个测试用例 |

## 向量模型选择（重点）

这是你最关心的问题。答案是：需要向量模型，但不需要本地部署大型模型。

### 方案一：使用百炼Embedding API（推荐）

阿里云百炼提供在线Embedding服务，价格低廉，无需本地GPU。

### 方案二：本地小型向量模型

如果完全离线，可以使用本地小型模型。

## 完整架构图


# 详细开发计划

## 第一阶段：知识库搭建 ✅ 已完成 (2026-02-27)

| 天 | 任务 | 交付物 | 状态 |
|----|------|--------|------|
| D1-2 | 搭建ChromaDB环境 | 数据库初始化代码 | ✅ |
| D3-4 | 实现文档处理 | PDF/Word解析模块 | ✅ |
| D5-6 | 实现文本分块 | 分块算法 | ✅ |
| D7 | 整合测试 | 知识库模块完整代码 | ✅ |

### 已交付文件

```
src/rag/
├── __init__.py              # 模块导出
├── document_processor.py    # 多格式文档解析 (262行)
├── text_chunker.py          # 重叠滑动窗口分块 (264行)
├── knowledge_base.py        # ChromaDB封装 (352行)
├── embedding.py             # 百炼Embedding API (202行)
└── retriever.py             # 高级检索服务 (Wave 3)

tests/test_rag/
└── test_rag_system.py       # 28个单元测试 (429行)
```

### 测试覆盖率

```
src/rag/knowledge_base.py     80% ✅
src/rag/text_chunker.py       82% ✅
src/rag/document_processor.py 40%
src/rag/embedding.py          40%
```

## 第二阶段：Excel智能体 ✅ 已完成 (2026-02-27)

| 天 | 任务 | 交付物 | 状态 |
|----|------|--------|------|
| D1-2 | Excel读写Tools | read_excel/write_excel | ✅ |
| D3-4 | 知识检索Tool | search_knowledge_base | ✅ |
| D5-6 | ExcelAssistantAgent | 主Agent实现 | ✅ |
| D7 | 测试优化 | 测试用例、Bug修复 | ✅ |

### 已交付文件

```
src/tools/
├── __init__.py              # 模块导出
└── excel_tools.py           # 6个工具函数 (487行)

src/agents/
└── excel_assistant_agent.py # Excel智能体 (321行)

scripts/
└── fill_excel.py            # CLI命令 (229行)

tests/
└── test_wave4_excel_agent.py # 16个测试 (332行)
```

## 第三阶段：系统集成 ⏳ 待开发

# 核心代码实现

## 项目结构

## 知识库核心代码

# src/rag/knowledge_base.py
import chromadb
from chromadb.utils import embedding_functions

class KnowledgeBase:
    def __init__(self, collection_name="xuanzhi"):
        # 初始化ChromaDB
        self.client = chromadb.PersistentClient(path="./data/chroma_db")
        
        # 使用百炼Embedding API
        self.embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
            api_key="sk-xxx",
            api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model_name="text-embedding-v3"
        )
        
        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn
        )

    def add_documents(self, documents, ids=None, metadatas=None):
        """添加文档到知识库"""
        if ids is None:
            ids = [str(i) for i in range(len(documents))]
        self.collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )

    def search(self, query, n_results=5):
        """检索知识库"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results"

## Excel辅助Agent代码

# src/agents/excel_assistant_agent.py
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from src.tools.excel_tools import read_excel, write_excel
from src.tools.knowledge_tools import search_knowledge_base

# 创建模型客户端（带联网搜索）
model_client = OpenAIChatCompletionClient(
    model="qwen-plus",
    api_key="sk-xxx",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    extra_body={"enable_search": True}
)

# 创建Excel辅助Agent
excel_agent = AssistantAgent(
    name="excel_assistant",
    model_client=model_client,
    system_message="""你是Excel辅助填写助手...""",
    tools=[read_excel, search_knowledge_base, write_excel]
)"


# 成本与性能分析

## 成本对比

## 推荐方案

向量模型：使用百炼text-embedding-v3，价格低廉，效果好

向量数据库：ChromaDB轻量易用，本地存储免费

文档处理：pymupdf解析PDF，python-docx解析Word

文本分块：重叠滑动窗口，块大小512字符，重叠128字符

## 总结

本开发计划采用"1主Agent + 6个Tools"的简洁架构，知识库使用ChromaDB + 百炼Embedding API的组合，联网搜索使用百炼内置功能。已完成Wave 1-4，剩余Wave 5集成和Wave FINAL验证。



| 功能 | 说明 |
|  --- | --- |
| 本地知识库检索 | 从用户上传的PDF/Word资料中检索信息 |
| 联网搜索 | 百炼API内置功能，无需额外开发 |
| Excel读写 | 读取和写入Excel文件 |


| 组件 | 类型 | 说明 |
|  --- | --- | --- |
| ExcelAssistantAgent | AssistantAgent | 主Agent，协调填写流程 |
| read_excel | FunctionTool | 读取Excel文件 |
| search_knowledge_base | FunctionTool | 本地知识库检索 |
| write_excel | FunctionTool | 写入Excel文件 |


| 组件 | 推荐方案 | 说明 |
|  --- | --- | --- |
| 向量数据库 | ChromaDB | 开源、轻量、本地存储 |
| 向量模型 | 百炼Embedding API | 价格低，无需GPU |
| 文档处理 | pymupdf/python-docx | 提取PDF/Word文本 |
| 文本分块 | 自实现/使用库 | 将大文档切分为小块 |


| 指标 | 数值 | 说明 |
|  --- | --- | --- |
| 模型名称 | text-embedding-v3 | 百炼最新Embedding模型 |
| 向量维度 | 1024维 | 平衡性能与储存 |
| 价格 | 0.0005元/千token | 数据量小可忽略 |
| 优势 | 无需本地GPU | 适合数据量小的场景 |


| 模型 | 特点 | 适用场景 |
|  --- | --- | --- |
| BGE-small-zh | 38M参数，中文优化 | 资源有限，中文为主 |
| BGE-base-zh | 102M参数，效果更好 | 平衡方案 |
| GTE-small | 阿里开源，中英文 | 需要英文支持 |


| 层级 | 组件与说明 |
|  --- | --- |
| API层 | AutoGen AssistantAgent + 6个FunctionTool |
| LLM层 | 百炼qwen-plus（带enable_search） |
| 检索层 | ChromaDB + 百炼Embedding API |
| 处理层 | PDF解析 + 文本分块 + 向量化 |
| 存储层 | 本地文件系统（PDF/Word/Excel） |


| 天 | 任务 | 交付物 | 关键技术 |
|  --- | --- | --- | --- |
| D1-2 | 搭建ChromaDB环境 | 数据库初始化代码 | chromadb |
| D3-4 | 实现文档处理 | PDF/Word解析模块 | pymupdf/python-docx |
| D5-6 | 实现文本分块 | 分块算法 | 重叠滑动窗口 |
| D7 | 整合测试 | 知识库模块完整代码 | pytest |


| 天 | 任务 | 交付物 | 关键技术 |
|  --- | --- | --- | --- |
| D1-2 | Excel读写Tools | read_excel/write_excel | openpyxl |
| D3-4 | 知识检索Tool | search_knowledge_base | ChromaDB |
| D5-6 | ExcelAssistantAgent | 主Agent实现 | AssistantAgent |
| D7 | 测试优化 | 测试用例、Bug修复 | pytest |


| 天 | 任务 | 交付物 | 关键技术 |
|  --- | --- | --- | --- |
| D1-3 | 与6章Agent集成 | 统一编排器 | Orchestrator |
| D4-5 | 数据流优化 | 缓存机制 | 内存缓存 |
| D6-7 | 错误处理 | 异常处理框架 | Tenacity |


| 天 | 任务 | 交付物 | 关键技术 |
|  --- | --- | --- | --- |
| D1-5 | FastAPI接口 | RESTful API | FastAPI |
| D6-7 | 前端界面 | Web UI | Vue3 |


| 文件路径 | 说明 |
|  --- | --- |
| src/rag/knowledge_base.py | 知识库核心类 |
| src/rag/retriever.py | 高级检索服务 |
| src/agents/excel_assistant_agent.py | Excel辅助主Agent |
| src/tools/excel_tools.py | Excel读写工具 |
| scripts/kb.py | CLI知识库命令 |
| scripts/fill_excel.py | CLI Excel填充 |


| 方案 | 存储成本 | 计算成本 | 开发成本 |
|  --- | --- | --- | --- |
| 百炼知识库 | 高 | 高 | 低 |
| 本方案 | 免费 | 低（Embedding API） | 中 |
| 完全本地 | 免费 | 需GPU（一次性） | 高 |