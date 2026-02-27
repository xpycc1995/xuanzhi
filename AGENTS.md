# PROJECT KNOWLEDGE BASE

**Generated:** 2026-02-27
**Commit:** no-git
**Branch:** no-git
**AutoGen Version:** autogen-agentchat 0.7.x

## OVERVIEW

规划选址论证报告AI智能体协作系统 - 基于AutoGen框架的多Agent协作系统，自动生成规划选址综合论证报告。Python 3.10+, FastAPI + AutoGen + Pydantic + python-docx.
本地开发环境：/Users/yc/miniconda/envs/xuanzhi/bin
**重要:** 项目已迁移至新版 `autogen-agentchat` API (0.7.x)，不再使用旧版 `pyautogen`。

**项目状态: ✅ 全部6章Agent开发完成**

## STRUCTURE
```
xuanzhi/
├── src/                    # 核心源码 (三层架构)
│   ├── agents/             # Agent层 - 6个专业AI智能体
│   ├── models/             # 数据层 - 6个Pydantic验证模型
│   ├── services/           # 服务层 - 编排/文档/解析
│   ├── core/               # 配置 - LLM配置加载
│   └── utils/              # 工具 - 日志配置
├── templates/
│   ├── prompts/            # Agent提示词模板 (6个*.md)
│   ├── word_templates/     # Word报告模板
│   └── excel_templates/    # Excel数据输入模板
├── scripts/                # 测试脚本入口
├── tests/                  # pytest单元测试
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
| 提示词模板 | `templates/prompts/*.md` | 6个章节模板 |
| 测试入口 | `scripts/test_all_agents.py` | 全部Agent验证 |

## DATA FLOW

```
Excel模板 → ExcelParser → Pydantic模型 → Agent生成 → DocumentService → Word报告
                    ↓
              AutoGenOrchestrator (协调中心)
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

# 代码质量
black src/ && flake8 src/ && pytest tests/
```

## NOTES

### 入口点
无`main.py`, 通过`scripts/`中的测试脚本启动:
- `test_all_agents.py` - 全部Agent验证
- `test_excel_input.py` - Excel流程测试
- `test_end_to_end.py` - 端到端测试

### 数据输入方式
1. **Excel模板** (推荐): `orchestrator.generate_full_report("项目数据.xlsx")`
2. **代码调用**: 直接传递Pydantic模型

### 特殊文件
- `.env` - API密钥配置 (不提交)
- `templates/excel_templates/项目数据模板.xlsx` - 数据输入模板
- `templates/word_templates/标准模板.docx` - 报告输出模板

### 未实现模块
- `src/api/` - FastAPI Web接口 (计划中)
- `config/` - 配置目录 (为空, 配置在根目录)

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