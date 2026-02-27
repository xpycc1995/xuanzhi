# Excel辅助填写 + RAG知识库系统 - 工作计划摘要

## TL;DR

实现基于ChromaDB和百炼Embedding的本地RAG知识库,以及ExcelAssistantAgent智能体,自动填充Excel模板,CLI命令行接口,TDD测试驱动。

**预估工作量**: Medium (5个开发Wave, 18个Tasks + 4个Final验证)

---

## 开发进度

### Wave 1: 环境验证 ✅ 完成 (2026-02-27)
| 任务 | 状态 | 结果 |
|------|------|------|
| Task 1: 技术假设验证 | ✅ | 百炼Embedding API成功返回1024维向量 |
| Task 2: 安装依赖 | ✅ | chromadb 1.5.1, pypdf 6.7.3, pytest-cov 7.0.0 |
| Task 3: pytest配置 | ✅ | pytest.ini, conftest.py, fixtures配置完成 |

### Wave 2: 知识库核心 ✅ 完成 (2026-02-27)
| 任务 | 状态 | 文件 |
|------|------|------|
| Task 4: 文档处理器 | ✅ | `src/rag/document_processor.py` |
| Task 5: 文本分块器 | ✅ | `src/rag/text_chunker.py` |
| Task 6: 知识库核心 | ✅ | `src/rag/knowledge_base.py` |
| Task 7: 百炼Embedding | ✅ | `src/rag/embedding.py` |
| Task 8: 单元测试 | ✅ | `tests/test_rag/test_rag_system.py` (28个测试通过) |

### Wave 3: 检索服务 ⏳ 待开发
- **Task 9**: 实现检索服务 (Retriever, Top-K返回, 阈值过滤)
- **Task 10**: 实现CLI知识库命令 (kb-init, kb-add, kb-query, kb-list)
- **Task 11**: 检索功能测试

### Wave 4: Excel智能体 ⏳ 待开发
- **Task 12**: 实现FunctionTools (read_excel, search_knowledge_base, write_excel)
- **Task 13**: 实现ExcelAssistantAgent (3个Tools, 完全自动填充)
- **Task 14**: 实现fill-excel CLI命令
- **Task 15**: Excel智能体测试

### Wave 5: 6章Agent集成 ⏳ 待开发
- **Task 16**: 扩展AutoGenOrchestrator支持知识库
- **Task 17**: 修改6章Agent使用知识库 (补充数据、案例参考)
- **Task 18**: 集成测试

### Wave FINAL: 文档和验证 ⏳ 待开发
- **F1**: 更新AGENTS.md和README
- **F2**: 生成使用示例和文档
- **F3**: 端到端QA验证
- **F4**: 计划合规审计 (oracle)

---

## 已完成的文件结构

```
src/rag/
├── __init__.py              # 模块导出
├── document_processor.py    # 多格式文档解析 (PDF/Word/MD/TXT)
├── text_chunker.py          # 重叠滑动窗口分块 (512字符, 128重叠)
├── knowledge_base.py        # ChromaDB封装 (向量存储/检索)
└── embedding.py             # 百炼Embedding API (text-embedding-v3, 1024维)

tests/test_rag/
└── test_rag_system.py       # 28个单元测试

data/
├── knowledge_base/          # 知识库文档存储
└── chroma_db/               # ChromaDB向量数据库
```

---

## 测试覆盖率

```
src/rag/knowledge_base.py     80% ✅
src/rag/text_chunker.py       82% ✅
src/rag/document_processor.py 40% (PDF/Word解析未覆盖)
src/rag/embedding.py          40% (API调用使用mock)
─────────────────────────────────────────
总计: 28个测试通过
```

---

## 关键决策汇总

### 用户已确认
- ✅ **辅助填写方式**: 完全自动填充 (用户不干预)
- ✅ **无匹配行为**: 警告+继续 (记录警告,提示手动填写)
- ✅ **文档格式支持**: 全部格式 (PDF/Word/Markdown/TXT)
- ✅ **检索精度**: Top-5, 阈值0.7
- ✅ **测试策略**: TDD (测试驱动开发)
- ✅ **ChromaDB部署**: 本地文件存储 (data/chroma_db/)
- ✅ **知识库更新**: 混合模式 (全量+增量)

### Metis识别的Guardrails
- ❌ Web界面 (明确延后)
- ❌ 知识库版本控制
- ❌ 多用户权限系统
- ❌ 编造虚假数据
- ❌ 自动修改Excel模板格式

---

## 关键依赖路径

```
T2 → T4 → T6 → T9 → T12 → T13 → T16 → T17 → T18 → F3 → F4
```

**并行加速比**: ~60% faster than sequential

---

## 验收标准

```bash
# 1. 知识库初始化 ✅
python -c "from src.rag import KnowledgeBase; kb = KnowledgeBase(); print(f'文档数: {kb.count()}')"

# 2. 文档索引 (待实现)
python scripts/test_rag.py --ingest test_docs/ --assert-count 5

# 3. 检索测试 (待实现)
python scripts/test_rag.py --search "项目选址原则" --assert-top-k 5

# 4. Excel智能体 (待实现)
python scripts/test_excel_assistant.py --input test.xlsx --assert-fields-filled 80

# 5. CLI命令 (待实现)
fill-excel test.xlsx --output filled.xlsx --top-k 5 --threshold 0.7

# 6. 单元测试 ✅
pytest tests/test_rag/ -v --cov=src/rag
```

---

## 已验证的验收命令

```bash
# Wave 1-2 验收
source /Users/yc/miniconda/bin/activate xuanzhi
pytest tests/test_rag/test_rag_system.py -v --cov=src/rag

# 输出:
# 28 passed, 3 deselected
# src/rag/knowledge_base.py   80%
# src/rag/text_chunker.py     82%
```

---

## 技术栈确认

| 组件 | 技术 | 版本 |
|------|------|------|
| 向量数据库 | ChromaDB | 1.5.1 |
| Embedding | 百炼 text-embedding-v3 | 1024维 |
| PDF解析 | pypdf | 6.7.3 |
| Word解析 | python-docx | 已安装 |
| 测试框架 | pytest + pytest-cov | 8.3.4 + 7.0.0 |

---

## 详细任务列表

由于token限制,详细任务描述见 `.sisyphus/drafts/后续开发方案.md` 中的"开发里程碑"部分。

如需要完整的详细工作计划(包含每个任务的QA场景、Agent Profile、Parallelization信息),请告知,我将生成多个文件分批提供。
