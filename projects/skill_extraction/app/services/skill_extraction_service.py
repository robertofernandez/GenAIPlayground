from app.models.job_description import JobDescriptionRequest
from app.models.skill_response import SkillExtractionResponse
from app.providers.anthropic_provider import LLMProvider, AnthropicProvider


class SkillExtractionService:
    def __init__(self, provider: LLMProvider | None = None):
        self.provider = provider or AnthropicProvider()

    def extract_skills(self, request: JobDescriptionRequest) -> SkillExtractionResponse:
        content = "\n".join(
            part for part in [request.title, request.company, request.location, request.description] if part
        )
        return self.provider.extract_skills(content)
