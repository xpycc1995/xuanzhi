"""
文本分块器 - 重叠滑动窗口分块
配置: 默认512字符块, 128字符重叠
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class TextChunk:
    """文本块数据结构"""
    content: str
    metadata: Dict[str, Any]
    chunk_id: int
    source: str
    start_char: int
    end_char: int


class TextChunker:
    """
    文本分块器
    
    使用重叠滑动窗口策略，确保上下文连续性
    默认配置:
    - chunk_size: 512字符
    - overlap: 128字符 (约25%重叠)
    """
    
    # 默认分块配置
    DEFAULT_CHUNK_SIZE = 512
    DEFAULT_OVERLAP = 128
    
    # 中文句子分隔符
    SENTENCE_DELIMITERS = ['。', '！', '？', '；', '\n\n', '\n']
    
    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        overlap: int = DEFAULT_OVERLAP,
    ):
        """
        初始化文本分块器
        
        Args:
            chunk_size: 每个文本块的字符数，默认512
            overlap: 相邻块之间的重叠字符数，默认128
            
        Raises:
            ValueError: 参数无效
        """
        if chunk_size <= 0:
            raise ValueError(f"chunk_size必须大于0，当前: {chunk_size}")
        if overlap < 0:
            raise ValueError(f"overlap不能为负数，当前: {overlap}")
        if overlap >= chunk_size:
            raise ValueError(f"overlap必须小于chunk_size: {overlap} >= {chunk_size}")
        
        self.chunk_size = chunk_size
        self.overlap = overlap
        
        logger.info(
            f"TextChunker初始化: chunk_size={chunk_size}, overlap={overlap}"
        )
    
    def chunk_text(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        source: str = "unknown",
    ) -> List[TextChunk]:
        """
        将文本分割成多个重叠块
        
        Args:
            text: 待分割的文本
            metadata: 文档元数据
            source: 文档来源标识
            
        Returns:
            TextChunk列表
        """
        if not text or not text.strip():
            return []
        
        if metadata is None:
            metadata = {}
        
        chunks = []
        text_length = len(text)
        
        # 如果文本长度小于chunk_size，直接返回一个块
        if text_length <= self.chunk_size:
            chunks.append(TextChunk(
                content=text.strip(),
                metadata={**metadata, "is_complete": True},
                chunk_id=0,
                source=source,
                start_char=0,
                end_char=text_length,
            ))
            return chunks
        
        # 滑动窗口分块
        start = 0
        chunk_id = 0
        
        while start < text_length:
            # 计算当前块的结束位置
            end = min(start + self.chunk_size, text_length)
            
            # 尝试在句子边界处分割
            if end < text_length:
                end = self._find_sentence_boundary(text, end)
            
            # 提取文本块
            chunk_content = text[start:end].strip()
            
            if chunk_content:
                chunks.append(TextChunk(
                    content=chunk_content,
                    metadata={**metadata},
                    chunk_id=chunk_id,
                    source=source,
                    start_char=start,
                    end_char=end,
                ))
                chunk_id += 1
            
            # 移动到下一个块的起始位置（考虑重叠）
            next_start = end - self.overlap
            
            # 确保前进
            if next_start <= start:
                next_start = start + self.chunk_size - self.overlap
            
            start = next_start
            
            # 防止无限循环
            if start >= text_length:
                break
        
        logger.info(
            f"文本分块完成: 原始长度={text_length}, 块数={len(chunks)}, "
            f"来源={source}"
        )
        
        return chunks
    
    def chunk_document(
        self,
        document: Any,  # Document类型，避免循环导入
    ) -> List[TextChunk]:
        """
        分块处理Document对象
        
        Args:
            document: Document对象（来自document_processor）
            
        Returns:
            TextChunk列表
        """
        return self.chunk_text(
            text=document.content,
            metadata=document.metadata,
            source=document.source,
        )
    
    def _find_sentence_boundary(self, text: str, position: int) -> int:
        """
        在指定位置附近查找句子边界
        
        Args:
            text: 完整文本
            position: 建议的分割位置
            
        Returns:
            调整后的分割位置
        """
        # 向后查找边界（最多查找100字符）
        look_ahead = 100
        search_start = position
        search_end = min(position + look_ahead, len(text))
        
        for i in range(search_start, search_end):
            if text[i] in self.SENTENCE_DELIMITERS:
                return i + 1
        
        # 向前查找边界
        look_back = min(position, 100)
        search_start = position - look_back
        search_end = position
        
        for i in range(search_end, search_start, -1):
            if text[i] in self.SENTENCE_DELIMITERS:
                return i + 1
        
        # 未找到边界，返回原位置
        return position
    
    def get_chunk_info(self, chunks: List[TextChunk]) -> Dict[str, Any]:
        """
        获取分块统计信息
        
        Args:
            chunks: TextChunk列表
            
        Returns:
            统计信息字典
        """
        if not chunks:
            return {
                "total_chunks": 0,
                "total_chars": 0,
                "avg_chunk_size": 0,
                "min_chunk_size": 0,
                "max_chunk_size": 0,
            }
        
        sizes = [len(chunk.content) for chunk in chunks]
        
        return {
            "total_chunks": len(chunks),
            "total_chars": sum(sizes),
            "avg_chunk_size": sum(sizes) // len(sizes),
            "min_chunk_size": min(sizes),
            "max_chunk_size": max(sizes),
        }


def get_sample_chunks() -> List[str]:
    """
    获取示例文本块（用于测试）
    
    Returns:
        示例文本块列表
    """
    return [
        "规划选址应当符合城乡规划要求，避开地质灾害易发区、洪涝灾害危险区、生态保护红线等禁止建设区域。",
        "项目建设用地应当节约集约用地，严格控制用地规模，提高土地利用效率。",
        "选址论证报告应当包括项目概况、选址分析、合规性分析、合理性分析、节地分析、结论与建议等章节。",
    ]


if __name__ == "__main__":
    # 简单测试
    chunker = TextChunker()
    
    test_text = """
    规划选址综合论证报告是对建设项目选址进行科学论证的重要文件。
    报告应当全面分析项目的选址依据、合规性、合理性等方面内容。
    通过系统的论证分析，确保项目选址的科学性和可行性。
    """ * 10  # 重复以测试分块
    
    chunks = chunker.chunk_text(test_text, source="test")
    info = chunker.get_chunk_info(chunks)
    
    print(f"分块数量: {info['total_chunks']}")
    print(f"平均块大小: {info['avg_chunk_size']}")