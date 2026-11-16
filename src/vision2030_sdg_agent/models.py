"""Validated road safety records and outputs."""
from pydantic import BaseModel, Field


class Incident(BaseModel):
    district: str = Field(min_length=1)
    severity: str
    hour: int = Field(ge=0, le=23)
    injuries: int = Field(ge=0)
    fatalities: int = Field(ge=0)


class Recommendation(BaseModel):
    action: str
    sdg_target: str = Field(pattern=r"^(3\.6|11\.2)$")
    confidence_note: str = Field(min_length=5)


class Report(BaseModel):
    language: str
    mode: str
    record_count: int
    total_injuries: int
    total_fatalities: int
    highest_incident_district: str
    peak_hour: int
    forecast_incidents: int
    recommendations: list[Recommendation]
    limitations: str
