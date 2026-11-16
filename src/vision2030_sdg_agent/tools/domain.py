"""Deterministic road-incident analysis tools; no enforcement decisions."""
import csv
from collections import Counter
from pathlib import Path

from vision2030_sdg_agent.models import Incident, Recommendation


def load_data(path: str) -> list[Incident]:
    """Load validated synthetic or permitted open-data incident records."""
    with Path(path).open(newline="", encoding="utf-8") as stream:
        records = [Incident.model_validate(row) for row in csv.DictReader(stream)]
    if not records:
        raise ValueError("No incident records found")
    return records


def analyze_incidents(records: list[Incident]) -> dict[str, int | str]:
    """Summarize incident counts, injuries, fatalities, and peak hour."""
    if not records:
        raise ValueError("At least one incident is required")
    return {
        "record_count": len(records),
        "total_injuries": sum(r.injuries for r in records),
        "total_fatalities": sum(r.fatalities for r in records),
        "highest_incident_district": sorted(Counter(r.district for r in records).items(),
                                             key=lambda pair: (-pair[1], pair[0]))[0][0],
        "peak_hour": sorted(Counter(r.hour for r in records).items(),
                            key=lambda pair: (-pair[1], pair[0]))[0][0],
    }


def forecast_incidents(records: list[Incident]) -> int:
    """Return a naive next-period baseline equal to observed incident count."""
    if not records:
        raise ValueError("At least one incident is required")
    return len(records)


def recommend_actions(metrics: dict[str, int | str], language: str = "en") -> list[Recommendation]:
    """Produce SDG-tagged, human-reviewed safety suggestions."""
    if language not in ("en", "ar"):
        raise ValueError("Unsupported language")
    district = metrics["highest_incident_district"]
    hour = metrics["peak_hour"]
    if language == "ar":
        note = "ثقة منخفضة: بيانات اصطناعية صغيرة؛ تتطلب مراجعة بشرية"
        return [
            Recommendation(action=f"راجع سلامة الطرق في منطقة {district} ميدانياً",
                           sdg_target="3.6", confidence_note=note),
            Recommendation(action=f"راجع تصميم عبور المشاة قرب الساعة {hour}:00",
                           sdg_target="11.2", confidence_note=note),
        ]
    note = "Low confidence: small synthetic sample; field validation required"
    return [
        Recommendation(action=f"Request a human road-safety audit in {district}",
                       sdg_target="3.6", confidence_note=note),
        Recommendation(action=f"Review pedestrian crossing safety around {hour}:00",
                       sdg_target="11.2", confidence_note=note),
    ]
