"""Завантаження GPT-2: токенайзер + модель на найкращому доступному пристрої.

Перший виклик тягне ~500 MB у HF-кеш (~/.cache/huggingface).
"""

from __future__ import annotations

import os

os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402

from .config import DTYPE, MODEL_ID, pick_device


def load_model():
    """Повертає (tokenizer, model, device)."""
    device = pick_device()
    print(f"[gpt2] завантаження {MODEL_ID} → {device} ({DTYPE})…", flush=True)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    # GPT-2 не має окремого pad-токена — використовуємо eos як pad.
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype=DTYPE).to(device)
    model.eval()

    print("[gpt2] готово.", flush=True)
    return tokenizer, model, device
