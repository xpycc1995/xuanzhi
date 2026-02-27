# 规划选址论证报告AI智能体协作系统

基于AutoGen框架的多Agent协作系统,用于自动生成规划选址综合论证报告。

## 项目简介

本系统通过8个专业AI Agent的协作,实现规划选址综合论证报告的智能编制,将传统2-4周的人工编制时间缩短至小时级。

### 核心功能

- ✅ **多Agent协作**: 8个专业Agent分工协作,确保报告质量
- ✅ **智能内容生成**: 支持多种LLM(阿里云百炼Qwen/OpenAI GPT)
- ✅ **标准化输出**: 严格按照标准模板生成Word文档
- ✅ **质量控制**: 三级质量检查机制,确保报告规范性
- ✅ **低成本**: 使用国产模型可节省70-90%成本

### 技术栈

- **后端框架**: FastAPI
- **Agent框架**: AutoGen (微软开源)
- **LLM服务**: 阿里云百炼 Qwen / OpenAI GPT-4
- **文档生成**: python-docx
- **开发语言**: Python 3.10+
- **环境管理**: Conda / venv

## 项目结构

```
xuanzhi/
├── src/                      # 源代码目录
│   ├── core/                 # 核心模块(AutoGen配置)
│   ├── agents/               # 专业Agent实现
│   ├── services/             # 服务层(文档、数据、编排)
│   ├── utils/                # 工具函数
│   └── api/                  # Web API接口
├── templates/                # 模板资源
│   ├── prompts/              # 提示词模板
│   └── word_templates/       # Word文档模板
├── data/                     # 数据目录
│   ├── knowledge_base/       # 知识库(法规、案例)
│   ├── gis_data/             # GIS数据
│   └── cache/                # 缓存数据
├── output/                   # 输出目录
│   ├── reports/              # 生成的报告
│   ├── charts/               # 生成的图表
│   └── logs/                 # 日志文件
├── tests/                    # 测试目录
├── scripts/                  # 脚本目录
└── config/                   # 配置文件
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

**选项2: OpenAI**
```bash
# 配置OpenAI密钥
cp .env.example .env
# 编辑.env设置: OPENAI_API_KEY=sk-your-key
```

### 3. 准备模板文件

模板文件已就位,无需额外操作。

### 4. 运行测试

```bash
# 运行MVP测试(单Agent验证)
python scripts/test_mvp.py
```

## 开发计划

### 第一阶段: MVP验证 (第1-4周)
- ✅ 项目初始化和环境配置
- ✅ 实现项目概况Agent
- ✅ 实现Word文档生成服务
- ✅ 端到端测试验证

### 第二阶段: 扩展Agent (第5-10周)
- 实现8个专业Agent
- 实现多Agent协作机制
- 完善数据服务

### 第三阶段: 系统优化 (第11-14周)
- 提示词优化
- 报告质量提升
- 性能优化

### 第四阶段: Web上线 (第15-16周)
- Web界面开发
- 系统部署上线

## Agent架构

系统包含8个专业Agent:

1. **项目概况Agent** - 负责第1章内容生成
2. **选址分析Agent** - 负责第2章内容生成
3. **合规审查Agent** - 负责第3章内容生成
4. **合理性分析Agent** - 负责第4章内容生成
5. **节地分析Agent** - 负责第5章内容生成
6. **数据获取Agent** - 负责数据获取和处理
7. **图表生成Agent** - 负责图表制作
8. **质量审核Agent** - 负责质量检查

## AutoGen学习资源

- [AutoGen GitHub](https://github.com/microsoft/autogen)
- [官方文档](https://microsoft.github.io/autogen/)
- [快速开始](https://microsoft.github.io/autogen/docs/Getting-Started)

## 贡献指南

欢迎提交Issue和Pull Request!

## 许可证

MIT License

## 联系方式

- 项目负责人: AI开发团队
- 创建日期: 2025-02-26
- 技术栈: Python + FastAPI + AutoGen + python-docx
