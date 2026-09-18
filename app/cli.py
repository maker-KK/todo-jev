"""Interactive CLI for To do - Jev."""
import sys
import asyncio
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app.router import TaskRouter
from app.classifier import JevClassifier
from app.config import Settings, settings as default_settings
from app.skill_registry import SkillRegistry
from app.skill_profiles import TOP_STAR_SKILL_PROFILES

app = typer.Typer(help="[To do - Jev] Intelligent Task Classifier & 3-Tier Router")
console = Console(legacy_windows=False)

async def run_routing(
    prompt: str,
    format_type: str = "one_line",
    threshold: Optional[float] = None,
    auto_sync: bool = True
):
    """Core routing runner with Star Skill awareness and Preflight Guarantees."""
    custom_settings = Settings(
        rule_threshold=threshold if threshold is not None else default_settings.rule_threshold,
        report_format=format_type,
        auto_sync_skills=auto_sync
    )
    classifier = JevClassifier(settings=custom_settings)
    router = TaskRouter(classifier=classifier)

    if format_type == "detailed":
        with console.status("[bold green]Querying Jev System One & Preflight verification...[/bold green]"):
            result = await router.route_and_execute(prompt)
    else:
        result = await router.route_and_execute(prompt)

    clf = result["classification"]
    tier = clf["recommended_tier"]
    rate = clf["matching_rate"]
    latency = result["latency_ms"]["total"]
    badge = clf.get("guarantee_badge", "Standard")
    matched_skill = clf.get("matched_skill")

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

        skill_tag = f" ★ [bold cyan]{matched_skill}[/bold cyan]" if matched_skill else ""
        guarantee_tag = f" [[bold green]{badge}[/bold green]]" if "Verified" in badge else f" [{badge}]"

        console.print(
            f"{tier_badge}{skill_tag}{guarantee_tag} [dim]({rate:.1%} match, {latency:.0f}ms)[/dim] "
            f"[bold]{prompt[:40] + ('...' if len(prompt) > 40 else '')}[/bold] "
            f"→ [italic]{clf['rationale']}[/italic]"
        )
        return result

    # 3. Detailed Table Mode
    table = Table(title="🎯 Jev Classification & Star Skill Verdict", show_header=True, header_style="bold cyan")
    table.add_column("Property", style="dim", width=22)
    table.add_column("Value", style="bold")

    table.add_row("User Prompt", result["prompt"])
    table.add_row("Task Type", str(clf["task_type"]))
    if matched_skill:
        table.add_row("Matched Star Skill", f"[bold cyan]{matched_skill}[/bold cyan] ({clf.get('skill_domain')})")
        table.add_row("Pre-flight Status", f"[green]PASSED[/green]: {clf.get('preflight_details')}" if clf.get('preflight_passed') else f"[red]FAILED[/red]: {clf.get('preflight_details')}")
        table.add_row("Guarantee Badge", f"[bold green]{badge}[/bold green]")
    table.add_row("Type Confidence", f"{clf['type_confidence']:.1%}")
    table.add_row("Can Handle Locally", f"{clf['can_handle_locally']:.1%}")
    table.add_row("Matching Rate", f"[green]{rate:.1%}[/green]" if rate >= 0.7 else f"[yellow]{rate:.1%}[/yellow]")
    table.add_row("Recommended Tier", f"[bold magenta]{tier}[/bold magenta]")
    table.add_row("Total Latency", f"{latency} ms (Classifier: {result['latency_ms']['classification']} ms)")

    console.print(table)
    console.print(Panel(clf["rationale"], title="💡 Rationale & Preflight Evidence", border_style="blue"))
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
def catalog():
    """Display curated GitHub Top Star Skill Profiles and pre-flight health."""
    table = Table(title="⭐ Curated GitHub Top Star Skill Knowledge Base", show_header=True, header_style="bold magenta")
    table.add_column("Skill ID", style="bold cyan", width=24)
    table.add_column("Domain", style="dim", width=22)
    table.add_column("Preflight Health", width=18)
    table.add_column("Triggers & Action", style="italic")

    for sid, prof in TOP_STAR_SKILL_PROFILES.items():
        passed, details = prof.precondition_check()
        health = "[green]✓ Ready[/green]" if passed else "[yellow]⚠ Warning[/yellow]"
        table.add_row(
            sid,
            prof.domain,
            f"{health}\n[dim]({details[:16]}..)[/dim]",
            f"[bold]{prof.display_name}[/bold]\nTriggers: {', '.join(prof.positive_triggers[:3])}..\nAction: {prof.recommended_action}"
        )

    console.print(table)

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
    console.print(f"[bold]Auto-sync status:[/bold] [green]{'ENABLED' if default_settings.auto_sync_skills else 'DISABLED'}[/green]")

@app.command()
def demo():
    """Run benchmark queries showcasing Star Skills & Preflight Guarantees."""
    test_cases = [
        "신규 결제 기능 EARS 기획서 작성하고 태스크 분할해줘",
        "현재 레거시 모듈 간 결합도 분석 및 DDD 도메인 분리 계획 세워줘",
        "로그인 페이지 폼 자동 입력 및 화면 캡처하는 E2E 테스트 작성해줘",
        "15 + 27 수식 계산하고 cm 단위로 변환해줘",
        "다음 파이썬 비동기 웹소켓 서버 코드 리팩토링 및 아키텍처 설계해줘",
    ]
    console.print("[bold yellow]🚀 Running Star-Skill Grounded Routing Demo (One-line Mode)...[/bold yellow]\n")
    for prompt in test_cases:
        asyncio.run(run_routing(prompt, format_type="one_line"))
    
    console.print("\n[bold cyan]💡 Tip: Run `todo-jev catalog` to inspect curated star skill profiles![/bold cyan]")

if __name__ == "__main__":
    app()
