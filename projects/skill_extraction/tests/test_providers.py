import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.models.skill_response import SkillExtractionResponse, SkillItem
from app.providers.anthropic_provider import AnthropicResponseParser


def test_response_parser_builds_skill_models():
    raw_payload = '{"skills": [{"name": "Python", "category": "backend", "confidence": 0.95}], "summary": "Great fit"}'

    parsed = AnthropicResponseParser.parse(raw_payload)

    assert isinstance(parsed, SkillExtractionResponse)
    assert parsed.skills[0].name == "Python"
    assert parsed.summary == "Great fit"
