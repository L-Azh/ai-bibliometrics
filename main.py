#!/usr/bin/env python3
"""
main.py
AI增强文献计量分析系统 - 最终版
用法: python main.py 你的文件.enw
"""

import sys
import os
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from dotenv import load_dotenv  # ← 添加这行

load_dotenv() 

# 导入自定义模块
from cnki_parser import quick_parse
from network_builder import NetworkBuilder
from visualizer import Visualizer
from ai_modules import DeepSeekAnalyzer

console = Console()


def print_banner():
    """打印欢迎界面"""
    console.print(Panel.fit(
        "[bold cyan]🚀 AI增强文献计量分析系统[/bold cyan]\n"
        "[dim]Powered by DeepSeek + Python + 知网数据[/dim]\n"
        "[green]版本: 1.0 | 作者: AI助手[/green]",
        title="[bold blue]欢迎使用[/bold blue]",
        border_style="cyan"
    ))


def print_stats(stats, papers):
    """打印数据统计表格"""
    table = Table(title="📊 数据概览", show_header=False, border_style="blue")
    table.add_column("指标", style="cyan", width=20)
    table.add_column("数值", style="green")
    
    table.add_row("文献总数", f"{stats['total']} 篇")
    table.add_row("时间跨度", f"{stats['years'][0] if stats['years'] else 'N/A'} - {stats['years'][-1] if stats['years'] else 'N/A'}")
    table.add_row("独立作者", f"{stats['authors']} 人")
    table.add_row("来源期刊", f"{stats['journals']} 种")
    table.add_row("涉及机构", f"{stats['institutions']} 个")
    
    # 计算总被引
    total_citations = sum(p.citations for p in papers)
    table.add_row("总被引次数", f"{total_citations} 次")
    
    console.print(table)


def print_top_papers(papers, n=5):
    """打印高影响力文献"""
    console.print(f"\n[bold yellow]📄 Top {n} 高影响力文献[/bold yellow]")
    
    # 按被引排序
    top_papers = sorted(papers, key=lambda x: x.citations, reverse=True)[:n]
    
    for i, p in enumerate(top_papers, 1):
        console.print(f"\n[bold]{i}. {p.title[:60]}...[/bold]")
        console.print(f"   [dim]作者: {', '.join(p.authors[:3])} | "
                     f"年份: {p.year} | "
                     f"被引: {p.citations}次 | "
                     f"期刊: {p.journal[:20]}[/dim]")


def main():
    # 检查命令行参数
    if len(sys.argv) < 2:
        console.print("[red]❌ 请提供文件名[/red]")
        console.print("[dim]用法: python main.py 大数据审计.enw[/dim]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        console.print(f"[red]❌ 文件不存在: {file_path}[/red]")
        sys.exit(1)
    
    # 开始分析
    print_banner()
    start_time = datetime.now()
    
    # 创建输出目录
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_dir = f"output_{base_name}"
    os.makedirs(output_dir, exist_ok=True)
    
    console.print(f"\n[bold blue]📂 正在分析: {file_path}[/bold blue]")
    console.print("=" * 60)
    
    # ========== 步骤1: 解析数据 ==========
    console.print("\n[bold green]步骤 1/5: 解析知网数据...[/bold green]")
    papers, df, stats = quick_parse(file_path)
    print_stats(stats, papers)
    print_top_papers(papers)
    
    # 保存原始数据
    excel_path = os.path.join(output_dir, "00_原始数据.xlsx")
    df.to_excel(excel_path, index=False)
    console.print(f"\n[dim]💾 原始数据已保存: {excel_path}[/dim]")
    
    # ========== 步骤2: 构建网络 ==========
    console.print("\n[bold green]步骤 2/5: 构建计量网络...[/bold green]")
    builder = NetworkBuilder(papers)
    
    coauth_net = builder.build_coauthorship(top_n=50)
    inst_net = builder.build_institution()
    keyword_net = builder.build_keywords(min_freq=2)
    
    # ========== 步骤3: 生成可视化 ==========
    console.print("\n[bold green]步骤 3/5: 生成可视化图谱...[/bold green]")
    viz = Visualizer(output_dir)
    
    viz.plot_coauthorship(coauth_net, "01_作者合作网络.png")
    viz.plot_institution(inst_net, "02_机构合作网络.png")
    viz.plot_keywords(keyword_net, "03_关键词共现网络.png")
    viz.plot_trend(papers, "04_年度发文趋势.png")
    viz.plot_wordcloud(papers, "05_关键词词云.png")
    viz.plot_top_authors(papers, top_n=15, filename="06_高产作者排名.png")
    
    # ========== 步骤4: AI智能分析 ==========
    api_key = os.getenv("DEEPSEEK_API_KEY")
    ai_report = None
    
    if api_key and len(papers) >= 5:
        console.print("\n[bold green]步骤 4/5: DeepSeek AI智能分析...[/bold green]")
        
        try:
            analyzer = DeepSeekAnalyzer(api_key)
            
            # 准备数据
            all_keywords = [kw for p in papers for kw in p.keywords]
            all_titles = [p.title for p in papers]
            
            # AI主题分析
            console.print("[dim]🤖 正在分析研究主题...[/dim]")
            theme_result = analyzer.analyze_themes(all_keywords, all_titles)
            
            # AI生成综述
            console.print("[dim]🤖 正在生成文献综述...[/dim]")
            top_papers_data = [{
                'title': p.title,
                'authors': p.authors,
                'year': p.year,
                'citations': p.citations
            } for p in sorted(papers, key=lambda x: x.citations, reverse=True)[:10]]
            
            review_result = analyzer.generate_summary(stats, top_papers_data)
            
            # 组合AI报告
            ai_report = f"""# 🤖 DeepSeek AI 智能分析报告

## 一、AI主题分析

{theme_result.content}

## 二、研究综述

{review_result.content}

## 三、数据基础

- 分析文献数: {stats['total']} 篇
- 时间跨度: {stats['years'][0] if stats['years'] else 'N/A'} - {stats['years'][-1] if stats['years'] else 'N/A'}
- 核心作者: {stats['authors']} 人
- 主要期刊: {stats['journals']} 种

---
*本报告由 DeepSeek AI 自动生成*
*分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            # 保存AI报告
            report_path = os.path.join(output_dir, "07_AI智能分析报告.md")
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(ai_report)
            
            console.print(f"[green]✅ AI报告已保存: {report_path}[/green]")
            console.print(f"[dim]💰 AI分析消耗: ¥{theme_result.cost_rmb + review_result.cost_rmb:.4f}[/dim]")
            
        except Exception as e:
            console.print(f"[yellow]⚠️ AI分析失败: {e}[/yellow]")
    else:
        if not api_key:
            console.print("\n[yellow]步骤 4/5: 跳过AI分析（未设置API密钥）[/yellow]")
            console.print("[dim]   设置方法: set DEEPSEEK_API_KEY=sk-your-key[/dim]")
        else:
            console.print("\n[yellow]步骤 4/5: 跳过AI分析（文献数不足5篇）[/yellow]")
    
    # ========== 步骤5: 完成汇总 ==========
    console.print("\n[bold green]步骤 5/5: 生成汇总报告...[/bold green]")
    
    # 生成README
    readme = f"""# 文献计量分析报告: {base_name}

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 数据概览

| 指标 | 数值 |
|------|------|
| 文献总数 | {stats['total']} 篇 |
| 时间跨度 | {stats['years'][0] if stats['years'] else 'N/A'} - {stats['years'][-1] if stats['years'] else 'N/A'} |
| 独立作者 | {stats['authors']} 人 |
| 来源期刊 | {stats['journals']} 种 |
| 涉及机构 | {stats['institutions']} 个 |

## 文件清单

| 文件名 | 说明 |
|--------|------|
| 00_原始数据.xlsx | 文献数据表格 |
| 01_作者合作网络.png | 作者合作关系图 |
| 02_机构合作网络.png | 机构合作关系图 |
| 03_关键词共现网络.png | 关键词共现图 |
| 04_年度发文趋势.png | 时间趋势图 |
| 05_关键词词云.png | 词云图 |
| 06_高产作者排名.png | 作者排名图 |
| 07_AI智能分析报告.md | DeepSeek AI分析（如有） |

## 使用说明

1. 查看PNG图片了解网络结构和趋势
2. 阅读AI分析报告获取深度洞察
3. 在Excel中查看原始数据

---
*本报告由 AI增强文献计量分析系统 自动生成*
"""
    
    readme_path = os.path.join(output_dir, "README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme)
    
    # 完成
    duration = (datetime.now() - start_time).total_seconds()
    
    console.print("\n" + "=" * 60)
    console.print(Panel.fit(
        f"[bold green]✅ 分析完成！[/bold green]\n\n"
        f"📁 输出目录: {output_dir}/\n"
        f"⏱️  耗时: {duration:.1f} 秒\n\n"
        f"[dim]建议查看顺序:[/dim]\n"
        f"1. README.md - 报告总览\n"
        f"2. 07_AI智能分析报告.md - AI深度洞察（如有）\n"
        f"3. PNG图片 - 可视化图谱\n"
        f"4. 00_原始数据.xlsx - 详细数据",
        title="[bold cyan]完成[/bold cyan]",
        border_style="green"
    ))
    console.print("=" * 60)


if __name__ == "__main__":
    main()