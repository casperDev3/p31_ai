"""Локальний CLI-чат із Nemotron-Nano-4B (reasoning on/off).

Запуск із кореня репозиторію:

    python -m nemotron_nano_4b.chat

Команди в діалозі:
    /think      — увімкнути міркування ("detailed thinking on")
    /no_think   — вимкнути міркування (жадібне декодування)
    /reset      — очистити історію діалогу
    /exit       — вихід
"""

from __future__ import annotations

import sys

import torch
from transformers import TextStreamer

from .config import (
    GEN_THINK_OFF,
    GEN_THINK_ON,
    MAX_NEW_TOKENS,
    THINK_OFF,
    THINK_ON,
)
from .model import load_model

BANNER = (
    "\nNemotron-Nano-4B — локальний reasoning-чат (PyTorch+MPS)\n"
    "  /think — міркування ON    /no_think — OFF\n"
    "  /reset — очистити історію  /exit — вихід\n"
)


def build_messages(history: list[dict], think: bool) -> list[dict]:
    """Системний промпт-перемикач reasoning + накопичена історія."""
    system = THINK_ON if think else THINK_OFF
    return [{"role": "system", "content": system}, *history]


def main() -> int:
    tokenizer, model, device = load_model()
    streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
    history: list[dict] = []
    think = True
    print(BANNER)

    while True:
        try:
            user = input("ти> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user:
            continue
        if user == "/exit":
            break
        if user == "/think":
            think = True
            print("[режим] міркування ON")
            continue
        if user == "/no_think":
            think = False
            print("[режим] міркування OFF")
            continue
        if user == "/reset":
            history = []
            print("[історію очищено]")
            continue

        history.append({"role": "user", "content": user})
        # transformers 5.x: return_dict=True дає BatchEncoding (input_ids + attention_mask),
        # який передаємо в generate через **inputs.
        inputs = tokenizer.apply_chat_template(
            build_messages(history, think),
            add_generation_prompt=True,
            return_tensors="pt",
            return_dict=True,
        ).to(device)

        gen_kwargs = GEN_THINK_ON if think else GEN_THINK_OFF
        print("nemotron> ", end="", flush=True)
        with torch.no_grad():
            out = model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                streamer=streamer,
                pad_token_id=tokenizer.eos_token_id,
                **gen_kwargs,
            )

        prompt_len = inputs["input_ids"].shape[-1]
        # clean_up_tokenization_spaces=False: канонічно для BPE-токенайзера
        # (інакше transformers лише попереджає й усе одно ігнорує cleanup).
        reply = tokenizer.decode(
            out[0, prompt_len:],
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        ).strip()
        history.append({"role": "assistant", "content": reply})

    print("До зустрічі!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
