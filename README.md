# 规划选址论证报告AI智能体协作系统

基于AutoGen框架的多Agent协作系统,用于自动生成规划选址综合论证报告。

**项目状态**: ✅ 全部6章Agent开发完成 + RAG知识库 | 版本: autogen-agentchat 0.7.x

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
- ✅ **RAG知识库**: 基于ChromaDB的本地向量检索增强生成
- ✅ **多格式文档解析**: 支持PDF/Word/Markdown/TXT
- ✅ **百炼Embedding**: text-embedding-v3, 1024维向量
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
- **开发语言**: Python 3.10+
- **环境管理**: Conda / venv

## 项目结构

```
xuanzhi/
├── src/                      # 核心源码 (三层架构)
│   ├── agents/               # Agent层 - 6个专业AI智能体
│   ├── models/               # 数据层 - 6个Pydantic验证模型
│   ├── services/             # 服务层 - 编排/文档/解析
│   ├── rag/                  # RAG知识库 - 向量检索增强生成
│   ├── core/                 # 配置 - LLM配置加载
│   └── utils/                # 工具 - 日志配置
├── templates/
│   ├── prompts/               # Agent提示词模板 (6个*.md)
│   ├── word_templates/        # Word报告模板
│   └── excel_templates/       # Excel数据输入模板
├── scripts/                  # 测试脚本入口
├── tests/                    # pytest单元测试
│   └── test_rag/             # RAG知识库测试 (28个测试)
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

# 运行全部测试
pytest tests/
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

系统包含6个专业Agent,对应报告的6个章节:

| 章节 | Agent | 数据模型 | 提示词模板 | 状态 |
|-----|-------|---------|-----------|------|
| 第1章 | ProjectOverviewAgent | ProjectOverviewData | project_overview.md | ✅ |
| 第2章 | SiteSelectionAgent | SiteSelectionData | site_selection.md | ✅ |
| 第3章 | ComplianceAnalysisAgent | ComplianceData | compliance_analysis.md | ✅ |
| 第4章 | RationalityAnalysisAgent | RationalityData | rationality_analysis.md | ✅ |
| 第5章 | LandUseAnalysisAgent | LandUseData | land_use_analysis.md | ✅ |
| 第6章 | ConclusionAgent | ConclusionData | conclusion.md | ✅ |

## 数据流程

```
Excel模板 → ExcelParser → Pydantic模型 → Agent生成 → DocumentService → Word报告
                    ↓
              AutoGenOrchestrator (协调中心)
                    ↓
              KnowledgeBase (RAG知识库)
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

## 测试覆盖率

```
src/rag/knowledge_base.py     80% ✅
src/rag/text_chunker.py       82% ✅
src/rag/document_processor.py 40%
src/rag/embedding.py          40%
─────────────────────────────────────────
RAG模块测试: 28个测试通过
```

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