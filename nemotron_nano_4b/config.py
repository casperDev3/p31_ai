"""Конфігурація локального інференсу Nemotron-Nano-4B на Apple Silicon.

Уся «магія» зібрана тут, щоб model.py / chat.py лишались тонкими.
"""

from __future__ import annotations

import torch

# Text-only reasoning-модель родини NVIDIA Nemotron, ~4B / ~8 GB BF16.
MODEL_ID = "nvidia/Llama-3.1-Nemotron-Nano-4B-v1.1"

# bf16 підтримується на MPS (macOS 14+). За помилок окремих операцій
# PYTORCH_ENABLE_MPS_FALLBACK (див. model.py) відправляє їх на CPU.
# Якщо саме bf16 капризує — поміняй на torch.float16.
DTYPE = torch.bfloat16

# Перемикання міркувань у родині Llama-Nemotron робиться СИСТЕМНИМ ПРОМПТОМ
# (не спецтокеном). Рядки мають бути дослівними.
THINK_ON = "detailed thinking on"
THINK_OFF = "detailed thinking off"

MAX_NEW_TOKENS = 1024

# Рекомендації картки NVIDIA: ON — семплінг; OFF — жадібне декодування.
GEN_THINK_ON: dict = {"do_sample": True, "temperature": 0.6, "top_p": 0.95}
GEN_THINK_OFF: dict = {"do_sample": False}


def pick_device() -> str:
    """Найкращий доступний бекенд: MPS на Mac, інакше CUDA, інакше CPU."""
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"
