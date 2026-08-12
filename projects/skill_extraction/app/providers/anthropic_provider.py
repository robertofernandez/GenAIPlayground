import json
from abc import ABC, abstractmethod
import logging
from typing import Any

# Configura logging si no lo tienes
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

import httpx

from app.core.config import settings
from app.core.utils import load_prompt
from app.models.skill_response import SkillExtractionResponse


class LLMProvider(ABC):
    @abstractmethod
    def extract_skills(self, job_description: str) -> SkillExtractionResponse:
        raise NotImplementedError


class AnthropicResponseParser:

    @staticmethod
    def _extract_json(text: str) -> str:
        text = text.strip()

        # Buscar el primer { o [
        start = None
        stack = []

        for i, ch in enumerate(text):
            if ch == "{":
                start = i
                stack.append("}")
                break
            elif ch == "[":
                start = i
                stack.append("]")
                break

        if start is None:
            raise ValueError("No JSON found in response.")

        in_string = False
        escaped = False

        for i in range(start + 1, len(text)):
            ch = text[i]

            if escaped:
                escaped = False
                continue

            if ch == "\\":
                escaped = True
                continue

            if ch == '"':
                in_string = not in_string
                continue

            if in_string:
                continue

            if ch == "{":
                stack.append("}")
            elif ch == "[":
                stack.append("]")
            elif ch in "}]":
                if not stack or ch != stack[-1]:
                    raise ValueError(
                        f"Unexpected '{ch}' at position {i}."
                    )

                stack.pop()

                if not stack:
                    return text[start:i + 1]

        raise ValueError("JSON appears to be incomplete.")

    @staticmethod
    def parse(raw_payload: str) -> SkillExtractionResponse:

        try:
            cleaned = AnthropicResponseParser._extract_json(raw_payload)
            payload = json.loads(cleaned)

        except Exception:
            logger.exception(
                "Unable to parse Anthropic response:\n%s",
                raw_payload
            )
            raise

        skills = []

        for skill in payload.get("skills", []):

            if not isinstance(skill, dict):
                continue

            name = skill.get("name")

            if not name:
                continue

            skills.append({
                "name": name,
                "category": skill.get("category"),
                "confidence": skill.get("confidence"),
            })

        return SkillExtractionResponse(
            title=payload.get("title"),
            skills=skills,
            summary=payload.get("summary"),
        )

class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str | None = None, api_url: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.anthropic_api_key
        self.api_url = api_url or settings.anthropic_api_url
        self.model = model or settings.model

    def extract_skills(self, job_description: str) -> SkillExtractionResponse:
        if not self.api_key:
            return SkillExtractionResponse(
                title="Unknown",
                skills=[],
                summary="Anthropic API key is not configured.",
            )

        prompt = load_prompt("skill_extraction_prompt.txt")
        payload = {
            "model": self.model,
            "max_tokens": 600,
            "messages": [
                {
                    "role": "user",
                    "content": f"{prompt}\n\nJob description:\n{job_description}",
                }
            ],
        }

        headers = {
            "x-api-key": self.api_key,
            "content-type": "application/json",
            "anthropic-version": "2023-06-01",
        }

        print(f"📡 Sending request to Anthropic API at {self.api_url} with model {self.model} and headers: {headers}")

        # LOG DE LA SOLICITUD
        logger.info("=" * 80)
        logger.info("📤 REQUEST TO ANTHROPIC API")
        logger.info(f"URL: {self.api_url}/v1/messages")
        logger.info(f"Model: {self.model}")
        logger.info(f"Headers: {headers}")
        logger.info(f"Payload (truncado): {json.dumps(payload, indent=2)[:500]}...")
        logger.info("=" * 80)
        
        response = httpx.post(
            f"{self.api_url}/v1/messages",
            headers=headers,
            json=payload,
            timeout=30.0,
        )

                  # LOG DE LA RESPUESTA COMPLETA
        logger.info("=" * 80)
        logger.info("📥 RESPONSE FROM ANTHROPIC API")
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Headers Response: {dict(response.headers)}")
        logger.info(f"Response Content (truncado): {response.text[:500]}...")
        c1 = response.json()["content"][0]
        logger.info(f"Content 1 truncado: {c1}")
        content = response.json()["content"][0]["text"]
        logger.info(f"Content: {content[:500]}")

        #response.raise_for_status()
        return AnthropicResponseParser.parse(content)
