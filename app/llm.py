"""
Thin wrapper around any OpenAI-compatible chat API (OpenAI, Gemini, Groq, OpenRouter...).
Switching provider = changing LLM_BASE_URL / LLM_MODEL / LLM_API_KEY in .env.
"""
from openai import OpenAI

from .config import settings


class LLMNotConfigured(Exception):
    pass


_client: OpenAI | None = None


def client() -> OpenAI:
    global _client
    if not settings.llm_api_key:
        raise LLMNotConfigured("LLM_API_KEY is empty. Copy .env.example to .env and set it.")
    if _client is None:
        _client = OpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url,
                         timeout=60, max_retries=2)
    return _client


def chat(messages: list[dict], tools: list[dict] | None = None, temperature: float = 0.1):
    kwargs = {"model": settings.llm_model, "messages": messages, "temperature": temperature}
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"
    return client().chat.completions.create(**kwargs).choices[0].message
