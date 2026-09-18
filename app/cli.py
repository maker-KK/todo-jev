"""Interactive CLI for To do - Jev."""
import asyncio
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from app.router import TaskRouter

app = typer.Typer(help="⚡ To do - Jev: Intelligent Task Classifier & 3-Tier Router")
console = Console()

@app.command()
def route(prompt: str = typer.Argument(..., help="User prompt to classify and route")):
    """Classify a single task and view routing decisions in real-time."""
    async def _run():
        router = TaskRouter()
        with console.status("[bold green]Querying Jev System One classifier...[/bold green]"):
            result = await router.route_and_execute(prompt)

        clf = result["classification"]
        
        # Display Result
        table = Table(title="🎯 Jev Classification & Routing Verdict", show_header=True, header_style="bold cyan")
        table.add_column("Property", style="dim", width=22)
        table.add_column("Value", style="bold")

        table.add_row("User Prompt", result["prompt"])
        table.add_row("Task Type", clf["task_type"])
        table.add_row("Type Confidence", f"{clf['type_confidence']:.1%}")
        table.add_row("Can Handle Locally", f"{clf['can_handle_locally']:.1%}")
        table.add_row("Matching Rate", f"[green]{clf['matching_rate']:.1%}[/green]" if clf['matching_rate'] >= 0.7 else f"[yellow]{clf['matching_rate']:.1%}[/yellow]")
        table.add_row("Recommended Tier", f"[bold magenta]{clf['recommended_tier']}[/bold magenta]")
        table.add_row("Total Latency", f"{result['latency_ms']['total']} ms (Classifier: {result['latency_ms']['classification']} ms)")

        console.print(table)
        console.print(Panel(clf["rationale"], title="💡 Rationale", border_style="blue"))

    asyncio.run(_run())

@app.command()
def demo():
    """Run built-in benchmark queries across diverse task categories."""
    test_cases = [
        "PDF 0페이지의 3번 문항 정답과 쪽수 앵커 연결해줘",
        "15 + 27 수식 계산하고 cm 단위로 변환해줘",
        "다음 파이썬 비동기 웹소켓 서버 코드 리팩토링 및 아키텍처 설계해줘",
        "첨부된 기하 문제 그림에서 삼각형의 각도를 읽어줘"
    ]
    console.print("[bold yellow]🚀 Running To do - Jev Multi-Task Routing Demo...[/bold yellow]\n")
    for prompt in test_cases:
        route(prompt)
        console.print("\n" + "─" * 60 + "\n")

if __name__ == "__main__":
    app()
