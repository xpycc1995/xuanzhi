"""
Excel智能体工具模块

提供Excel辅助填写的核心工具
"""

from .excel_tools import (
    read_excel,
    read_excel_all_sheets,
    search_knowledge_base,
    search_knowledge_base_for_field,
    write_excel,
    write_excel_batch,
    get_excel_tools,
    TOOL_DESCRIPTIONS,
)

__all__ = [
    "read_excel",
    "read_excel_all_sheets",
    "search_knowledge_base",
    "search_knowledge_base_for_field",
    "write_excel",
    "write_excel_batch",
    "get_excel_tools",
    "TOOL_DESCRIPTIONS",
]

from .knowledge_tools import (
    search_knowledge_base as kb_search,
    search_regulations,
    search_cases,
    search_technical_standards,
    get_knowledge_base_stats,
    KNOWLEDGE_TOOLS,
)

__all__.extend([
    "kb_search",
    "search_regulations",
    "search_cases",
    "search_technical_standards",
    "get_knowledge_base_stats",
    "KNOWLEDGE_TOOLS",
])