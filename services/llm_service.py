import os
from typing import List, Dict, Optional
import httpx
from fastapi import HTTPException, status
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class LLMService:
    """Service layer for external LLM interactions with OpenRouter API."""

    def __init__(self):
        self.api_url = OPENROUTER_URL

    def get_model(self, model_override: Optional[str] = None) -> str:
        """Resolve OpenRouter model name:
        1. Prioritize OPENROUTER_MODEL_NAME from .env if configured.
        2. Fall back to model_override (if provided and not dummy Swagger placeholder).
        3. Fall back to default 'openai/gpt-4o-mini'.
        """
        load_dotenv(override=True)
        env_model = os.getenv("OPENROUTER_MODEL_NAME", "").strip()
        if env_model and env_model.lower() not in ["string", "null", "none", "undefined"]:
            return env_model
        
        if model_override and model_override.strip():
            clean_model = model_override.strip()
            if clean_model.lower() not in ["string", "null", "none", "undefined"]:
                return clean_model

        return "openai/gpt-4o-mini"

    def get_api_key(self, api_key_override: Optional[str] = None) -> Optional[str]:
        """Resolve OpenRouter API key from override or environment variables (.env)."""
        if api_key_override and api_key_override.strip():
            clean_override = api_key_override.strip()
            if clean_override.lower() not in ["string", "null", "none", "undefined"]:
                return clean_override

        # Securely read from .env
        load_dotenv(override=True)
        env_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        if env_key and env_key.lower() not in ["string", "null", "none", "undefined"]:
            return env_key
        return None

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
        selected_model = self.get_model(model)

        if not api_key:
            last_prompt = messages[-1]["content"] if messages else "Hello"
            return (
                "⚡ **NEXUS AI Neural Core**\n\n"
                f"Aapka prompt receive ho gaya hai: *\"{last_prompt}\"*\n\n"
                f"• Configured Model (.env): `{selected_model}`\n\n"
                "> ⚠️ **OPENROUTER_API_KEY is Missing**\n>\n"
                "> Live AI generation ke liye OpenRouter API Key configure karna zaroori hai.\n>\n"
                "> 1. **[openrouter.ai/keys](https://openrouter.ai/keys)** se free API Key lein.\n"
                "> 2. Root folder mein `.env` file mein daalein:\n"
                ">    ```env\n"
                ">    OPENROUTER_API_KEY=sk-or-v1-...\n"
                f">    OPENROUTER_MODEL_NAME={selected_model}\n"
                ">    ```\n"
                ">    *Ya phir top-right **⋮ Menu > System Preferences** mein paste karein.*"
            )

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
            return f"⚠️ Network error connecting to OpenRouter API: {str(exc)}"

        if response.status_code != 200:
            try:
                error_body = response.json()
                error_msg = error_body.get("error", {}).get("message", response.text)
            except Exception:
                error_msg = response.text
            return f"⚠️ OpenRouter Error ({response.status_code}): {error_msg}"

        try:
            data = response.json()
            reply = data["choices"][0]["message"]["content"]
            return reply
        except (KeyError, IndexError, TypeError):
            return "⚠️ Unexpected response structure received from OpenRouter API."


# Singleton instance of LLMService
llm_service = LLMService()
