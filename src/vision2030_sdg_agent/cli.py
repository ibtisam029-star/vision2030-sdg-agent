"""Typer command-line interface."""
import json
from pathlib import Path
from typing import Annotated

import typer
from dotenv import load_dotenv

from vision2030_sdg_agent.agent import run_agent

app = typer.Typer(help="Vision 2030 / SDG 3 bilingual road-safety planning agent")


@app.command()
def run(
    mock: Annotated[bool, typer.Option(help="Run without API key or network")] = False,
    language: Annotated[str, typer.Option(help="en or ar")] = "en",
    data: Annotated[Path | None, typer.Option(help="CSV input file")] = None,
    model: Annotated[str, typer.Option(help="Anthropic model ID")] = "claude-sonnet-4-5",
) -> None:
    """Analyze records and print a JSON report."""
    load_dotenv()
    try:
        report = run_agent(str(data) if data else None, language=language,
                           mock=mock, model=model)
    except (ValueError, OSError, RuntimeError) as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(json.dumps(report.model_dump(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    app()
