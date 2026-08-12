from fastapi import APIRouter, Depends

from app.models.job_description import JobDescriptionRequest
from app.models.skill_response import SkillExtractionResponse
from app.services.skill_extraction_service import SkillExtractionService

router = APIRouter()


def get_skill_extraction_service() -> SkillExtractionService:
    return SkillExtractionService()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/skills/extract", response_model=SkillExtractionResponse)
def extract_skills(
    request: JobDescriptionRequest,
    service: SkillExtractionService = Depends(get_skill_extraction_service),
) -> SkillExtractionResponse:
    return service.extract_skills(request)
