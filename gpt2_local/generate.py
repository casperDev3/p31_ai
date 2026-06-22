"""Локальна генерація тексту з GPT-2 (продовження запиту).

Запуск із кореня репозиторію:

    python -m gpt2_local.generate

GPT-2 — базова мовна модель БЕЗ чату/інструкцій: вона ПРОДОВЖУЄ введений текст,
а не відповідає на питання. Введи початок речення — отримаєш продовження.
Команда виходу: /exit
"""

from __future__ import annotations

import sys

import torch
from transformers import TextStreamer

from .config import GEN, MAX_NEW_TOKENS
from .model import load_model

BANNER = (
    "\nGPT-2 — локальна генерація тексту (PyTorch)\n"
    "  Введи ПОЧАТОК тексту — модель його продовжить (це не чат).\n"
    "  /exit — вихід\n"
)


def main() -> int:
    tokenizer, model, device = load_model()
    streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
    print(BANNER)

    while True:
        try:
            prompt = input("prompt> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not prompt:
            continue
        if prompt == "/exit":
            break

        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        print(prompt, end="", flush=True)  # ехо запиту; streamer допише продовження
        with torch.no_grad():
            model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                streamer=streamer,
                pad_token_id=tokenizer.eos_token_id,
                **GEN,
            )
        print()

    print("До зустрічі!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
