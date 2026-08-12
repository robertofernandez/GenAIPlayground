import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.main import create_app
from app.models.job_description import JobDescriptionRequest
from app.models.skill_response import SkillExtractionResponse, SkillItem
from app.services.skill_extraction_service import SkillExtractionService
from app.api.v1.routes import get_skill_extraction_service


class DummyProvider:
    def extract_skills(self, job_description: str) -> SkillExtractionResponse:
        return SkillExtractionResponse(
            title="Data Engineer",
            skills=[SkillItem(name="SQL")],
            summary="Good fit",
        )


def test_health_endpoint():
    app = create_app()
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_extract_endpoint_returns_response():
    app = create_app()
    app.dependency_overrides[get_skill_extraction_service] = lambda: SkillExtractionService(provider=DummyProvider())
    client = TestClient(app)

    response = client.post(
        "/skills/extract",
        json={
            "title": "Data Engineer",
            "company": "Acme",
            "location": "Remote",
            "description": "We need someone who works with SQL and data pipelines.",
        },
    )

    assert response.status_code == 200
    assert response.json()["skills"][0]["name"] == "SQL"
