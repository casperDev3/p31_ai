"""Simple local commands handled without an LLM call.

handle(text) returns a response string, or None if no local command matched.
"""

from datetime import datetime

EXIT_WORDS = {"вихід", "вийти", "стоп", "до побачення", "exit", "quit", "stop"}


def is_exit_command(text: str) -> bool:
    t = text.lower().strip(" .!?")
    return any(word in t for word in EXIT_WORDS)


def handle(text: str) -> str | None:
    t = text.lower()

    if "котра година" in t or "який час" in t or "time" in t:
        return f"Зараз {datetime.now():%H:%M}."

    if "яке сьогодні число" in t or "яка дата" in t or "date" in t:
        return f"Сьогодні {datetime.now():%d.%m.%Y}."

    return None
