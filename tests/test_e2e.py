"""End-to-end bilingual CLI tests without API credentials."""
from typer.testing import CliRunner

from vision2030_sdg_agent.cli import app


def test_mock_cli_english():
    result = CliRunner().invoke(app, ["--mock", "--language", "en"])
    assert result.exit_code == 0, result.output
    assert '"sdg_target": "3.6"' in result.output


def test_mock_cli_arabic():
    result = CliRunner().invoke(app, ["--mock", "--language", "ar"])
    assert result.exit_code == 0, result.output
    assert "راجع" in result.output
