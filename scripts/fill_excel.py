#!/usr/bin/env python
"""
Excel辅助填写CLI命令

使用方法:
    python scripts/fill_excel.py analyze <file.xlsx>           # 分析Excel空白字段
    python scripts/fill_excel.py fill <file.xlsx>              # 自动填充Excel
    python scripts/fill_excel.py fill <file.xlsx> -o output.xlsx  # 输出到新文件
    python scripts/fill_excel.py query "项目名称"               # 检索知识库
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.excel_agent import create_excel_agent

app = typer.Typer(
    name="fill-excel",
    help="Excel辅助填写智能助手 - 自动填充项目数据模板"
)
console = Console()


@app.command()
def analyze(
    file_path: str = typer.Argument(..., help="Excel文件路径"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="显示详细信息")
):
    """
    分析Excel文件,统计空白字段
    
    示例:
        fill-excel analyze 项目数据.xlsx
        fill-excel analyze 项目数据.xlsx -v
    """
    async def _analyze():
        # 检查文件
        path = Path(file_path)
        if not path.exists():
            console.print(f"[red]错误: 文件不存在 {file_path}[/red]")
            raise typer.Exit(1)
        
        console.print(Panel(f"分析Excel文件: [bold]{path.name}[/bold]", style="blue"))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("正在分析...", total=None)
            
            # 创建Agent并分析
            agent = create_excel_agent()
            result = await agent.analyze_excel(file_path)
            
            progress.update(task, completed=True)
        
        if result.get("success"):
            console.print("\n[green]✓ 分析完成[/green]\n")
            
            # 显示分析结果
            analysis = result.get("analysis", "")
            console.print(analysis)
            
            if verbose:
                console.print(f"\n[dim]文件: {file_path}[/dim]")
        else:
            console.print(f"[red]分析失败: {result.get('error', '未知错误')}[/red]")
    
    asyncio.run(_analyze())


@app.command()
def fill(
    file_path: str = typer.Argument(..., help="Excel文件路径"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="输出文件路径"),
    threshold: float = typer.Option(0.7, "--threshold", "-t", help="检索阈值 (0-1)"),
    dry_run: bool = typer.Option(False, "--dry-run", "-d", help="仅模拟,不实际写入"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="显示详细信息")
):
    """
    自动填充Excel文件
    
    示例:
        fill-excel fill 项目数据.xlsx
        fill-excel fill 项目数据.xlsx -o 填充后.xlsx
        fill-excel fill 项目数据.xlsx --threshold 0.8
        fill-excel fill 项目数据.xlsx --dry-run
    """
    async def _fill():
        # 检查文件
        path = Path(file_path)
        if not path.exists():
            console.print(f"[red]错误: 文件不存在 {file_path}[/red]")
            raise typer.Exit(1)
        
        output_path = output or file_path
        console.print(Panel(
            f"填充Excel文件: [bold]{path.name}[/bold]\n"
            f"输出: [bold]{output_path}[/bold]\n"
            f"阈值: [bold]{threshold}[/bold]",
            style="blue"
        ))
        
        if dry_run:
            console.print("[yellow]模拟模式: 不会实际写入文件[/yellow]\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("正在填充...", total=None)
            
            # 创建Agent并填充
            agent = create_excel_agent()
            
            if dry_run:
                # 仅分析
                result = await agent.analyze_excel(file_path)
            else:
                result = await agent.fill_excel(file_path, output_path, threshold)
            
            progress.update(task, completed=True)
        
        if result.get("success"):
            console.print("\n[green]✓ 完成[/green]\n")
            
            # 显示填充结果
            response = result.get("response", "")
            console.print(response)
            
            if verbose:
                console.print(f"\n[dim]输入: {file_path}[/dim]")
                console.print(f"[dim]输出: {output_path}[/dim]")
                console.print(f"[dim]阈值: {threshold}[/dim]")
        else:
            console.print(f"[red]填充失败: {result.get('error', '未知错误')}[/red]")
    
    asyncio.run(_fill())


@app.command()
def query(
    field_name: str = typer.Argument(..., help="字段名称"),
    context: str = typer.Option("", "--context", "-c", help="项目上下文")
):
    """
    为特定字段检索知识库
    
    示例:
        fill-excel query "项目名称"
        fill-excel query "建设单位" -c "杭州市"
    """
    async def _query():
        console.print(Panel(
            f"检索字段: [bold]{field_name}[/bold]\n"
            f"上下文: [bold]{context or '无'}[/bold]",
            style="blue"
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("正在检索知识库...", total=None)
            
            agent = create_excel_agent()
            result = await agent.query_for_field(field_name, context)
            
            progress.update(task, completed=True)
        
        if result.get("success"):
            console.print("\n[green]✓ 检索完成[/green]\n")
            console.print(result.get("suggestions", ""))
        else:
            console.print(f"[red]检索失败[/red]")
    
    asyncio.run(_query())


@app.command()
def tools():
    """列出所有可用工具"""
    console.print(Panel("Excel助手可用工具", style="blue"))
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("工具名称", style="cyan")
    table.add_column("说明")
    
    tools_list = [
        ("read_excel", "读取Excel文件指定Sheet"),
        ("read_excel_all_sheets", "读取Excel所有Sheet概要"),
        ("search_knowledge_base", "从RAG知识库检索信息"),
        ("search_knowledge_base_for_field", "为特定字段检索知识库"),
        ("write_excel", "写入单个Excel字段"),
        ("write_excel_batch", "批量写入Excel字段"),
    ]
    
    for name, desc in tools_list:
        table.add_row(name, desc)
    
    console.print(table)


@app.command()
def version():
    """显示版本信息"""
    console.print("[bold]Excel辅助填写智能助手[/bold] v0.1.0")
    console.print("基于AutoGen + RAG知识库")
    console.print("项目: 规划选址论证报告AI智能体协作系统")


if __name__ == "__main__":
    app()