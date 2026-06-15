"""Free-form request handling via Groq chat completions, with short memory."""

from voice_assistant.config import config
from voice_assistant.groq_client import get_client
from voice_assistant.utils.logger import get_logger

log = get_logger(__name__)

# Rolling conversation history (system prompt kept separate).
_history: list[dict] = []
_MAX_TURNS = 6  # keep last N user/assistant messages


def process(text: str) -> str:
    client = get_client()
    _history.append({"role": "user", "content": text})

    messages = [{"role": "system", "content": config.system_prompt}, *_history[-_MAX_TURNS:]]

    resp = client.chat.completions.create(
        model=config.llm_model,
        messages=messages,
        temperature=config.temperature,
    )
    answer = resp.choices[0].message.content.strip()
    _history.append({"role": "assistant", "content": answer})
    log.info("Відповідь LLM: %s", answer)
    return answer


def reset_memory() -> None:
    _history.clear()
