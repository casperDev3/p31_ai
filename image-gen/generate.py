"""Інтерактивний генератор зображень на основі Stable Diffusion (diffusers).

Запуск:
    python generate.py

Підтримує Apple Silicon (MPS), CUDA та CPU. Зображення зберігаються у ./output/.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import torch
from diffusers import AutoPipelineForText2Image


OUTPUT_DIR = Path(__file__).parent / "output"
DEFAULT_MODEL = "stabilityai/sdxl-turbo"
DEFAULT_STEPS = 2
DEFAULT_GUIDANCE = 0.0


def pick_device() -> tuple[str, torch.dtype]:
    if torch.cuda.is_available():
        return "cuda", torch.float16
    if torch.backends.mps.is_available():
        return "mps", torch.float16
    return "cpu", torch.float32


def slugify(text: str, max_len: int = 40) -> str:
    keep = "abcdefghijklmnopqrstuvwxyz0123456789-_"
    s = "".join(c if c in keep else "-" for c in text.lower().strip())
    while "--" in s:
        s = s.replace("--", "-")
    return s.strip("-")[:max_len] or "image"


def ask_int(label: str, default: int) -> int:
    raw = input(f"{label} [{default}]: ").strip()
    if not raw:
        return default
    try:
        return max(1, int(raw))
    except ValueError:
        print(f"  ! не число, використовую {default}")
        return default


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    device, dtype = pick_device()
    print(f"Пристрій: {device} ({dtype})")
    print(f"Завантажую модель: {DEFAULT_MODEL} (перший запуск завантажить ваги ~6 GB)")

    pipe = AutoPipelineForText2Image.from_pretrained(
        DEFAULT_MODEL,
        torch_dtype=dtype,
        variant="fp16" if dtype == torch.float16 else None,
    ).to(device)

    if device == "mps":
        pipe.enable_attention_slicing()

    print(f"Готово. Зображення зберігатимуться у: {OUTPUT_DIR}")
    print("Введіть промпт (порожній рядок або 'exit' — вихід).\n")

    while True:
        try:
            prompt = input("prompt> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not prompt or prompt.lower() in {"exit", "quit", "q"}:
            break

        count = ask_int("  скільки зображень", 1)
        steps = ask_int("  кроків (inference steps)", DEFAULT_STEPS)

        for i in range(count):
            print(f"  → генерую {i + 1}/{count}...")
            image = pipe(
                prompt=prompt,
                num_inference_steps=steps,
                guidance_scale=DEFAULT_GUIDANCE,
            ).images[0]

            ts = datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"{ts}_{slugify(prompt)}_{i + 1}.png"
            path = OUTPUT_DIR / filename
            image.save(path)
            print(f"    збережено: {path.relative_to(Path.cwd()) if path.is_relative_to(Path.cwd()) else path}")

        print()

    print("Бувай.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
 