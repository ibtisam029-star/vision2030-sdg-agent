"""Bilingual road-safety agent with offline and Claude tool-use modes."""
import json
import os
from pathlib import Path
from typing import Any

from vision2030_sdg_agent.models import Report
from vision2030_sdg_agent.tools.domain import (
    analyze_incidents,
    forecast_incidents,
    load_data,
    recommend_actions,
)

DEFAULT_DATA = Path(__file__).resolve().parents[2] / "data/sample/incidents.csv"
TOOLS = [
    {"name": "load_data", "description": "Load incident CSV records", "input_schema": {
        "type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    {"name": "analyze_incidents", "description": "Summarize incident patterns", "input_schema": {
        "type": "object", "properties": {}}},
    {"name": "forecast_incidents", "description": "Calculate a naive baseline", "input_schema": {
        "type": "object", "properties": {}}},
    {"name": "recommend_actions", "description": "Suggest human-reviewed safety actions", "input_schema": {
        "type": "object", "properties": {}}},
]


def build_report(path: str, language: str = "en", mode: str = "mock") -> Report:
    """Execute validated tools deterministically to create a report."""
    records = load_data(path)
    metrics = analyze_incidents(records)
    return Report(language=language, mode=mode, **metrics,
                  forecast_incidents=forecast_incidents(records),
                  recommendations=recommend_actions(metrics, language),
                  limitations=("بيانات اصطناعية؛ ليست لتوجيه الإنفاذ أو تحديد المسؤولية"
                               if language == "ar" else
                               "Synthetic sample; not for enforcement or fault attribution"))


def run_agent(path: str | None = None, language: str = "en", mock: bool = False,
              model: str = "claude-sonnet-4-5") -> Report:
    """Run without credentials in mock mode, or use an allowlisted Claude tool loop."""
    if language not in ("en", "ar"):
        raise ValueError("language must be en or ar")
    data_path = str(Path(path or DEFAULT_DATA).resolve())
    if mock:
        return build_report(data_path, language)
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY required in live mode; use --mock")
    try:
        import anthropic
    except ImportError as exc:
        raise RuntimeError("Install the anthropic SDK") from exc
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    prompt = Path(__file__).with_name("prompts").joinpath("system.txt").read_text(
        encoding="utf-8")
    messages: list[dict[str, Any]] = [{"role": "user", "content": (
        f"Analyze incident data at {data_path}; call load_data, analyze_incidents, "
        f"forecast_incidents, recommend_actions. Respond in {language}. "
        "Do not invent statistics or make enforcement decisions.")}]
    records = None
    metrics = None
    forecast = None
    recs = None
    for _ in range(12):
        response = client.messages.create(model=model, max_tokens=1200, system=prompt,
                                          tools=TOOLS, messages=messages)
        messages.append({"role": "assistant", "content": response.content})
        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            if block.name == "load_data":
                if Path(block.input.get("path", "")).resolve() != Path(data_path):
                    raise ValueError("Unauthorized path")
                records = load_data(data_path)
                result: Any = {"records_loaded": len(records)}
            elif block.name == "analyze_incidents":
                if records is None:
                    raise ValueError("load_data required first")
                metrics = analyze_incidents(records)
                result = metrics
            elif block.name == "forecast_incidents":
                if records is None:
                    raise ValueError("load_data required first")
                forecast = forecast_incidents(records)
                result = {"forecast_incidents": forecast}
            elif block.name == "recommend_actions":
                if metrics is None:
                    raise ValueError("analyze_incidents required first")
                recs = recommend_actions(metrics, language)
                result = [r.model_dump() for r in recs]
            else:
                raise ValueError("Unknown tool")
            results.append({"type": "tool_result", "tool_use_id": block.id,
                            "content": json.dumps(result, ensure_ascii=False)})
        if results:
            messages.append({"role": "user", "content": results})
        elif response.stop_reason == "end_turn":
            if metrics is None or forecast is None or recs is None:
                raise RuntimeError("Agent stopped before completing all tools")
            return build_report(data_path, language, mode="live")
        else:
            raise RuntimeError(f"Unexpected stop reason: {response.stop_reason}")
    raise RuntimeError("Tool-use round limit reached")
