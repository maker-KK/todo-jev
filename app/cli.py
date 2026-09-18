"""Interactive CLI for To do - Jev."""
import asyncio
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from app.router import TaskRouter
from app.classifier import JevClassifier
from app.config import Settings, settings as default_settings
from app.skill_registry import SkillRegistry

app = typer.Typer(help="⚡ To do - Jev: Intelligent Task Classifier & 3-Tier Router")
console = Console()

async def run_routing(
    prompt: str,
    format_type: str = "one_line",
    threshold: Optional[float] = None,
    auto_sync: bool = True
):
    """Core routing runner."""
    custom_settings = Settings(
        rule_threshold=threshold if threshold is not None else default_settings.rule_threshold,
        report_format=format_type,
        auto_sync_skills=auto_sync
    )
    classifier = JevClassifier(settings=custom_settings)
    router = TaskRouter(classifier=classifier)

    if format_type == "detailed":
        with console.status("[bold green]Querying Jev System One classifier...[/bold green]"):
            result = await router.route_and_execute(prompt)
    else:
        result = await router.route_and_execute(prompt)

    clf = result["classification"]
    tier = clf["recommended_tier"]
    rate = clf["matching_rate"]
    latency = result["latency_ms"]["total"]

    # 1. Quiet Mode
    if format_type == "quiet":
        return result

    # 2. One-line Mode (Default)
    if format_type == "one_line":
        if "Tier 1" in tier:
            tier_badge = "[bold green][Tier 1: Rule][/bold green]"
        elif "Tier 2" in tier:
            tier_badge = "[bold blue][Tier 2: Jev][/bold blue]"
        else:
            tier_badge = "[bold magenta][Tier 3: LLM][/bold magenta]"

        console.print(
            f"{tier_badge} [dim]({rate:.1%} match, {latency:.0f}ms)[/dim] "
            f"[bold]{prompt[:40] + ('...' if len(prompt) > 40 else '')}[/bold] "
            f"→ [italic]{clf['rationale']}[/italic]"
        )
        return result

    # 3. Detailed Table Mode
    table = Table(title="🎯 Jev Classification & Routing Verdict", show_header=True, header_style="bold cyan")
    table.add_column("Property", style="dim", width=22)
    table.add_column("Value", style="bold")

    table.add_row("User Prompt", result["prompt"])
    table.add_row("Task Type", str(clf["task_type"]))
    table.add_row("Type Confidence", f"{clf['type_confidence']:.1%}")
    table.add_row("Can Handle Locally", f"{clf['can_handle_locally']:.1%}")
    table.add_row("Matching Rate", f"[green]{rate:.1%}[/green]" if rate >= 0.7 else f"[yellow]{rate:.1%}[/yellow]")
    table.add_row("Recommended Tier", f"[bold magenta]{tier}[/bold magenta]")
    table.add_row("Total Latency", f"{latency} ms (Classifier: {result['latency_ms']['classification']} ms)")
    table.add_row("Auto-Synced Skills", f"{'Enabled' if auto_sync else 'Disabled'}")

    console.print(table)
    console.print(Panel(clf["rationale"], title="💡 Rationale", border_style="blue"))
    return result

@app.command()
def route(
    prompt: str = typer.Argument(..., help="User prompt to classify and route"),
    format: str = typer.Option(
        default_settings.report_format,
        "--format", "-f",
        help="Report format: 'one_line' (default), 'detailed', 'quiet'"
    ),
    threshold: Optional[float] = typer.Option(
        None,
        "--threshold", "-t",
        help="Override rule matching threshold (0.0 to 1.0)"
    ),
    auto_sync: bool = typer.Option(
        default_settings.auto_sync_skills,
        "--auto-sync/--no-auto-sync",
        help="Enable or disable auto-syncing installed skills with Jev criteria"
    )
):
    """Classify a single task and view routing decisions in real-time."""
    asyncio.run(run_routing(prompt, format_type=format, threshold=threshold, auto_sync=auto_sync))

@app.command()
def skills():
    """List discovered agent skills and preview Jev criteria synchronization."""
    registry = SkillRegistry()
    discovered = registry.discover_skills()
    
    table = Table(title=f"📦 Discovered Agent Skills ({len(discovered)} total)", show_header=True, header_style="bold green")
    table.add_column("Skill Name", style="bold cyan", width=30)
    table.add_column("Description Preview", style="dim")
    table.add_column("Source Location", style="italic blue")

    for name, meta in list(discovered.items())[:20]:
        clean_desc = meta.description.strip().replace("\n", " ")
        if len(clean_desc) > 80:
            clean_desc = clean_desc[:77] + "..."
        table.add_row(name, clean_desc, str(meta.path.name))

    console.print(table)
    if len(discovered) > 20:
        console.print(f"[dim]... and {len(discovered) - 20} more skills ready for Jev auto-sync.[/dim]\n")
    console.print(f"[bold]Auto-sync status:[/bold] [green]{'ENABLED' if default_settings.auto_sync_skills else 'DISABLED'}[/green] (Toggle via JEV_AUTO_SYNC_SKILLS=false or --no-auto-sync)")

@app.command()
def demo():
    """Run built-in benchmark queries across diverse task categories."""
    test_cases = [
        "PDF 0페이지의 3번 문항 정답과 쪽수 앵커 연결해줘",
        "15 + 27 수식 계산하고 cm 단위로 변환해줘",
        "다음 파이썬 비동기 웹소켓 서버 코드 리팩토링 및 아키텍처 설계해줘",
        "첨부된 기하 문제 그림에서 삼각형의 각도를 읽어줘"
    ]
    console.print("[bold yellow]🚀 Running To do - Jev Multi-Task Routing Demo (One-line Mode)...[/bold yellow]\n")
    for prompt in test_cases:
        asyncio.run(run_routing(prompt, format_type="one_line"))
    
    console.print("\n[bold cyan]💡 Tip: Use `todo-jev route --format detailed` for full inspection tables![/bold cyan]")

if __name__ == "__main__":
    app()
