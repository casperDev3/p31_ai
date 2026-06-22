"""Завантаження токенайзера й моделі на найкращий доступний пристрій.

Перший виклик load_model() тягне ваги (~8 GB) у HF-кеш (~/.cache/huggingface)
і тримає їх у пам'яті — на M1 Pro / 16 GB це ~9–11 GB резидентно.
"""

from __future__ import annotations

import os

# Має бути виставлено ДО ініціалізації MPS-бекенду: непідтримані на Metal
# операції падатимуть на CPU замість того, щоб кидати помилку.
os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402

from .config import DTYPE, MODEL_ID, pick_device


def load_model():
    """Повертає (tokenizer, model, device)."""
    device = pick_device()
    print(f"[nemotron] завантаження {MODEL_ID} → {device} ({DTYPE})…", flush=True)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    # transformers 5.x: аргумент називається `dtype` (старий `torch_dtype` лишений
    # лише для зворотної сумісності й кидає deprecation-попередження).
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        dtype=DTYPE,
        trust_remote_code=True,
        low_cpu_mem_usage=True,
    ).to(device)
    model.eval()

    print("[nemotron] готово.", flush=True)
    return tokenizer, model, device
