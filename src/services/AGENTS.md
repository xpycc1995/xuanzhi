# SERVICES MODULE KNOWLEDGE BASE

## OVERVIEW
服务层 - 编排器、Excel解析、Word文档生成的实现层. 三大核心服务.

**AutoGen 版本:** autogen-agentchat 0.7.x

## FILES

| 文件 | 行数 | 职责 |
|------|------|------|
| `autogen_orchestrator.py` | ~370 | Agent协调中心, 异步调用管理 |
| `excel_parser.py` | ~630 | Excel模板解析, Sheet读取 |
| `document_service.py` | ~780 | Word模板操作, Markdown解析 |

## CORE INTERFACES

### AutoGenOrchestrator (新版 API)
```python
from src.core.autogen_config import get_model_client

class AutoGenOrchestrator:
    def __init__(self, model_client: OpenAIChatCompletionClient = None)
    def get_agent(self, agent_name: str) -> AssistantAgent
    def generate_chapter_1(self, project_data: Dict) -> str
    def generate_chapter_2(self, site_data: SiteSelectionData) -> str
    def generate_chapter_3(self, compliance_data: ComplianceData) -> str
    def generate_from_excel(self, excel_path: str) -> Dict[str, str]
    def generate_full_report(self, excel_path: str, output_path: str = None) -> str
```

### ExcelParser
```python
class ExcelParser:
    SHEETS = ["项目基本信息", "备选方案", "场地条件", "敏感条件", 
              "施工运营", "征求意见", "方案比选"]
    
    def parse_project_overview(self) -> ProjectOverviewData
    def parse_site_selection(self) -> SiteSelectionData
    def parse_compliance(self) -> ComplianceData
    def parse_all(self) -> Tuple[ProjectOverviewData, SiteSelectionData, ComplianceData]
    def close(self)  # 必须调用, 释放workbook
```

### DocumentService
```python
class DocumentService:
    def generate_report(self, project_data: Dict, chapters: Dict, 
                        output_path: str = None) -> str
    def generate_chapter_2(self, content: str, site_data) -> str
```

## CRITICAL IMPLEMENTATION DETAILS

### 文档操作顺序 (CRITICAL)
```python
# 删除段落: 从后往前删除, 避免索引变化
for i in sorted(indices_to_delete, reverse=True):
    del paragraphs[i]

# 插入段落: 从后往前插入, 保持顺序
for content in reversed(contents):
    insert_paragraph_before(target, content)
```

### Excel Sheet读取模式
```python
# 三种Sheet格式:
_read_key_value_sheet()   # 键值对 (项目基本信息)
_read_category_sheet()    # 分类格式 (场地条件)
_read_table_sheet()       # 表格格式 (备选方案)
```

### Agent延迟导入模式 (新版 API)
```python
def _initialize_agents(self):
    # 延迟导入, 避免循环依赖
    from src.agents.project_overview_agent import ProjectOverviewAgent
    from src.agents.site_selection_agent import SiteSelectionAgent
    from src.agents.compliance_analysis_agent import ComplianceAnalysisAgent
    
    # 初始化 Agent, 传入 model_client
    self._agents["project_overview"] = ProjectOverviewAgent(self.model_client)
    self._agents["site_selection"] = SiteSelectionAgent(self.model_client)
    self._agents["compliance_analysis"] = ComplianceAnalysisAgent(self.model_client)
```

### 异步调用包装
```python
import asyncio

def generate_chapter_1(self, project_data: Dict) -> str:
    """同步方法包装异步调用"""
    agent = self.get_agent("project_overview")
    
    # 检查是否已在异步上下文
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # 在线程池中运行
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                asyncio.run,
                agent.generate(project_data)
            )
            return future.result()
    else:
        # 直接运行
        return asyncio.run(agent.generate(project_data))
```

## ERROR HANDLING

### 必检错误
```python
# Excel解析
if len(alternatives) < 2:
    raise ExcelParseError("至少需要2个备选方案")

if len(opinions) < 3:
    raise ExcelParseError("至少需要3个部门意见")

# Agent响应
result = await agent.run(task=user_message)
if not result or not result.messages:
    raise ValueError("Agent没有返回任何内容")
```

### 资源清理
```python
# 使用finally确保关闭
parser = ExcelParser(path)
try:
    return parser.parse_all()
finally:
    parser.close()  # 释放workbook
```

## DATA TRANSFORMATION

### Excel → Pydantic
```
Sheet: 项目基本信息  →  ProjectOverviewData
Sheet: 备选方案      →  List[SiteAlternative]
Sheet: 场地条件      →  SiteNaturalConditions + SiteExternalConditions
Sheet: 敏感条件      →  SiteSensitiveConditions
Sheet: 施工运营      →  ConstructionConditions
Sheet: 征求意见      →  List[ConsultationOpinion]
Sheet: 方案比选      →  SchemeComparison
```

### Pydantic → Agent Message
```python
def _build_user_message(self, site_data) -> str:
    lines = []
    # 构建格式化的用户消息
    lines.append("# 项目基本信息")
    for key, value in site_data.项目基本信息.items():
        lines.append(f"{key}：{value}")
    # ...
    return "\n".join(lines)
```

### Agent Content → Word
```python
# Markdown解析 + Word替换
paragraph = parse_markdown_to_paragraph(content)
replace_placeholder(target, paragraph)
```

## API VERSION NOTES

### 新版 API 初始化
```python
# 推荐方式: 传入 model_client
from src.core.autogen_config import get_model_client

model_client = get_model_client()
orchestrator = AutoGenOrchestrator(model_client=model_client)

# 或让编排器自动创建
orchestrator = AutoGenOrchestrator()  # 内部调用 get_model_client()
```

### 旧版 API (已废弃)
```python
# 以下方式不再使用:
# orchestrator = AutoGenOrchestrator(llm_config=llm_config)
# create_orchestrator(llm_config)  # 兼容函数已废弃
```