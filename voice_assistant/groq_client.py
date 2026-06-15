"""Single shared Groq client instance (lazy, so imports stay cheap for tests)."""

from functools import lru_cache

from groq import Groq

from voice_assistant.config import config


@lru_cache(maxsize=1)
def get_client() -> Groq:
    config.validate()
    return Groq(api_key=config.groq_api_key)
