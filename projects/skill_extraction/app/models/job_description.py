from pydantic import Field

from app.models.base_model import BaseSchema


class JobDescriptionRequest(BaseSchema):
    title: str = Field(..., min_length=1)
    company: str | None = None
    location: str | None = None
    description: str = Field(..., min_length=1)
