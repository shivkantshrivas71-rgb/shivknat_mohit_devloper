import os
from typing import List, Dict, Optional
import httpx
from fastapi import HTTPException, status
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"


class LLMService:
    """Service layer for external LLM interactions with OpenRouter API."""

    def __init__(self):
        self.api_url = OPENROUTER_URL
        self.default_model = DEFAULT_MODEL

    def get_api_key(self, api_key_override: Optional[str] = None) -> str:
        """Resolve OpenRouter API key from override or environment variables."""
        if api_key_override and api_key_override.strip():
            return api_key_override.strip()

        # Securely read from .env
        env_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        if not env_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OPENROUTER_API_KEY is not configured in the server environment (.env file)."
            )
        return env_key

    async def call_openrouter(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        api_key_override: Optional[str] = None,
        site_url: str = "http://localhost:8000",
        site_name: str = "ChatBOT API"
    ) -> str:
        """
        Send formatted messages to OpenRouter chat completions endpoint and return the text reply.
        """
        api_key = self.get_api_key(api_key_override)
        selected_model = model.strip() if model and model.strip() else self.default_model

        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": site_url,
            "X-Title": site_name,
            "Content-Type": "application/json"
        }

        payload = {
            "model": selected_model,
            "messages": messages
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Network error connecting to OpenRouter API: {str(exc)}"
            )

        if response.status_code != 200:
            try:
                error_body = response.json()
                error_msg = error_body.get("error", {}).get("message", response.text)
            except Exception:
                error_msg = response.text
            raise HTTPException(
                status_code=response.status_code,
                detail=f"OpenRouter API Error: {error_msg}"
            )

        try:
            data = response.json()
            reply = data["choices"][0]["message"]["content"]
            return reply
        except (KeyError, IndexError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Invalid or unexpected response structure received from OpenRouter API."
            )


# Singleton instance of LLMService
llm_service = LLMService()
