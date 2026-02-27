"""
知识库检索工具 - 供Agent使用的知识检索函数

这些工具可以被AutoGen AssistantAgent直接使用，用于从知识库中检索相关内容。

工具列表:
- search_knowledge_base: 通用知识库检索
- search_regulations: 检索法规标准
- search_cases: 检索案例参考
- search_technical_standards: 检索技术标准
"""

import json
from typing import List, Dict, Any, Optional

# 延迟导入，避免循环依赖
_retriever = None


def _get_retriever():
    """获取Retriever实例（延迟初始化）"""
    global _retriever
    if _retriever is None:
        from src.rag.retriever import get_retriever
        _retriever = get_retriever()
    return _retriever


def search_knowledge_base(
    query: str,
    n_results: int = 5,
    threshold: float = 0.7,
) -> str:
    """
    从知识库中检索相关内容
    
    这是通用的知识检索工具，用于从本地知识库中检索与查询相关的内容。
    知识库包含法规标准、技术规范、案例参考等资料。
    
    Args:
        query: 检索查询文本，描述需要查找的内容
        n_results: 返回结果数量，默认5条
        threshold: 相似度阈值 (0-1)，默认0.7，越高越严格
    
    Returns:
        JSON格式的检索结果，包含以下字段:
        - success: 是否成功
        - results: 检索结果列表，每项包含 content, score, source
        - count: 结果数量
        - message: 状态消息
    
    示例:
        >>> search_knowledge_base("城乡规划法 选址要求")
        >>> search_knowledge_base("建设用地节约集约利用标准", n_results=3)
    """
    try:
        retriever = _get_retriever()
        results = retriever.search(
            query=query,
            n_results=n_results,
            threshold=threshold,
        )
        
        if not results:
            return json.dumps({
                "success": True,
                "results": [],
                "count": 0,
                "message": f"未找到与 '{query}' 相关的内容 (阈值: {threshold})"
            }, ensure_ascii=False, indent=2)
        
        # 格式化结果
        formatted_results = []
        for r in results:
            formatted_results.append({
                "content": r.content,
                "score": round(r.score, 3),
                "source": r.metadata.get("source", "未知"),
            })
        
        return json.dumps({
            "success": True,
            "results": formatted_results,
            "count": len(formatted_results),
            "message": f"找到 {len(formatted_results)} 条相关内容"
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "results": [],
            "count": 0,
            "message": f"检索失败: {str(e)}"
        }, ensure_ascii=False, indent=2)


def search_regulations(
    query: str,
    n_results: int = 3,
) -> str:
    """
    检索法规标准相关内容
    
    专门用于检索法律法规、政策文件、规划标准等内容。
    适用于需要引用法规依据的场景。
    
    Args:
        query: 法规相关查询，如"城乡规划法"、"土地管理法"等
        n_results: 返回结果数量，默认3条
    
    Returns:
        JSON格式的检索结果，重点突出法规来源
    
    示例:
        >>> search_regulations("建设项目选址 规划许可")
        >>> search_regulations("永久基本农田 保护要求")
    """
    # 增强查询，添加法规相关关键词
    enhanced_query = f"法规 标准 {query}"
    
    try:
        retriever = _get_retriever()
        results = retriever.search(
            query=enhanced_query,
            n_results=n_results,
            threshold=0.65,  # 稍低的阈值，确保召回
        )
        
        if not results:
            return json.dumps({
                "success": True,
                "results": [],
                "count": 0,
                "message": f"未找到与 '{query}' 相关的法规标准"
            }, ensure_ascii=False, indent=2)
        
        # 格式化结果，突出法规来源
        formatted_results = []
        for r in results:
            formatted_results.append({
                "content": r.content,
                "score": round(r.score, 3),
                "source": r.metadata.get("source", "未知"),
                "document": r.metadata.get("original_filename", "未知文档"),
            })
        
        return json.dumps({
            "success": True,
            "results": formatted_results,
            "count": len(formatted_results),
            "message": f"找到 {len(formatted_results)} 条法规相关内容"
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "results": [],
            "count": 0,
            "message": f"法规检索失败: {str(e)}"
        }, ensure_ascii=False, indent=2)


def search_cases(
    query: str,
    n_results: int = 3,
) -> str:
    """
    检索案例参考
    
    用于检索类似项目的案例、经验做法、分析模式等内容。
    适用于需要参考同类项目做法的场景。
    
    Args:
        query: 案例相关查询，如"污水处理厂选址"、"基础设施项目"等
        n_results: 返回结果数量，默认3条
    
    Returns:
        JSON格式的检索结果，包含案例参考内容
    
    示例:
        >>> search_cases("污水处理厂 选址论证")
        >>> search_cases("基础设施 节约集约用地")
    """
    # 增强查询，添加案例相关关键词
    enhanced_query = f"案例 参考 经验 {query}"
    
    try:
        retriever = _get_retriever()
        results = retriever.search(
            query=enhanced_query,
            n_results=n_results,
            threshold=0.6,  # 较低的阈值，扩大召回范围
        )
        
        if not results:
            return json.dumps({
                "success": True,
                "results": [],
                "count": 0,
                "message": f"未找到与 '{query}' 相关的案例参考"
            }, ensure_ascii=False, indent=2)
        
        # 格式化结果
        formatted_results = []
        for r in results:
            formatted_results.append({
                "content": r.content,
                "score": round(r.score, 3),
                "source": r.metadata.get("source", "未知"),
                "document": r.metadata.get("original_filename", "未知文档"),
            })
        
        return json.dumps({
            "success": True,
            "results": formatted_results,
            "count": len(formatted_results),
            "message": f"找到 {len(formatted_results)} 条案例参考"
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "results": [],
            "count": 0,
            "message": f"案例检索失败: {str(e)}"
        }, ensure_ascii=False, indent=2)


def search_technical_standards(
    query: str,
    n_results: int = 3,
) -> str:
    """
    检索技术标准规范
    
    用于检索技术标准、设计规范、技术参数等内容。
    适用于需要引用具体技术指标的场景。
    
    Args:
        query: 技术标准相关查询，如"用地指标"、"建筑密度"等
        n_results: 返回结果数量，默认3条
    
    Returns:
        JSON格式的检索结果，包含技术标准内容
    
    示例:
        >>> search_technical_standards("污水处理厂 用地指标")
        >>> search_technical_standards("容积率 标准")
    """
    # 增强查询，添加技术标准相关关键词
    enhanced_query = f"技术 标准 规范 指标 {query}"
    
    try:
        retriever = _get_retriever()
        results = retriever.search(
            query=enhanced_query,
            n_results=n_results,
            threshold=0.65,
        )
        
        if not results:
            return json.dumps({
                "success": True,
                "results": [],
                "count": 0,
                "message": f"未找到与 '{query}' 相关的技术标准"
            }, ensure_ascii=False, indent=2)
        
        # 格式化结果
        formatted_results = []
        for r in results:
            formatted_results.append({
                "content": r.content,
                "score": round(r.score, 3),
                "source": r.metadata.get("source", "未知"),
                "document": r.metadata.get("original_filename", "未知文档"),
            })
        
        return json.dumps({
            "success": True,
            "results": formatted_results,
            "count": len(formatted_results),
            "message": f"找到 {len(formatted_results)} 条技术标准"
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "results": [],
            "count": 0,
            "message": f"技术标准检索失败: {str(e)}"
        }, ensure_ascii=False, indent=2)


def get_knowledge_base_stats() -> str:
    """
    获取知识库统计信息
    
    返回知识库的基本统计信息，包括文档数量、分块参数等。
    
    Returns:
        JSON格式的统计信息
    """
    try:
        retriever = _get_retriever()
        stats = retriever.get_stats()
        
        return json.dumps({
            "success": True,
            "stats": stats,
            "message": "知识库统计信息"
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "stats": {},
            "message": f"获取统计信息失败: {str(e)}"
        }, ensure_ascii=False, indent=2)


# 工具列表，供Agent导入使用
KNOWLEDGE_TOOLS = [
    search_knowledge_base,
    search_regulations,
    search_cases,
    search_technical_standards,
    get_knowledge_base_stats,
]


if __name__ == "__main__":
    # 测试工具
    print("测试知识库检索工具...")
    
    # 测试统计
    print("\n1. 获取知识库统计信息:")
    print(get_knowledge_base_stats())
    
    # 测试检索
    print("\n2. 测试通用检索:")
    print(search_knowledge_base("城乡规划", n_results=2))
    
    print("\n3. 测试法规检索:")
    print(search_regulations("土地管理"))
    
    print("\n4. 测试案例检索:")
    print(search_cases("污水处理厂"))
    
    print("\n5. 测试技术标准检索:")
    print(search_technical_standards("用地指标"))