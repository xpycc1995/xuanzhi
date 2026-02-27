# AGENTS MODULE KNOWLEDGE BASE

## OVERVIEW
Agent层 - 专业AI智能体实现. 基于新版 autogen-agentchat AssistantAgent, 加载提示词模板生成报告章节.

**AutoGen 版本:** autogen-agentchat 0.7.x

## FILES

| 文件 | 行数 | 章节 |
|------|------|------|
| `project_overview_agent.py` | ~230 | 第1章: 项目概况 |
| `site_selection_agent.py` | ~430 | 第2章: 选址可行性分析 |
| `compliance_analysis_agent.py` | ~470 | 第3章: 合法合规性分析 |

## AGENT CLASS PATTERN (新版 API)

```python
from typing import Dict, Any, Optional
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

class XxxAgent:
    """专业Agent, 使用新版 autogen-agentchat API"""
    
    def __init__(
        self,
        model_client: OpenAIChatCompletionClient,
        prompt_template_path: str = None
    ):
        self.model_client = model_client
        self.template_path = self._get_template_path()
        self.system_message = self._load_template()
        
        # 创建 AssistantAgent
        self.agent = AssistantAgent(
            name="xxx_agent",
            model_client=self.model_client,
            system_message=self.system_message,
            description="Agent描述"
        )
    
    def _get_template_path(self) -> str:
        """计算模板路径 (相对于项目根目录)"""
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "templates", "prompts", "xxx.md"
        )
    
    def _load_template(self) -> str:
        """加载提示词模板"""
        with open(self.template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _build_user_message(self, data) -> str:
        """构建用户消息, 格式化输入数据"""
        # 子类实现
        raise NotImplementedError
    
    async def generate(self, data) -> str:
        """异步生成内容"""
        user_message = self._build_user_message(data)
        result = await self.agent.run(task=user_message)
        
        if result and result.messages:
            last_message = result.messages[-1]
            if isinstance(last_message, TextMessage):
                return last_message.content
            return str(last_message.content)
        
        raise ValueError("Agent没有返回任何内容")
    
    def get_agent(self) -> AssistantAgent:
        """返回AutoGen Agent实例"""
        return self.agent
```

## CRITICAL CONFIGURATION (新版 API)

### Agent创建
```python
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

# 创建模型客户端
model_client = OpenAIChatCompletionClient(
    model="qwen-plus",
    api_key="sk-xxx",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 创建 Agent
self.agent = AssistantAgent(
    name="xxx_agent",
    model_client=model_client,      # 使用 model_client 替代 llm_config
    system_message=self.system_message,
    description="Agent描述"
)
```

### 模板路径计算
```python
# 项目根目录计算 (向上两级)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
template_path = os.path.join(project_root, "templates", "prompts", "xxx.md")
```

### 异步调用模式
```python
# 方式1: 直接异步调用
async def generate():
    content = await agent.generate(data)
    return content

# 方式2: 同步包装
import asyncio
content = asyncio.run(agent.generate(data))

# 方式3: 在已有事件循环中
loop = asyncio.get_event_loop()
if loop.is_running():
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(asyncio.run, agent.generate(data))
        content = future.result()
else:
    content = asyncio.run(agent.generate(data))
```

## MESSAGE BUILDING PATTERN

### 项目概况Agent
```python
def _build_user_message(self, data: Dict[str, Any]) -> str:
    lines = ["# 项目信息"]
    for key, value in data.items():
        lines.append(f"- {key}：{value}")
    
    lines.append("\n" + "=" * 60)
    lines.append("请根据以上项目信息生成第1章内容。")
    return "\n".join(lines)
```

### 选址分析Agent
```python
def _build_user_message(self, site_data: SiteSelectionData) -> str:
    # 使用Pydantic模型构建详细消息
    lines = ["# 项目基本信息"]
    for key, value in site_data.项目基本信息.items():
        lines.append(f"{key}：{value}")
    
    # 添加备选方案
    lines.append("\n# 备选方案")
    for alt in site_data.备选方案:
        lines.append(f"## {alt.方案名称}")
        # ...
    
    return "\n".join(lines)
```

## ERROR HANDLING

### 模板加载失败
```python
def _load_template(self) -> str:
    if not os.path.exists(self.template_path):
        raise FileNotFoundError(f"模板文件不存在: {self.template_path}")
    
    with open(self.template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if not content:
        raise RuntimeError(f"模板文件为空: {self.template_path}")
    
    return content
```

### Agent调用失败
```python
async def generate(self, data) -> str:
    user_message = self._build_user_message(data)
    
    try:
        result = await self.agent.run(task=user_message)
    except Exception as e:
        logger.error(f"Agent调用失败: {str(e)}")
        raise
    
    if not result or not result.messages:
        raise ValueError("Agent没有返回任何内容")
    
    return result.messages[-1].content
```

### 编排器调用模式
```python
# Agent通过编排器协调
from src.core.autogen_config import get_model_client

model_client = get_model_client()
orchestrator = AutoGenOrchestrator(model_client=model_client)

# 获取Agent并异步调用
agent = orchestrator.get_agent("project_overview")
content = await agent.generate(project_data)

# 或通过编排器方法
chapter_1 = orchestrator.generate_chapter_1(project_data)
```

## TEMPLATE REQUIREMENTS

提示词模板 (`templates/prompts/*.md`) 必须包含:

1. **角色定义** - 专业背景和职责
2. **章节结构** - 子节划分和字数要求
3. **内容标准** - 专业性、准确性、逻辑性
4. **格式要求** - Markdown格式
5. **禁止事项** - 不编造数据、不遗漏子节
6. **示例** - 输出示例

## EXTENSION GUIDE

### 添加新Agent
1. 在 `src/agents/` 创建 `xxx_agent.py`
2. 使用上述模式, 实现 `_build_user_message()` 和 `async generate()`
3. 在 `templates/prompts/` 创建提示词模板
4. 在 `autogen_orchestrator.py` 注册Agent:
   ```python
   from src.agents.xxx_agent import XxxAgent
   
   # 在 _initialize_agents() 中添加
   self._agents["xxx"] = XxxAgent(self.model_client)
   ```
5. 添加对应的生成方法:
   ```python
   def generate_chapter_x(self, data) -> str:
       agent = self.get_agent("xxx")
       return asyncio.run(agent.generate(data))
   ```

## API VERSION NOTES

### 新版 API (autogen-agentchat 0.7.x)
- 使用 `OpenAIChatCompletionClient` 作为模型客户端
- Agent 接收 `model_client` 参数而非 `llm_config`
- 调用方式: `await agent.run(task=...)`
- 返回 `TaskResult`, 内容在 `result.messages[-1].content`

### 旧版 API (已废弃)
- `from autogen import AssistantAgent` - 不再使用
- `llm_config={"config_list": [...]}` - 不再使用
- `UserProxyAgent` + `initiate_chat()` - 不再使用