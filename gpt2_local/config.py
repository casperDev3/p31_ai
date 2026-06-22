"""Конфігурація локального інференсу GPT-2.

GPT-2 — БАЗОВА мовна модель (не instruct/chat): вона продовжує текст,
а не відповідає на запити. Тому тут немає reasoning-режимів і chat-template.
"""

from __future__ import annotations

import torch

# Базова модель, 124M параметрів, ~500 MB. Без trust_remote_code, без chat-template.
MODEL_ID = "openai-community/gpt2"

# GPT-2 крихітна — float32 на MPS цілком комфортно (за бажання можна torch.float16).
DTYPE = torch.float32

# GPT-2 має контекст лише 1024 токени, тож тримаємо генерацію короткою.
MAX_NEW_TOKENS = 120

# GPT-2 схильна зациклюватись — стримуємо повторення.
GEN: dict = {
    "do_sample": True,
    "temperature": 0.8,
    "top_p": 0.95,
    "top_k": 50,
    "repetition_penalty": 1.2,
    "no_repeat_ngram_size": 3,
}


def pick_device() -> str:
    """Найкращий доступний бекенд: MPS на Mac, інакше CUDA, інакше CPU."""
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"
