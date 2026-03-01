#!/usr/bin/env python3
"""
规划选址论证报告生成系统 - 统一CLI入口

命令:
  xuanzhi kb init          初始化知识库
  xuanzhi kb add <path>    添加文档到知识库
  xuanzhi kb query <text>  检索知识库
  xuanzhi kb stats         显示知识库统计
  xuanzhi generate <excel> 从Excel生成报告

使用示例:
    # 知识库管理
    python main.py kb init
    python main.py kb add data/knowledge_base/
    python main.py kb query "城乡规划要求"
    python main.py kb stats

    # 报告生成
    python main.py generate templates/excel_templates/项目数据模板.xlsx
    python main.py generate 项目数据.xlsx -o output/报告.docx
"""

import sys
import os
import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich import print as rprint

# 加载环境变量
from dotenv import load_dotenv
load_dotenv(override=True)

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入核心模块
from src.rag import Retriever, get_retriever
from src.core.autogen_config import get_model_client, get_model_info
from src.services.autogen_orchestrator_v2 import AutoGenOrchestratorV2
from src.services.excel_parser import ExcelParser
from src.services.document_service import DocumentService
from src.utils.logger import setup_logger


# ============================================================================
# 辅助函数
# ============================================================================

def parse_chapters(chapters_str: Optional[str]) -> Optional[list]:
    """
    解析章节选择参数
    
    支持格式:
    - '1,2,3' - 指定章节
    - '2-4' - 范围
    - '1,3-5' - 混合
    
    Args:
        chapters_str: 章节字符串
        
    Returns:
        章节列表，如 ['1', '2', '3']，None表示全部章节
    """
    if not chapters_str:
        return None
    
    result = set()
    parts = chapters_str.split(',')
    
    for part in parts:
        part = part.strip()
        if '-' in part:
            # 范围格式: 2-4
            try:
                start, end = part.split('-')
                start, end = int(start.strip()), int(end.strip())
                for i in range(start, end + 1):
                    if 1 <= i <= 6:
                        result.add(str(i))
            except ValueError:
                console.print(f"[yellow]⚠️ 无法解析章节范围: {part}[/yellow]")
        else:
            # 单个章节
            try:
                num = int(part)
                if 1 <= num <= 6:
                    result.add(str(num))
            except ValueError:
                console.print(f"[yellow]⚠️ 无效章节号: {part}[/yellow]")
    
    if not result:
        return None
    
    return sorted(result, key=int)
app = typer.Typer(
    name="xuanzhi",
    help="规划选址论证报告AI智能体协作系统",
    add_completion=False,
)

# 知识库子命令
kb_app = typer.Typer(
    name="kb",
    help="RAG知识库管理",
)
app.add_typer(kb_app, name="kb")

# Rich控制台
console = Console()


# ============================================================================
# 知识库命令
# ============================================================================

@kb_app.command("init")
def kb_init(
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


@kb_app.command("add")
def kb_add(
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
            count = retriever.ingest_file(str(input_path))
            progress.update(task, description=f"处理完成: {input_path.name}")
            console.print(f"\n[green]✅ 添加成功: {input_path.name}[/green]")
            console.print(f"  添加块数: {count}")
        else:
            results = retriever.ingest_directory(
                str(input_path),
                recursive=recursive,
            )
            progress.update(task, description="目录处理完成")
            
            total = sum(results.values())
            console.print(f"\n[green]✅ 目录处理完成[/green]")
            console.print(f"  处理文件数: {len(results)}")
            console.print(f"  添加块总数: {total}")
            
            if results:
                table = Table(title="文件处理详情")
                table.add_column("文件", style="cyan")
                table.add_column("块数", style="green", justify="right")
                
                for file_path, count in sorted(results.items()):
                    table.add_row(Path(file_path).name, str(count))
                
                console.print(table)


@kb_app.command("query")
def kb_query(
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
):
    """检索知识库"""
    retriever = get_retriever(collection_name=collection)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("正在检索...", total=None)
        
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


@kb_app.command("stats")
def kb_stats(
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


@kb_app.command("clear")
def kb_clear(
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


# ============================================================================
# 报告生成命令
# ============================================================================

@app.command()
def generate(
    excel_path: str = typer.Argument(
        ...,
        help="Excel数据文件路径"
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output", "-o",
        help="输出Word文档路径"
    ),
    chapters: Optional[str] = typer.Option(
        None,
        "--chapters", "-C",
        help="指定生成的章节，逗号分隔，如 '1,2,3' 或 '2-4'。默认生成全部6章"
    ),
    use_knowledge: bool = typer.Option(
        True,
        "--use-knowledge/--no-knowledge",
        help="是否使用知识库增强"
    ),
    collection: str = typer.Option(
        "xuanzhi_knowledge",
        "--collection", "-c",
        help="知识库集合名称"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="显示详细输出"
    ),
):
    """
    从Excel生成规划选址论证报告
    
    示例:
        python main.py generate 项目数据.xlsx
        python main.py generate 项目数据.xlsx -o output/报告.docx
        python main.py generate 项目数据.xlsx --no-knowledge
    """
    # 设置日志
    if verbose:
        setup_logger()
    
    # 检查文件存在
    if not os.path.exists(excel_path):
        console.print(f"[red]❌ Excel文件不存在: {excel_path}[/red]")
        raise typer.Exit(1)
    
    # 显示配置信息
    console.print(Panel.fit(
        "[bold blue]规划选址论证报告生成系统[/bold blue]",
        subtitle="AI智能体协作",
    ))
    
    model_info = get_model_info()
    console.print(f"\n[cyan]LLM配置:[/cyan]")
    console.print(f"  提供商: {model_info['provider']}")
    console.print(f"  模型: {model_info['model']}")
    
    if use_knowledge:
        retriever = get_retriever(collection_name=collection)
        kb_count = retriever.count()
        console.print(f"\n[cyan]知识库状态:[/cyan]")
        console.print(f"  集合: {collection}")
        console.print(f"  文档数: {kb_count}")
    
    # 执行生成流程
    console.print(f"\n[cyan]Excel文件:[/cyan] {excel_path}")
    
    try:
        # 步骤1: 解析Excel
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]步骤1/3: 解析Excel数据...", total=None)
            
            parser = ExcelParser(excel_path)
            project_data = parser.parse_project_overview()
            parser.close()
            
            progress.update(task, description="[green]✓ Excel解析完成[/green]")
        
        console.print(f"  项目名称: [bold]{project_data.项目名称}[/bold]")
        console.print(f"  建设单位: {project_data.建设单位}")
        
        # 步骤2: 调用编排器生成各章节（并行优化）
        console.print(f"\n[cyan]步骤2/3: 调用AI智能体生成报告章节（并行执行）[/cyan]")
        
        model_client = get_model_client()
        orchestrator = AutoGenOrchestratorV2(model_client=model_client)
        
        # 设置知识库（如果需要）
        if use_knowledge:
            retriever = get_retriever(collection_name=collection)
            orchestrator.set_retriever(retriever)
        
        # 解析章节选择
        selected_chapters = parse_chapters(chapters)
        if selected_chapters:
            console.print(f"  [cyan]生成章节: {', '.join(selected_chapters)}[/cyan]")
        else:
            console.print(f"  [cyan]生成章节: 全部6章[/cyan]")
        
        # 执行工作流（不生成Word文档，只获取chapters）
        result = orchestrator._run_async(
            orchestrator.execute_workflow(excel_path, enable_progress=False, selected_chapters=selected_chapters)
        )
        
        if not result["success"]:
            console.print(f"\n[red]❌ 章节生成失败[/red]")
            raise RuntimeError("工作流执行失败")
        
        chapters = result["chapters"]
        
        # 获取性能指标
        
        # 调试：打印第一章完整内容
        if "1" in chapters:
            console.print(f"\n[yellow]=== 第1章完整内容 ===[/yellow]")
            console.print(chapters["1"])
            console.print(f"\n[yellow]=== 内容结束 ===[/yellow]\n")
        
        # 获取性能指标
        
        
        # 获取性能指标
        if orchestrator.get_metrics():
            metrics = orchestrator.get_metrics()
            console.print(f"\n[bold]性能指标:[/bold]")
            console.print(f"  总耗时: {metrics.get('total_duration', 0):.2f}秒")
            console.print(f"  完成Agent: {metrics.get('completed', 0)}/{metrics.get('total_agents', 0)}")
            console.print(f"  重试次数: {metrics.get('total_retries', 0)}")
            console.print(f"  成功率: {metrics.get('success_rate', 0):.1%}")
            metrics = orchestrator.get_metrics()
            console.print(f"\n[bold]性能指标:[/bold]")
            console.print(f"  总耗时: {metrics.get('total_duration', 0):.2f}秒")
            console.print(f"  完成Agent: {metrics.get('completed', 0)}/{metrics.get('total_agents', 0)}")
            console.print(f"  重试次数: {metrics.get('total_retries', 0)}")
            console.print(f"  成功率: {metrics.get('success_rate', 0):.1%}")
        # 显示章节生成结果
        chapter_names = {
            "1": "项目概况",
            "2": "选址可行性分析",
            "3": "合法合规性分析",
            "4": "选址合理性分析",
            "5": "节约集约用地分析",
            "6": "结论与建议"
        }
        
        console.print("\n[bold]章节生成结果[/bold]\n")
        table = Table(title="章节生成结果")
        table.add_column("章节", style="cyan")
        table.add_column("状态", style="green")
        table.add_column("字数", justify="right")
        
        total_chars = 0
        for num, name in chapter_names.items():
            content = chapters.get(num, "")
            chars = len(content)
            total_chars += chars
            status = "✓" if chars > 100 else "✗"
            table.add_row(f"第{num}章 {name}", status, f"{chars}")
        
        console.print(table)
        console.print(f"\n[bold]总字数: {total_chars} 字符[/bold]")
        
        # 步骤3: 生成Word文档
        console.print(f"\n[cyan]步骤3/3: 生成Word文档[/cyan]")
        
        # 确定输出路径
        if output is None:
            output_dir = os.path.join(os.path.dirname(__file__), "output", "reports")
            os.makedirs(output_dir, exist_ok=True)
            output = os.path.join(output_dir, f"{project_data.项目名称}_规划选址论证报告.docx")
        
        doc_service = DocumentService()
        report_path = doc_service.generate_report(
            project_data=project_data.to_dict(),
            chapters=chapters,
            output_path=output
        )
        
        # 完成
        file_size = os.path.getsize(report_path)
        console.print(f"\n[bold green]✅ 报告生成成功！[/bold green]")
        console.print(f"  路径: {report_path}")
        console.print(f"  大小: {file_size / 1024:.2f} KB")
        
    except Exception as e:
        console.print(f"\n[red]❌ 生成失败: {str(e)}[/red]")
        if verbose:
            import traceback
            traceback.print_exc()
        raise typer.Exit(1)


# ============================================================================
# 状态命令
# ============================================================================

@app.command()
def status():
    """显示系统状态"""
    console.print(Panel.fit(
        "[bold blue]规划选址论证报告生成系统[/bold blue]\n"
        "AI智能体协作系统状态检查",
    ))
    
    # 检查LLM配置
    console.print("\n[bold cyan]1. LLM配置[/bold cyan]")
    try:
        model_info = get_model_info()
        console.print(f"  [green]✓[/green] 提供商: {model_info['provider']}")
        console.print(f"  [green]✓[/green] 模型: {model_info['model']}")
        console.print(f"  [green]✓[/green] Base URL: {model_info['base_url']}")
    except Exception as e:
        console.print(f"  [red]✗[/red] 配置错误: {str(e)}")
    
    # 检查知识库
    console.print("\n[bold cyan]2. 知识库状态[/bold cyan]")
    try:
        retriever = get_retriever()
        stats = retriever.get_stats()
        console.print(f"  [green]✓[/green] 集合: {stats['collection_name']}")
        console.print(f"  [green]✓[/green] 文档数: {stats['document_count']}")
        console.print(f"  [green]✓[/green] 持久化目录: {stats['persist_dir']}")
    except Exception as e:
        console.print(f"  [red]✗[/red] 知识库错误: {str(e)}")
    
    # 检查模板
    console.print("\n[bold cyan]3. 模板文件[/bold cyan]")
    template_dir = Path(__file__).parent / "templates"
    
    prompts_dir = template_dir / "prompts"
    if prompts_dir.exists():
        prompt_files = list(prompts_dir.glob("*.md"))
        console.print(f"  [green]✓[/green] 提示词模板: {len(prompt_files)} 个")
    else:
        console.print(f"  [red]✗[/red] 提示词模板目录不存在")
    
    excel_template = template_dir / "excel_templates" / "项目数据模板.xlsx"
    if excel_template.exists():
        console.print(f"  [green]✓[/green] Excel模板: {excel_template.name}")
    else:
        console.print(f"  [yellow]?[/yellow] Excel模板: 未找到")
    
    word_template = template_dir / "word_templates" / "标准模板.docx"
    if word_template.exists():
        console.print(f"  [green]✓[/green] Word模板: {word_template.name}")
    else:
        console.print(f"  [yellow]?[/yellow] Word模板: 未找到")
    
    # 检查输出目录
    console.print("\n[bold cyan]4. 输出目录[/bold cyan]")
    output_dir = Path(__file__).parent / "output"
    if output_dir.exists():
        reports_dir = output_dir / "reports"
        if reports_dir.exists():
            reports = list(reports_dir.glob("*.docx"))
            console.print(f"  [green]✓[/green] 已生成报告: {len(reports)} 个")
        else:
            console.print(f"  [green]✓[/green] 输出目录存在")
    else:
        console.print(f"  [yellow]?[/yellow] 输出目录不存在，将在首次运行时创建")


# ============================================================================
# 版本命令
# ============================================================================

@app.command()
def version():
    """显示版本信息"""
    console.print(Panel.fit(
        "[bold blue]规划选址论证报告生成系统[/bold blue]\n\n"
        "版本: 1.0.0\n"
        "框架: AutoGen-agentchat 0.7.x\n"
        "LLM: 阿里云百炼 Qwen / OpenAI GPT\n"
        "向量数据库: ChromaDB\n"
        "Python: 3.10+",
    ))


# ============================================================================
# 快速开始命令
# ============================================================================

@app.command()
def quickstart():
    """快速开始指南"""
    console.print(Panel.fit(
        "[bold blue]快速开始指南[/bold blue]",
    ))
    
    console.print("""
[bold cyan]1. 配置API密钥[/bold cyan]
   编辑 .env 文件，设置:
   DASHSCOPE_API_KEY=sk-xxx
   MODEL_NAME=qwen-plus

[bold cyan]2. 初始化知识库[/bold cyan]
   python main.py kb init
   python main.py kb add data/knowledge_base/

[bold cyan]3. 准备Excel数据[/bold cyan]
   使用 templates/excel_templates/项目数据模板.xlsx

[bold cyan]4. 生成报告[/bold cyan]
   python main.py generate 项目数据.xlsx

[bold cyan]5. 查看帮助[/bold cyan]
   python main.py --help
   python main.py generate --help
   python main.py kb --help
""")


if __name__ == "__main__":
    app()