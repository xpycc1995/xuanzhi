# 规划选址论证报告AI智能体协作系统

基于AutoGen框架的多Agent协作系统,用于自动生成规划选址综合论证报告。

**项目状态**: ✅ 全部6章Agent + RAG知识库 + Excel智能体 | 版本: autogen-agentchat 0.7.x

## 项目简介

本系统通过6个专业AI Agent的协作,实现规划选址综合论证报告的智能编制,将传统2-4周的人工编制时间缩短至小时级。

**已实现章节**:
- 第1章: 项目概况
- 第2章: 选址分析
- 第3章: 合规性分析
- 第4章: 合理性分析
- 第5章: 节地分析
- 第6章: 结论

### 核心功能

- ✅ **多Agent协作**: 6个专业Agent分工协作,确保报告质量
- ✅ **智能内容生成**: 支持多种LLM(阿里云百炼Qwen/OpenAI GPT)
- ✅ **标准化输出**: 严格按照标准模板生成Word文档
- ✅ **Excel数据输入**: 支持通过Excel模板输入项目数据
- ✅ **Excel智能填写**: ExcelAssistantAgent自动填充空白字段
- ✅ **RAG知识库**: 基于ChromaDB的本地向量检索增强生成
- ✅ **多格式文档解析**: 支持PDF/Word/Markdown/TXT
- ✅ **百炼Embedding**: text-embedding-v3, 1024维向量
- ✅ **CLI命令**: kb.py知识库管理 + fill_excel.py智能填充
- ✅ **新版API**: 基于autogen-agentchat 0.7.x,异步调用更高效
- ✅ **低成本**: 使用国产模型可节省70-90%成本

### 技术栈

- **Agent框架**: AutoGen-agentchat 0.7.x (微软开源)
- **LLM服务**: 阿里云百炼 Qwen / OpenAI GPT-4
- **向量数据库**: ChromaDB 1.5.1
- **Embedding**: 百炼 text-embedding-v3 (1024维)
- **文档解析**: pypdf, python-docx
- **文档生成**: python-docx
- **数据验证**: Pydantic
- **CLI框架**: typer + rich
- **开发语言**: Python 3.10+
- **环境管理**: Conda / venv

## 项目结构

```
xuanzhi/
├── src/                      # 核心源码 (三层架构)
│   ├── agents/               # Agent层 - 7个专业AI智能体
│   │   ├── project_overview_agent.py
│   │   ├── site_selection_agent.py
│   │   ├── compliance_analysis_agent.py
│   │   ├── rationality_analysis_agent.py
│   │   ├── land_use_analysis_agent.py
│   │   ├── conclusion_agent.py
│   │   └── excel_assistant_agent.py    # Excel智能体 (Wave 4)
│   ├── models/               # 数据层 - 6个Pydantic验证模型
│   ├── services/             # 服务层 - 编排/文档/解析
│   ├── rag/                  # RAG知识库 - 向量检索增强生成
│   │   ├── document_processor.py
│   │   ├── text_chunker.py
│   │   ├── knowledge_base.py
│   │   ├── embedding.py
│   │   └── retriever.py      # 检索服务 (Wave 3)
│   ├── tools/                # 工具层 - Excel工具 (Wave 4)
│   │   └── excel_tools.py
│   ├── core/                 # 配置 - LLM配置加载
│   └── utils/                # 工具 - 日志配置
├── templates/
│   ├── prompts/               # Agent提示词模板 (6个*.md)
│   ├── word_templates/        # Word报告模板
│   └── excel_templates/       # Excel数据输入模板
├── scripts/                  # 测试脚本入口
│   ├── test_all_agents.py
│   ├── kb.py                 # CLI知识库命令 (Wave 3)
│   └── fill_excel.py         # CLI Excel填充命令 (Wave 4)
├── tests/                    # pytest单元测试
│   ├── test_rag/             # RAG知识库测试 (38个测试)
│   ├── test_wave3_retriever.py
│   └── test_wave4_excel_agent.py
├── data/
│   ├── knowledge_base/       # 知识库文档存储
│   └── chroma_db/            # ChromaDB向量数据库
├── output/                   # 运行时输出 (报告/日志)
├── environment.yml           # Conda环境配置
├── requirements.txt          # Python依赖
└── .env                      # API密钥配置 (不提交)
```

## 快速开始

### 1. 环境准备

**方式1: 使用Conda(推荐)**
```bash
# 创建并激活环境
conda env create -f environment.yml
conda activate xuanzhi
```

**方式2: 使用venv**
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置API密钥

**选项1: 阿里云百炼(推荐,低成本)**
```bash
# 1. 获取API密钥: https://bailian.console.aliyun.com/
# 2. 配置密钥
cp .env.example .env

# 3. 编辑.env文件:
DASHSCOPE_API_KEY=sk-你的API密钥
MODEL_NAME=qwen-plus

# 4. 验证配置
python test_qwen.py
```

### 3. 运行测试

```bash
# 测试LLM连接
python test_qwen.py

# 测试全部Agent
python scripts/test_all_agents.py

# 测试Excel输入流程
python scripts/test_excel_input.py all

# 运行RAG知识库测试
pytest tests/test_rag/ -v --cov=src/rag

# 运行Wave 3-4测试
pytest tests/test_wave3_retriever.py tests/test_wave4_excel_agent.py -v

# 运行全部测试
pytest tests/
```

## CLI命令

### 知识库管理 (Wave 3)

```bash
# 初始化知识库
python scripts/kb.py init

# 添加文档
python scripts/kb.py add data/knowledge_base/

# 检索
python scripts/kb.py query "城乡规划要求" --top-k 5 --threshold 0.7

# 统计
python scripts/kb.py stats

# 列出文档
python scripts/kb.py list --limit 20

# 清空
python scripts/kb.py clear --force
```

### Excel智能填充 (Wave 4)

```bash
# 分析Excel空白字段
python scripts/fill_excel.py analyze 项目数据.xlsx

# 自动填充Excel
python scripts/fill_excel.py fill 项目数据.xlsx

# 输出到新文件
python scripts/fill_excel.py fill 项目数据.xlsx -o 填充后.xlsx

# 检索特定字段
python scripts/fill_excel.py query "项目名称" -c "杭州市"

# 列出工具
python scripts/fill_excel.py tools
```

## RAG知识库使用

### 知识库初始化

```python
from src.rag import KnowledgeBase

# 初始化知识库
kb = KnowledgeBase()
print(f"当前文档数: {kb.count()}")

# 添加文档
texts = ["规划选址应当符合城乡规划要求。", "项目建设用地应当节约集约用地。"]
kb.add_documents(texts)

# 语义检索
results = kb.search("城乡规划", n_results=5)
for r in results:
    print(f"相似度: {1-r['distance']:.2f}, 内容: {r['content'][:50]}...")
```

### Retriever检索服务 (Wave 3)

```python
from src.rag import Retriever

# 初始化
retriever = Retriever()

# 摄取文档
retriever.ingest_file("regulations.pdf")
retriever.ingest_directory("data/knowledge_base/")

# 语义检索
results = retriever.search("城乡规划要求", n_results=5, threshold=0.7)

# 获取LLM上下文
context = retriever.search_with_context("项目选址原则")
```

### 文档处理

```python
from src.rag import DocumentProcessor, TextChunker

# 处理多种格式文档
processor = DocumentProcessor()
doc = processor.process_file("regulations.pdf")  # 或 .docx, .md, .txt

# 文本分块
chunker = TextChunker(chunk_size=512, overlap=128)
chunks = chunker.chunk_text(doc.content)
```

## Agent架构

系统包含7个专业Agent,对应报告的6个章节 + Excel智能体:

| 章节 | Agent | 数据模型 | 提示词模板 | 状态 |
|-----|-------|---------|-----------|------|
| 第1章 | ProjectOverviewAgent | ProjectOverviewData | project_overview.md | ✅ |
| 第2章 | SiteSelectionAgent | SiteSelectionData | site_selection.md | ✅ |
| 第3章 | ComplianceAnalysisAgent | ComplianceData | compliance_analysis.md | ✅ |
| 第4章 | RationalityAnalysisAgent | RationalityData | rationality_analysis.md | ✅ |
| 第5章 | LandUseAnalysisAgent | LandUseData | land_use_analysis.md | ✅ |
| 第6章 | ConclusionAgent | ConclusionData | conclusion.md | ✅ |
| Excel | ExcelAssistantAgent | - | - | ✅ |

## 数据流程

```
Excel模板 → ExcelParser → Pydantic模型 → Agent生成 → DocumentService → Word报告
                    ↓
              AutoGenOrchestrator (协调中心)
                    ↓
              KnowledgeBase (RAG知识库)
                    ↓
              ExcelAssistantAgent (智能填充)
```

## 新版API使用

**autogen-agentchat 0.7.x** 异步调用示例:

```python
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

### ExcelAssistantAgent使用

```python
from src.agents.excel_assistant_agent import create_excel_agent

# 创建Excel智能体
agent = create_excel_agent()

# 分析Excel
result = await agent.analyze_excel("项目数据.xlsx")

# 自动填充
result = await agent.fill_excel("项目数据.xlsx", threshold=0.7)

# 检索特定字段
result = await agent.query_for_field("项目名称", "杭州市")
```

## 测试覆盖率

```
src/rag/knowledge_base.py     80% ✅
src/rag/text_chunker.py       82% ✅
src/rag/document_processor.py 40%
src/rag/embedding.py          40%
src/rag/retriever.py          新增
─────────────────────────────────────────
Wave 1-2: 28个测试通过
Wave 3: 10个测试通过
Wave 4: 16个测试通过
Wave 5: 19个测试通过
────────────────────────
总计: 97个测试通过

## 开发进度

| Wave | 阶段 | 状态 | 完成时间 |
|------|------|------|----------|
| Wave 1 | 环境验证 | ✅ 完成 | 2026-02-27 |
| Wave 2 | 知识库核心 | ✅ 完成 | 2026-02-27 |
| Wave 3 | 检索服务 | ✅ 完成 | 2026-02-27 |
| Wave 4 | Excel智能体 | ✅ 完成 | 2026-02-27 |
| Wave 5 | 6章Agent集成 | ✅ 完成 | 2026-02-27 |
| Wave FINAL | 文档和验证 | ✅ 完成 | 2026-02-27 |
## 代码规范

```bash
# 格式化代码
black src/

# 代码检查
flake8 src/

# 运行测试
pytest tests/
```

## 贡献指南

欢迎提交Issue和Pull Request!

## 许可证

MIT License

## 技术支持

- 项目位置: `/Users/yc/Applications/python/xuanzhi`
- 开发环境: `/Users/yc/miniconda/envs/xuanzhi/bin`
- 创建日期: 2026-02-27
- 技术栈: Python 3.10+ + AutoGen-agentchat 0.7.x + Pydantic + python-docx + ChromaDB