from pydantic import Field

from app.models.base_model import BaseSchema


class SkillItem(BaseSchema):
    name: str = Field(..., min_length=1)
    category: str | None = None
    confidence: float | None = None


class SkillExtractionResponse(BaseSchema):
    title: str | None = None
    skills: list[SkillItem] = Field(default_factory=list)
    summary: str | None = None
