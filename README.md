# 规划选址论证报告AI智能体协作系统

基于AutoGen框架的多Agent协作系统，自动生成规划选址综合论证报告。

**项目状态**: ✅ 全部6章Agent + RAG知识库 + Excel智能体 | **版本**: autogen-agentchat 0.7.x

## 项目简介

本系统通过6个专业AI Agent的协作，实现规划选址综合论证报告的智能编制，将传统2-4周的人工编制时间缩短至小时级。

**已实现章节**:
- 第1章: 项目概况
- 第2章: 选址分析
- 第3章: 合规性分析
- 第4章: 合理性分析
- 第5章: 节地分析
- 第6章: 结论

### 核心功能

- ✅ **多Agent协作**: 6个专业Agent分工协作，确保报告质量
- ✅ **智能内容生成**: 支持多种LLM（阿里云百炼Qwen/OpenAI GPT）
- ✅ **标准化输出**: 严格按照标准模板生成Word文档
- ✅ **Excel数据输入**: 支持通过Excel模板输入项目数据
- ✅ **Excel智能填写**: ExcelAssistantAgent自动填充空白字段
- ✅ **RAG知识库**: 基于ChromaDB的本地向量检索增强生成
- ✅ **多格式文档解析**: 支持PDF/Word/Markdown/TXT
- ✅ **百炼Embedding**: text-embedding-v3，1024维向量
- ✅ **统一CLI**: `main.py` 提供完整命令行接口
- ✅ **新版API**: 基于autogen-agentchat 0.7.x，异步调用更高效
- ✅ **低成本**: 使用国产模型可节省70-90%成本

### 技术栈

| 类别 | 技术 |
|------|------|
| Agent框架 | AutoGen-agentchat 0.7.x (微软开源) |
| LLM服务 | 阿里云百炼 Qwen / OpenAI GPT-4 |
| 向量数据库 | ChromaDB 1.5.1 |
| Embedding | 百炼 text-embedding-v3 (1024维) |
| 文档解析 | pypdf, python-docx |
| 文档生成 | python-docx |
| 数据验证 | Pydantic |
| CLI框架 | typer + rich |
| 开发语言 | Python 3.10+ |
| 环境管理 | Conda / venv |

## 快速开始

### 1. 环境准备

**方式1: 使用Conda（推荐）**
```bash
conda env create -f environment.yml
conda activate xuanzhi
```

**方式2: 使用venv**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 配置API密钥

**阿里云百炼（推荐，低成本）**
```bash
# 1. 获取API密钥: https://bailian.console.aliyun.com/
# 2. 配置密钥
cp .env.example .env

# 3. 编辑.env文件:
DASHSCOPE_API_KEY=sk-你的API密钥
MODEL_NAME=qwen-plus

# 4. 验证配置
python main.py status
```

### 3. 生成报告

```bash
# 初始化知识库
python main.py kb init
python main.py kb add data/knowledge_base/

# 生成报告
python main.py generate 项目数据.xlsx
```

## CLI命令 (统一入口 main.py)

### 报告生成

```bash
python main.py generate 项目数据.xlsx                    # 生成报告
python main.py generate 项目数据.xlsx -o output/报告.docx # 指定输出路径
python main.py generate 项目数据.xlsx --no-knowledge     # 不使用知识库
python main.py generate 项目数据.xlsx -v                 # 详细输出
```

### 知识库管理

```bash
python main.py kb init                    # 初始化
python main.py kb add data/knowledge_base/ # 添加文档
python main.py kb query "城乡规划"        # 检索
python main.py kb query "规划" -k 10      # 指定返回数量
python main.py kb stats                   # 统计
python main.py kb clear --force           # 清空
```

### 系统命令

```bash
python main.py status     # 显示系统状态
python main.py version    # 显示版本信息
python main.py quickstart # 快速开始指南
python main.py --help     # 查看帮助
```

## 测试命令

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
pytest tests/ -m "unit" -v          # 单元测试
pytest tests/ -m "integration" -v   # 集成测试
pytest tests/ -m "rag" -v           # RAG知识库测试
```

## 项目结构

```
xuanzhi/
├── main.py               # 统一CLI入口
├── src/
│   ├── agents/           # Agent层 - 7个专业AI智能体
│   ├── models/           # 数据层 - Pydantic验证模型（中文命名）
│   ├── services/         # 服务层 - 编排/文档/解析
│   ├── rag/              # RAG知识库 - ChromaDB + 百炼Embedding
│   ├── tools/            # 工具层 - Excel工具
│   └── core/             # 配置 - LLM配置加载
├── templates/
│   ├── prompts/          # Agent提示词模板（6个*.md）
│   ├── word_templates/   # Word报告模板
│   └── excel_templates/  # Excel数据输入模板
├── tests/                # pytest单元测试
├── scripts/              # 辅助脚本
└── data/chroma_db/       # ChromaDB向量数据库
```

## Agent架构

| 章节 | Agent | 数据模型 | 提示词模板 |
|-----|-------|---------|-----------|
| 第1章 | ProjectOverviewAgent | ProjectOverviewData | project_overview.md |
| 第2章 | SiteSelectionAgent | SiteSelectionData | site_selection.md |
| 第3章 | ComplianceAnalysisAgent | ComplianceData | compliance_analysis.md |
| 第4章 | RationalityAnalysisAgent | RationalityData | rationality_analysis.md |
| 第5章 | LandUseAnalysisAgent | LandUseData | land_use_analysis.md |
| 第6章 | ConclusionAgent | ConclusionData | conclusion.md |
| Excel | ExcelAssistantAgent | - | - |

## 新版API使用（autogen-agentchat 0.7.x）

### 模型客户端

```python
from autogen_ext.models.openai import OpenAIChatCompletionClient

model_client = OpenAIChatCompletionClient(
    model="qwen-plus",
    api_key="sk-xxx",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
```

### Agent创建

```python
from autogen_agentchat.agents import AssistantAgent

agent = AssistantAgent(
    name="my_agent",
    model_client=model_client,
    system_message="你是一个专业助手。",
)

# 异步调用
result = await agent.run(task="请生成报告...")
content = result.messages[-1].content
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

## RAG知识库使用

```python
from src.rag import KnowledgeBase, Retriever

# 知识库操作
kb = KnowledgeBase()
kb.add_documents(["文档内容1", "文档内容2"])
results = kb.search("查询", n_results=5)

# 检索服务
retriever = Retriever()
retriever.ingest_file("doc.pdf")
results = retriever.search("查询", threshold=0.7)
context = retriever.search_with_context("项目选址原则")
```

## 代码规范

```bash
black src/           # 格式化（无配置文件，使用默认）
flake8 src/          # 代码检查（无配置文件）
pytest tests/        # 运行测试
```

### 模块导入顺序

```python
# 1. 标准库
from typing import Dict, Any, Optional, List

# 2. 第三方库
from pydantic import BaseModel, Field, validator
from autogen_agentchat.agents import AssistantAgent

# 3. 本地模块
from src.utils.logger import logger
from src.rag import KnowledgeBase
```

### Pydantic模型规范

```python
class XxxData(BaseModel):
    # 字段使用中文命名
    项目名称: str = Field(..., description="项目全称")
    
    @validator('项目名称')
    def validate_name(cls, v):
        if not v:
            raise ValueError("项目名称不能为空")
        return v
    
    def to_dict(self) -> Dict[str, Any]: ...

# 必须提供示例数据函数
def get_sample_xxx_data() -> XxxData:
    return XxxData(项目名称="示例项目")
```

## 测试覆盖率

| 模块 | 覆盖率 |
|------|--------|
| src/rag/knowledge_base.py | 80% ✅ |
| src/rag/text_chunker.py | 82% ✅ |
| src/rag/document_processor.py | 40% |
| src/rag/embedding.py | 40% |

**测试统计**: Wave 1-2: 28个 | Wave 3: 10个 | Wave 4: 16个 | Wave 5: 19个 | **总计: 97个测试通过**

## 开发进度

| Wave | 阶段 | 状态 |
|------|------|------|
| Wave 1 | 环境验证 | ✅ 完成 |
| Wave 2 | 知识库核心 | ✅ 完成 |
| Wave 3 | 检索服务 | ✅ 完成 |
| Wave 4 | Excel智能体 | ✅ 完成 |
| Wave 5 | 6章Agent集成 | ✅ 完成 |
| Wave FINAL | 文档和验证 | ✅ 完成 |

## 许可证

MIT License

## 技术支持

- 项目位置: `/Users/yc/Applications/python/xuanzhi`
- 开发环境: `/Users/yc/miniconda/envs/xuanzhi/bin`
- 技术栈: Python 3.10+ + AutoGen-agentchat 0.7.x + Pydantic + python-docx + ChromaDB