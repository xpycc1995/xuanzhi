#!/usr/bin/env python3
"""
知识库CLI命令 - RAG知识库管理工具

命令:
- kb init     : 初始化知识库
- kb add      : 添加文档到知识库
- kb query    : 检索知识库
- kb list     : 列出知识库文档
- kb stats    : 显示知识库统计
- kb clear    : 清空知识库

使用示例:
    python scripts/kb.py init
    python scripts/kb.py add data/knowledge_base/
    python scripts/kb.py query "城乡规划要求"
    python scripts/kb.py list --limit 10
    python scripts/kb.py stats
    python scripts/kb.py clear
"""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag import Retriever, get_retriever

app = typer.Typer(
    name="kb",
    help="RAG知识库管理工具",
    add_completion=False,
)
console = Console()


@app.command()
def init(
    collection: str = typer.Option(
        "xuanzhi_knowledge",
        "--collection", "-c",
        help="知识库集合名称"
    ),
    persist_dir: Optional[str] = typer.Option(
        None,
        "--persist-dir", "-p",
        help="向量数据库持久化目录"
    ),
):
    """初始化知识库"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("正在初始化知识库...", total=None)
        
        retriever = Retriever(
            persist_dir=persist_dir,
            collection_name=collection,
        )
        
        progress.update(task, description="初始化完成")
    
    stats = retriever.get_stats()
    console.print("\n[bold green]✅ 知识库初始化成功[/bold green]")
    console.print(f"  集合名称: {stats['collection_name']}")
    console.print(f"  持久化目录: {stats['persist_dir']}")
    console.print(f"  当前文档数: {stats['document_count']}")
    console.print(f"  Embedding模型: {stats['embedding_model']}")


@app.command()
def add(
    path: str = typer.Argument(
        ...,
        help="文件或目录路径"
    ),
    recursive: bool = typer.Option(
        True,
        "--recursive/--no-recursive", "-r/-R",
        help="是否递归处理子目录"
    ),
    collection: str = typer.Option(
        "xuanzhi_knowledge",
        "--collection", "-c",
        help="知识库集合名称"
    ),
):
    """添加文档到知识库"""
    retriever = get_retriever(collection_name=collection)
    input_path = Path(path)
    
    if not input_path.exists():
        console.print(f"[red]❌ 路径不存在: {path}[/red]")
        raise typer.Exit(1)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("正在添加文档...", total=None)
        
        if input_path.is_file():
            # 单文件
            count = retriever.ingest_file(str(input_path))
            progress.update(task, description=f"处理完成: {input_path.name}")
            console.print(f"\n[green]✅ 添加成功: {input_path.name}[/green]")
            console.print(f"  添加块数: {count}")
        else:
            # 目录
            results = retriever.ingest_directory(
                str(input_path),
                recursive=recursive,
            )
            progress.update(task, description="目录处理完成")
            
            total = sum(results.values())
            console.print(f"\n[green]✅ 目录处理完成[/green]")
            console.print(f"  处理文件数: {len(results)}")
            console.print(f"  添加块总数: {total}")
            
            # 显示文件详情
            if results:
                table = Table(title="文件处理详情")
                table.add_column("文件", style="cyan")
                table.add_column("块数", style="green", justify="right")
                
                for file_path, count in sorted(results.items()):
                    table.add_row(Path(file_path).name, str(count))
                
                console.print(table)


@app.command()
def query(
    text: str = typer.Argument(
        ...,
        help="查询文本"
    ),
    top_k: int = typer.Option(
        5,
        "--top-k", "-k",
        help="返回结果数量"
    ),
    threshold: float = typer.Option(
        0.7,
        "--threshold", "-t",
        help="相似度阈值 (0-1)"
    ),
    collection: str = typer.Option(
        "xuanzhi_knowledge",
        "--collection", "-c",
        help="知识库集合名称"
    ),
    context: bool = typer.Option(
        False,
        "--context",
        help="输出为LLM上下文格式"
    ),
):
    """检索知识库"""
    retriever = get_retriever(collection_name=collection)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("正在检索...", total=None)
        
        if context:
            # LLM上下文格式
            result_text = retriever.search_with_context(
                query=text,
                n_results=top_k,
                threshold=threshold,
            )
            progress.update(task, description="检索完成")
            console.print(f"\n{result_text}")
        else:
            results = retriever.search(
                query=text,
                n_results=top_k,
                threshold=threshold,
            )
            progress.update(task, description="检索完成")
            
            if not results:
                console.print("\n[yellow]⚠️ 未找到匹配结果[/yellow]")
                console.print(f"  查询: {text}")
                console.print(f"  阈值: {threshold}")
                return
            
            console.print(f"\n[bold green]找到 {len(results)} 个结果[/bold green]")
            console.print(f"  查询: {text}")
            console.print(f"  阈值: {threshold}\n")
            
            for i, result in enumerate(results, 1):
                console.print(f"[bold cyan]结果 {i}[/bold cyan] (相似度: {result.score:.3f})")
                console.print(f"  内容: {result.content[:200]}{'...' if len(result.content) > 200 else ''}")
                if result.metadata:
                    source = result.metadata.get('source', 'unknown')
                    console.print(f"  来源: {source}")
                console.print()


@app.command()
def list(
    limit: int = typer.Option(
        20,
        "--limit", "-l",
        help="返回数量限制"
    ),
    offset: int = typer.Option(
        0,
        "--offset", "-o",
        help="偏移量"
    ),
    collection: str = typer.Option(
        "xuanzhi_knowledge",
        "--collection", "-c",
        help="知识库集合名称"
    ),
):
    """列出知识库文档"""
    retriever = get_retriever(collection_name=collection)
    
    documents = retriever.list_documents(limit=limit, offset=offset)
    total = retriever.count()
    
    if not documents:
        console.print("[yellow]知识库为空[/yellow]")
        return
    
    console.print(f"\n[bold]知识库文档 (共 {total} 个, 显示 {len(documents)} 个)[/bold]\n")
    
    table = Table()
    table.add_column("ID", style="dim")
    table.add_column("内容预览", style="cyan")
    table.add_column("来源", style="green")
    
    for doc in documents:
        content = doc.get("content", "")[:60] + "..."
        source = doc.get("metadata", {}).get("source", "unknown")
        table.add_row(doc.get("id", ""), content, source)
    
    console.print(table)


@app.command()
def stats(
    collection: str = typer.Option(
        "xuanzhi_knowledge",
        "--collection", "-c",
        help="知识库集合名称"
    ),
):
    """显示知识库统计"""
    retriever = get_retriever(collection_name=collection)
    info = retriever.get_stats()
    
    console.print("\n[bold]知识库统计信息[/bold]\n")
    
    table = Table(show_header=False)
    table.add_column("属性", style="cyan")
    table.add_column("值", style="green")
    
    table.add_row("集合名称", info["collection_name"])
    table.add_row("持久化目录", info["persist_dir"])
    table.add_row("文档数量", str(info["document_count"]))
    table.add_row("Embedding模型", info["embedding_model"])
    table.add_row("向量维度", str(info["embedding_dimensions"]))
    table.add_row("分块大小", str(info["chunk_size"]))
    table.add_row("重叠大小", str(info["overlap"]))
    
    console.print(table)


@app.command()
def clear(
    collection: str = typer.Option(
        "xuanzhi_knowledge",
        "--collection", "-c",
        help="知识库集合名称"
    ),
    force: bool = typer.Option(
        False,
        "--force", "-f",
        help="强制清空，不询问确认"
    ),
):
    """清空知识库"""
    retriever = get_retriever(collection_name=collection)
    count = retriever.count()
    
    if count == 0:
        console.print("[yellow]知识库已经为空[/yellow]")
        return
    
    if not force:
        confirm = typer.confirm(
            f"确定要清空知识库吗？将删除 {count} 个文档",
            default=False,
        )
        if not confirm:
            console.print("[yellow]已取消[/yellow]")
            raise typer.Exit(0)
    
    deleted = retriever.clear()
    console.print(f"[green]✅ 已清空知识库，删除 {deleted} 个文档[/green]")


if __name__ == "__main__":
    app()