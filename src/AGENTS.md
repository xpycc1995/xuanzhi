# SRC MODULE KNOWLEDGE BASE

## OVERVIEW
核心源码层, 三层架构: Agent → Service → Model, 编排器为协调中心.

**AutoGen 版本:** autogen-agentchat 0.7.x

## ARCHITECTURE

```
┌─────────────────────────────────────────────────────────┐
│                   AutoGenOrchestrator                    │
│  (协调中心: Agent管理, 异步调用, 内容提取)                  │
└─────────────────────────────────────────────────────────┘
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  agents/      │    │  services/    │    │  models/      │
│  项目概况Agent │    │  excel_parser │    │  Pydantic    │
│  选址分析Agent │    │  document_svc │    │  数据验证     │
└───────────────┘    └───────────────┘    └───────────────┘
        │                    │                    │
        └────────────────────┴────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  core/           │
                    │  autogen_config  │
                    │  (模型客户端)    │
                    └──────────────────┘
```

## WHERE TO LOOK

| 组件 | 文件 | 职责 |
|------|------|------|
| 编排器 | `services/autogen_orchestrator.py` | Agent协调, 异步调用 |
| Excel解析 | `services/excel_parser.py` | 多Sheet解析, 数据映射 |
| 文档生成 | `services/document_service.py` | Word模板替换 |
| Agent基类 | `agents/project_overview_agent.py` | Agent创建模式 |
| 数据模型 | `models/site_selection_data.py` | Pydantic验证模式 |
| LLM配置 | `core/autogen_config.py` | 模型客户端创建 |

## MODULE DEPENDENCIES

```
agents/ ──► models/ (数据结构)
    │
    └──► services/autogen_orchestrator (编排)
              │
              ├──► services/excel_parser (输入)
              ├──► services/document_service (输出)
              └──► core/autogen_config (配置)
```

## INTERNAL PATTERNS

### 编排器调用流程 (新版 API)
```python
# 1. 初始化
from src.core.autogen_config import get_model_client

model_client = get_model_client()
orchestrator = AutoGenOrchestrator(model_client=model_client)

# 2. 从Excel生成
chapters = orchestrator.generate_from_excel("数据.xlsx")

# 3. 或直接调用
chapter_1 = orchestrator.generate_chapter_1(project_data)
chapter_2 = orchestrator.generate_chapter_2(site_data)
```

### Agent创建模式 (新版 API)
```python
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

class MyAgent:
    def __init__(self, model_client: OpenAIChatCompletionClient):
        self.model_client = model_client
        self.system_message = self._load_template()
        self.agent = AssistantAgent(
            name="my_agent",
            model_client=self.model_client,
            system_message=self.system_message,
        )
    
    async def generate(self, data) -> str:
        user_message = self._build_user_message(data)
        result = await self.agent.run(task=user_message)
        return result.messages[-1].content
```

### 数据模型模式
```python
class MyData(BaseModel):
    字段名: str = Field(..., description="描述")
    
    @validator('字段名')
    def validate_field(cls, v): ...
    
    def get_formatted_data(self) -> str: ...

def get_sample_data() -> MyData: ...
```

### 服务层模式
```python
class MyService:
    def __init__(self, file_path: str):
        self._validate_file()  # 验证输入
    
    def process(self) -> Result:
        # 处理逻辑
        return result
    
    def close(self): ...  # 资源清理
```

## CRITICAL PATTERNS

### 模型客户端配置 (新版 API)
```python
from src.core.autogen_config import get_model_client

# 自动从环境变量加载
model_client = get_model_client()

# 或手动指定
model_client = OpenAIChatCompletionClient(
    model="qwen-plus",
    api_key="sk-xxx",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
```

### Agent异步调用模式
```python
# 异步生成
async def generate_content():
    agent = orchestrator.get_agent("project_overview")
    content = await agent.generate(project_data)
    return content

# 同步包装
import asyncio
content = asyncio.run(generate_content())

# 或通过编排器
content = orchestrator.generate_chapter_1(project_data)
```

### 错误处理模式
```python
# Agent响应获取 (新版 API)
result = await agent.run(task=user_message)

if result and result.messages:
    content = result.messages[-1].content
else:
    raise ValueError("Agent没有返回任何内容")
```

### Excel解析容错
```python
# 支持多种列名格式
面积值 = row.get("面积") or row.get("面积(平方米)") or row.get("面积（平方米）")

# 布尔值解析
def _parse_bool(self, value) -> bool:
    return value.lower() in ("是", "true", "yes", "1", "√")
```