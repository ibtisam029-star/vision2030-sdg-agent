"""Unit tests for all four road safety tools."""
import pytest
from vision2030_sdg_agent.agent import DEFAULT_DATA
from vision2030_sdg_agent.tools.domain import (
    load_data, analyze_incidents, forecast_incidents, recommend_actions,
)


def test_loader():
    assert len(load_data(str(DEFAULT_DATA))) == 5


def test_analyzer():
    m = analyze_incidents(load_data(str(DEFAULT_DATA)))
    assert m["total_injuries"] == 5
    assert m["highest_incident_district"] == "Riyadh North"


def test_forecast():
    assert forecast_incidents(load_data(str(DEFAULT_DATA))) == 5


def test_recommender():
    m = analyze_incidents(load_data(str(DEFAULT_DATA)))
    assert all(r.sdg_target and r.confidence_note for r in recommend_actions(m, "ar"))


def test_empty_forecast():
    with pytest.raises(ValueError):
        forecast_incidents([])
