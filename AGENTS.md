# PROJECT KNOWLEDGE BASE

**Generated:** 2026-03-01 | **Commit:** 0d906b9 | **Branch:** main
**AutoGen Version:** autogen-agentchat 0.7.x

## OVERVIEW

规划选址论证报告AI智能体协作系统 - 基于AutoGen框架的多Agent协作系统，自动生成规划选址综合论证报告。
**技术栈:** Python 3.10+ | FastAPI | AutoGen-agentchat 0.7.x | Pydantic | python-docx | ChromaDB
**本地环境:** `/Users/yc/miniconda/envs/xuanzhi/bin`

## COMMANDS

### 环境配置
```bash
conda env create -f environment.yml && conda activate xuanzhi
# API配置 (.env): DASHSCOPE_API_KEY=sk-xxx, MODEL_NAME=qwen-plus
```

### 统一CLI入口 (main.py)

```bash
# 查看帮助
python main.py --help

# 报告生成
python main.py generate 项目数据.xlsx                    # 生成报告
python main.py generate 项目数据.xlsx -o output/报告.docx # 指定输出路径
python main.py generate 项目数据.xlsx --no-knowledge     # 不使用知识库

# 知识库管理
python main.py kb init                    # 初始化
python main.py kb add data/knowledge_base/ # 添加文档
python main.py kb query "城乡规划"        # 检索
python main.py kb stats                   # 统计

# 系统状态
python main.py status                     # 显示系统状态
python main.py version                    # 显示版本信息
python main.py quickstart                 # 快速开始指南
```

### 测试命令
```bash
# 全部测试
pytest tests/ -v

# 单个测试文件
pytest tests/test_rag/test_rag_system.py -v

# 单个测试类/函数
pytest tests/test_rag/test_rag_system.py::TestKnowledgeBase -v
pytest tests/test_rag/test_rag_system.py::TestKnowledgeBase::test_add_documents -v

# 带覆盖率
pytest tests/test_rag/ -v --cov=src/rag

# 按标记运行
pytest tests/ -m "unit" -v      # 单元测试
pytest tests/ -m "integration" -v  # 集成测试
pytest tests/ -m "slow" -v      # 慢速测试
```

### 代码质量
```bash
black src/           # 格式化 (无配置文件, 使用默认)
flake8 src/          # 代码检查 (无配置文件)
```

## STRUCTURE

```
xuanzhi/
├── main.py               # 统一CLI入口
├── src/
│   ├── agents/           # Agent层 - 7个专业AI智能体
│   ├── models/           # 数据层 - Pydantic验证模型 (中文命名)
│   ├── services/         # 服务层 - 编排/文档/解析
│   ├── rag/              # RAG知识库 - ChromaDB + 百炼Embedding
│   ├── tools/            # 工具层 - Excel工具
│   └── core/             # 配置 - LLM配置加载
├── templates/
│   ├── prompts/          # Agent提示词模板 (6个*.md)
│   ├── word_templates/   # Word报告模板
│   └── excel_templates/  # Excel数据输入模板
├── tests/                # pytest单元测试
├── scripts/              # 辅助脚本
└── data/chroma_db/       # ChromaDB向量数据库
```

## WHERE TO LOOK

| 任务 | 位置 |
|------|------|
| CLI入口 | `main.py` - 统一命令行接口 |
| 添加新Agent | `src/agents/` → 传入model_client, 加载模板 |
| 修改数据结构 | `src/models/` → Pydantic BaseModel, 中文命名 |
| 调整编排逻辑 | `src/services/autogen_orchestrator_v2.py` |
| Excel解析 | `src/services/excel_parser.py` |
| Word文档生成 | `src/services/document_service.py` |
| LLM配置 | `src/core/autogen_config.py` |
| RAG知识库 | `src/rag/` |

## CODE STYLE

### 模块导入顺序
```python
# 1. 标准库
from typing import Dict, Any, Optional, List

# 2. 第三方库
from pydantic import BaseModel, Field, validator
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

# 3. 本地模块
from src.utils.logger import logger
from src.rag import KnowledgeBase, Retriever
```

### Pydantic模型规范
```python
class XxxData(BaseModel):
    # 字段使用中文命名
    项目名称: str = Field(..., description="项目全称")
    是否启用: bool = Field(default=False, description="是否启用")
    
    @validator('字段名')
    def validate_field(cls, v):
        if not v:
            raise ValueError("字段不能为空")
        return v
    
    def to_dict(self) -> Dict[str, Any]: ...
    
# 必须提供示例数据函数
def get_sample_xxx_data() -> XxxData:
    return XxxData(项目名称="示例项目", ...)
```

### Agent开发规范 (新版 API)
```python
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

class XxxAgent:
    def __init__(self, model_client: OpenAIChatCompletionClient):
        self.model_client = model_client
        self.system_message = self._load_template()
        self.agent = AssistantAgent(
            name="xxx_agent",
            model_client=self.model_client,  # 使用 model_client
            system_message=self.system_message,
        )
    
    async def generate(self, data) -> str:
        user_message = self._build_user_message(data)
        result = await self.agent.run(task=user_message)
        if result and result.messages:
            return result.messages[-1].content
        raise ValueError("Agent没有返回任何内容")
```

### 错误处理规范
```python
# 正确: 具体异常, 清晰消息
if not os.path.exists(path):
    raise FileNotFoundError(f"模板文件不存在: {path}")

# 正确: 捕获并记录
try:
    result = await agent.run(task=message)
except Exception as e:
    logger.error(f"Agent调用失败: {str(e)}")
    raise

# 错误: 空catch块
try:
    ...
except Exception:
    pass  # 禁止
```

## CRITICAL PATTERNS

### AutoGen新版 API (0.7.x)
```python
# 正确: 使用 OpenAIChatCompletionClient
from autogen_ext.models.openai import OpenAIChatCompletionClient

model_client = OpenAIChatCompletionClient(
    model="qwen-plus",
    api_key="sk-xxx",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 错误: 旧版 API (已废弃)
# - llm_config = {"config_list": [...]}
# - UserProxyAgent + initiate_chat()
```

### 模型客户端获取
```python
from src.core.autogen_config import get_model_client

# 自动从环境变量加载
model_client = get_model_client()

# 或使用缓存单例
from src.core.autogen_config import get_cached_model_client
model_client = get_cached_model_client()
```

### 异步调用模式
```python
# 方式1: 异步函数
async def generate():
    content = await agent.generate(data)
    return content

# 方式2: 同步包装
import asyncio
content = asyncio.run(agent.generate(data))

# 方式3: 已有事件循环中
loop = asyncio.get_event_loop()
if loop.is_running():
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(asyncio.run, agent.generate(data))
        content = future.result()
```

## ANTI-PATTERNS

### 数据完整性
- **NEVER** 编造数据 - 缺失信息标注"待补充"
- **MUST** 使用用户提供的Excel数据
- **MUST** 引用相关标准并标注来源

### 数据验证
- 备选方案: **必须2个** (不多不少)
- 征求意见: **至少3个部门**
- 四至范围: **必须包含东南西北**
- 选址原则: **至少5条**

### 文档操作
- 删除段落: **从后往前删除** (避免索引变化)
- 插入段落: **从后往前插入** (保持顺序)

### 类型安全
- **禁止** `as any`, `# type: ignore`
- **禁止** 空catch块 `except: pass`
- **禁止** 删除测试来通过测试

## RAG知识库配置

```python
from src.rag import KnowledgeBase, Retriever

# 默认配置
# - Embedding维度: 1024 (text-embedding-v3)
# - 分块大小: 512字符, 重叠: 128字符
# - 默认检索: Top-5, 阈值0.7

kb = KnowledgeBase()
kb.add_documents(texts)
results = kb.search("查询", n_results=5)

retriever = Retriever()
retriever.ingest_file("doc.pdf")
results = retriever.search("查询", threshold=0.7)
```

## 测试配置 (pytest.ini)

```ini
[pytest]
testpaths = tests
python_files = test_*.py
asyncio_mode = auto
markers =
    slow: 慢速测试
    integration: 集成测试
    unit: 单元测试
    rag: RAG知识库测试
```

## 已完成Agent

| 章节 | Agent | 数据模型 | 模板 |
|-----|-------|---------|------|
| 第1章 | ProjectOverviewAgent | ProjectOverviewData | project_overview.md |
| 第2章 | SiteSelectionAgent | SiteSelectionData | site_selection.md |
| 第3章 | ComplianceAnalysisAgent | ComplianceData | compliance_analysis.md |
| 第4章 | RationalityAnalysisAgent | RationalityData | rationality_analysis.md |
| 第5章 | LandUseAnalysisAgent | LandUseData | land_use_analysis.md |
| 第6章 | ConclusionAgent | ConclusionData | conclusion.md |
| Excel | ExcelAssistantAgent | - | - |