# PROJECT KNOWLEDGE BASE

**Generated:** 2026-02-27
**Commit:** 0d906b9
**Branch:** main
**AutoGen Version:** autogen-agentchat 0.7.x

## OVERVIEW

规划选址论证报告AI智能体协作系统 - 基于AutoGen框架的多Agent协作系统，自动生成规划选址综合论证报告。Python 3.10+, FastAPI + AutoGen + Pydantic + python-docx + ChromaDB.
本地开发环境：/Users/yc/miniconda/envs/xuanzhi/bin
**重要:** 项目已迁移至新版 `autogen-agentchat` API (0.7.x)，不再使用旧版 `pyautogen`。

**项目状态: ✅ 全部完成 (Wave 1-5 + Wave FINAL)**

## STRUCTURE
```
xuanzhi/
├── src/                    # 核心源码 (三层架构)
│   ├── agents/             # Agent层 - 7个专业AI智能体
│   │   ├── project_overview_agent.py
│   │   ├── site_selection_agent.py
│   │   ├── compliance_analysis_agent.py
│   │   ├── rationality_analysis_agent.py
│   │   ├── land_use_analysis_agent.py
│   │   ├── conclusion_agent.py
│   │   └── excel_agent.py          # Wave 4 (混合模式)
│   ├── services/           # 服务层 - 编排/文档/解析
│   ├── rag/                # RAG知识库 - 向量检索增强生成
│   │   ├── document_processor.py  # 多格式文档解析
│   │   ├── text_chunker.py        # 重叠滑动窗口分块
│   │   ├── knowledge_base.py      # ChromaDB封装
│   │   ├── embedding.py           # 百炼Embedding API
│   │   └── retriever.py           # 检索服务 (Wave 3)
│   ├── tools/              # 工具层 - Excel工具 (Wave 4)
│   │   └── excel_tools.py
│   ├── core/               # 配置 - LLM配置加载
│   └── utils/              # 工具 - 日志配置
├── templates/
│   ├── prompts/            # Agent提示词模板 (6个*.md)
│   ├── word_templates/     # Word报告模板
│   └── excel_templates/    # Excel数据输入模板
├── tests/
│   ├── test_rag/           # RAG知识库测试 (28个测试)
│   ├── test_wave3_retriever.py  # Wave 3测试 (10个测试)
│   ├── test_wave4_excel_agent.py # Wave 4测试 (16个测试)
│   └── test_wave5_integration.py # Wave 5测试 (19个测试)
├── data/
│   ├── knowledge_base/     # 知识库文档存储
│   └── chroma_db/          # ChromaDB向量数据库
├── scripts/                # 测试脚本入口
│   ├── kb.py               # CLI知识库命令 (Wave 3)
│   └── fill_excel.py       # CLI Excel填充 (Wave 4)
└── output/                 # 运行时输出 (报告/日志)
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| 添加新Agent | `src/agents/` | 传入model_client, 加载模板 |
| 修改数据结构 | `src/models/` | Pydantic BaseModel, 中文命名 |
| 调整编排逻辑 | `src/services/autogen_orchestrator.py` | Agent协调中心 |
| Excel解析问题 | `src/services/excel_parser.py` | 支持全部6章解析 |
| Word文档生成 | `src/services/document_service.py` | 模板替换+Markdown解析 |
| LLM配置 | `src/core/autogen_config.py` | OpenAIChatCompletionClient |
| **RAG知识库** | `src/rag/` | ChromaDB + 百炼Embedding |
| **Retriever服务** | `src/rag/retriever.py` | 高级检索接口 |
| **Excel工具** | `src/tools/excel_tools.py` | 6个工具函数 |
| **Excel智能体** | `src/agents/excel_agent.py` | 混合模式: Python检索+模型写入 |
| 提示词模板 | `templates/prompts/*.md` | 6个章节模板 |
| CLI命令 | `scripts/kb.py`, `scripts/fill_excel.py` | 知识库+Excel命令 |

## DATA FLOW

```
Excel模板 → ExcelParser → Pydantic模型 → Agent生成 → DocumentService → Word报告
                    ↓
              AutoGenOrchestrator (协调中心)
                    ↓
              KnowledgeBase (RAG知识库)
                    ↓
              Retriever (检索服务)
                    ↓
              ExcelAssistantAgent (智能填充)
```

## COMPLETED AGENTS

| 章节 | Agent | 数据模型 | 提示词模板 | Excel解析 |
|-----|-------|---------|-----------|----------|
| 第1章 | ProjectOverviewAgent | ProjectOverviewData | project_overview.md | ✅ |
| 第2章 | SiteSelectionAgent | SiteSelectionData | site_selection.md | ✅ |
| 第3章 | ComplianceAnalysisAgent | ComplianceData | compliance_analysis.md | ✅ |
| 第4章 | RationalityAnalysisAgent | RationalityData | rationality_analysis.md | ✅ |
| 第5章 | LandUseAnalysisAgent | LandUseData | land_use_analysis.md | ✅ |
| 第6章 | ConclusionAgent | ConclusionData | conclusion.md | ✅ |
| Excel | ExcelAssistantAgent | - | - | ✅ (Wave 4) |

## RAG MODULE (Wave 1-3)

### 已完成功能
| 模块 | 文件 | 功能 | 测试覆盖率 |
|------|------|------|-----------|
| DocumentProcessor | document_processor.py | PDF/Word/MD/TXT解析 | 40% |
| TextChunker | text_chunker.py | 重叠滑动窗口分块 | 82% |
| KnowledgeBase | knowledge_base.py | ChromaDB向量存储/检索 | 80% |
| BailianEmbedding | embedding.py | 百炼text-embedding-v3 API | 40% |
| Retriever | retriever.py | 高级检索服务 | 新增 |

### 使用示例

```python
from src.rag import KnowledgeBase, DocumentProcessor, TextChunker, Retriever

# 1. 处理文档
processor = DocumentProcessor()
doc = processor.process_file("regulations.pdf")

# 2. 文本分块
chunker = TextChunker(chunk_size=512, overlap=128)
chunks = chunker.chunk_text(doc.content)

# 3. 存入知识库
kb = KnowledgeBase()
texts = [c.content for c in chunks]
kb.add_documents(texts)

# 4. 语义检索
results = kb.search("城乡规划要求", n_results=5)

# 5. 高级检索 (Wave 3)
retriever = Retriever()
retriever.ingest_file("regulations.pdf")
results = retriever.search("项目选址原则", n_results=5, threshold=0.7)
context = retriever.search_with_context("城乡规划要求")
```

## EXCEL MODULE (Wave 4)

### 工具模块 (src/tools/excel_tools.py)

| 工具 | 功能 |
|------|------|
| read_excel | 读取Excel指定Sheet |
| read_excel_all_sheets | 读取所有Sheet概要 |
| search_knowledge_base | RAG知识库检索 |
| search_knowledge_base_for_field | 字段级检索 |
| write_excel | 写入单个字段 |
| write_excel_batch | 批量写入字段 |

### ExcelAgent (混合模式)

**核心策略**: Python直接检索知识库 + 模型调用写入工具

```python
from src.agents.excel_agent import create_excel_agent

# 创建Agent
agent = create_excel_agent()

# 分析Excel空白字段
result = await agent.analyze_excel("项目数据.xlsx")

# 自动填充 (Python检索 + 模型写入)
result = await agent.fill_excel("项目数据.xlsx", threshold=0.7)

# 检索特定字段
result = await agent.query_for_field("项目名称", "杭州市")
```

### 关键改进

1. **混合模式**: Python直接检索知识库（可靠性100%），模型只负责写入
2. **线程池**: 解决异步上下文中调用同步代码的问题
3. **正则提取**: 从检索结果中提取特定字段值
4. **分批写入**: 每批10个字段，避免模型认知负担

### CLI命令

```bash
# 知识库管理
python scripts/kb.py init                  # 初始化
python scripts/kb.py add data/knowledge_base/  # 添加文档
python scripts/kb.py query "城乡规划"      # 检索
python scripts/kb.py stats                 # 统计

# Excel智能填充
python scripts/fill_excel.py analyze 项目数据.xlsx  # 分析
python scripts/fill_excel.py fill 项目数据.xlsx     # 填充
python scripts/fill_excel.py query "项目名称"       # 检索字段
```

## CONVENTIONS

### 代码规范
- **格式化**: `black src/` (无配置文件, 使用默认)
- **检查**: `flake8 src/` (无配置文件)
- **测试**: `pytest tests/`
- **编码**: UTF-8, 中文文档字符串

### 模块导入
```python
# 标准库 → 第三方库 → 本地模块
from typing import Dict, Any
from pydantic import BaseModel
from src.utils.logger import logger
from src.rag import KnowledgeBase, Retriever
from src.agents import ExcelAssistantAgent
```

### Pydantic模型
- 字段使用中文命名: `项目名称: str`
- 必须提供`get_sample_data()`测试函数
- 使用`@validator`进行数据校验

### Agent开发 (新版 API)
- 使用 `OpenAIChatCompletionClient` 作为模型客户端
- 加载 `templates/prompts/*.md` 作为 system_message
- 实现 `_build_user_message()` 格式化输入
- 通过 `AutoGenOrchestrator` 协调调用
- **异步调用**: 使用 `await agent.run(task=...)` 或 `asyncio.run()`

## ANTI-PATTERNS (THIS PROJECT)

### 数据完整性
- **NEVER** 编造数据 - 缺失信息标注"待补充"
- **MUST** 使用用户提供的Excel数据
- **MUST** 引用相关标准并标注来源

### AutoGen配置 (新版 API)
- 不再使用 `llm_config` 字典
- 使用 `OpenAIChatCompletionClient` 初始化模型客户端
- 不再需要 `UserProxyAgent`
- Agent 调用使用 `await agent.run(task=...)`

### RAG知识库
- ChromaDB要求metadata非空
- Embedding维度: 1024 (text-embedding-v3)
- 默认检索: Top-5, 阈值0.7

### 数据验证
- 备选方案: **必须2个** (不多不少)
- 征求意见: **至少3个部门**
- 四至范围: **必须包含东南西北**
- 选址原则: **至少5条**

### 文档操作
- 删除段落: **从后往前删除** (避免索引变化)
- 插入段落: **从后往前插入** (保持顺序)

### 内容生成
- 禁止遗漏子节 (第1章6节, 第2章9节)
- 禁止口语化表达 (避免"很好的"、"非常")
- 结论必须明确, 不得模糊

## COMMANDS

```bash
# 环境配置
conda env create -f environment.yml && conda activate xuanzhi

# API配置 (.env)
DASHSCOPE_API_KEY=sk-xxx
MODEL_NAME=qwen-plus

# 测试验证
python test_qwen.py                      # LLM连接验证
python scripts/test_all_agents.py        # 全部Agent测试
python scripts/test_excel_input.py all   # Excel输入测试
python scripts/create_excel_template.py  # 创建Excel模板

# RAG测试
pytest tests/test_rag/ -v --cov=src/rag  # RAG模块测试 (28个测试)

# Wave 3-4测试
pytest tests/test_wave3_retriever.py tests/test_wave4_excel_agent.py -v

# 代码质量
black src/ && flake8 src/ && pytest tests/
```

## NOTES

### 入口点
无`main.py`, 通过`scripts/`中的测试脚本启动:
- `test_all_agents.py` - 全部Agent验证
- `test_excel_input.py` - Excel流程测试
- `test_end_to_end.py` - 端到端测试
- `kb.py` - CLI知识库命令 (Wave 3)
- `fill_excel.py` - CLI Excel填充 (Wave 4)

### 数据输入方式
1. **Excel模板** (推荐): `orchestrator.generate_full_report("项目数据.xlsx")`
2. **代码调用**: 直接传递Pydantic模型
3. **智能填充**: `ExcelAssistantAgent.fill_excel()`

### 特殊文件
- `.env` - API密钥配置 (不提交)
- `templates/excel_templates/项目数据模板.xlsx` - 数据输入模板
- `templates/word_templates/标准模板.docx` - 报告输出模板
- `data/chroma_db/` - ChromaDB向量数据库

### 开发进度
- ✅ Wave 1: 环境验证
- ✅ Wave 2: 知识库核心
- ✅ Wave 3: 检索服务 (Retriever + CLI)
- ✅ Wave 4: Excel智能体 (Tools + Agent + CLI)
- ✅ Wave 5: 6章Agent集成知识库
- ✅ Wave FINAL: 文档和验证

### 测试覆盖率
```
Wave 1-2: 28个测试通过
Wave 3: 10个测试通过
Wave 4: 16个测试通过
Wave 5: 19个测试通过
────────────────────────
总计: 97个测试通过, 73个测试通过 (核心功能)
```

### 未实现模块
- `src/api/` - FastAPI Web接口 (计划中)
## API VERSION

### 新版 API (autogen-agentchat 0.7.x)

```python
# 导入
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

# 模型客户端
model_client = OpenAIChatCompletionClient(
    model="qwen-plus",
    api_key="sk-xxx",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# Agent 创建
agent = AssistantAgent(
    name="my_agent",
    model_client=model_client,
    system_message="你是一个专业助手。",
)

# Agent 调用 (异步)
result = await agent.run(task="请生成报告...")
content = result.messages[-1].content
```

### 旧版 API (已废弃)

```python
# 以下方式不再使用:
# - from autogen import AssistantAgent
# - llm_config = {"config_list": [...]}
# - UserProxyAgent + initiate_chat()
```