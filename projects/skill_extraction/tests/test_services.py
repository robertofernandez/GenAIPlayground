import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.models.job_description import JobDescriptionRequest
from app.models.skill_response import SkillExtractionResponse, SkillItem
from app.providers.anthropic_provider import LLMProvider
from app.services.skill_extraction_service import SkillExtractionService


class DummyProvider(LLMProvider):
    def extract_skills(self, job_description: str) -> SkillExtractionResponse:
        return SkillExtractionResponse(
            title="Software Engineer",
            skills=[SkillItem(name="Python"), SkillItem(name="FastAPI")],
            summary="Strong backend experience",
        )


def test_service_returns_structured_skills():
    service = SkillExtractionService(provider=DummyProvider())
    request = JobDescriptionRequest(
        title="Software Engineer",
        company="Acme",
        location="Remote",
        description="We need a Python backend engineer with FastAPI experience.",
    )

    response = service.extract_skills(request)

    assert response.title == "Software Engineer"
    assert [skill.name for skill in response.skills] == ["Python", "FastAPI"]
    assert response.summary == "Strong backend experience"
