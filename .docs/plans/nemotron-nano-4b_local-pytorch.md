# План: локальний запуск NVIDIA Nemotron reasoning-моделі через PyTorch

## Контекст

Запит — запустити `nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16` локально через PyTorch.
Це **неможливо на цій машині** (Apple M1 Pro / 16 GB):

- 31B параметрів, BF16 = **62 GB ваг**, мінімум 1× H100 80GB; навіть NVFP4 (21 GB) не влазить у 16 GB.
- MoE не зменшує резидентної пам'яті — усі ваги мусять бути в RAM, активних ~3B лише на токен.
- Apple Silicon / MPS не підтримується (шлях — CUDA: vLLM / SGLang / transformers на NVIDIA).
- Кореневий `.venv` = Python 3.14, для якого ще немає wheel'ів PyTorch.

**Узгоджений напрям:** лишаємось локально, беремо меншу модель тієї ж родини, що зберігає reasoning:

> **`nvidia/Llama-3.1-Nemotron-Nano-4B-v1.1`** — text-only reasoning, ~4B / **~8 GB BF16**,
> `transformers >= 4.44.2`, `trust_remote_code=True`. Reasoning перемикається **системним промптом**
> `detailed thinking on` / `detailed thinking off` (ON → `temperature=0.6, top_p=0.95`; OFF → greedy).

## Середовище (перевірено)

- Apple M1 Pro, 16 GB unified RAM, ~92 GB вільного диску, macOS 26.5.
- Окремий venv на **python3.13** (`/opt/homebrew/bin/python3.13`) — кореневий 3.14 не чіпаємо.
- Ваги ~8 GB у HF-кеш (`~/.cache/huggingface`, поза репо).

## Артефакт

Пакет `nemotron_nano_4b/`, запуск як модуль із кореня: `python -m nemotron_nano_4b.chat`.

```
nemotron_nano_4b/
  __init__.py
  config.py          # MODEL_ID, DTYPE=bfloat16, pick_device(), reasoning-промпти, дефолти генерації
  model.py           # load_model() -> (tokenizer, model, device); PYTORCH_ENABLE_MPS_FALLBACK=1
  chat.py            # CLI-REPL: /think /no_think /reset /exit; apply_chat_template + generate + TextStreamer
  requirements.txt   # torch>=2.4, transformers>=4.44.2, accelerate, huggingface_hub[hf_xet], sentencepiece
  README.md
.gitignore           # .venv/, __pycache__, .DS_Store, .idea/, .env
```

## Setup

```bash
python3.13 -m venv nemotron_nano_4b/.venv
source nemotron_nano_4b/.venv/bin/activate
pip install -U pip
pip install -r nemotron_nano_4b/requirements.txt
huggingface-cli download nvidia/Llama-3.1-Nemotron-Nano-4B-v1.1   # опційно, з resume
python -m nemotron_nano_4b.chat
```

## Перевірка

1. `python -c "import torch; print(torch.backends.mps.is_available())"` → `True`.
2. `python -m nemotron_nano_4b.chat`; reasoning-задача в `/think` → відповідь з міркуваннями; `/no_think` → коротша.
3. Пам'ять процесу в межах 16 GB (очікувано ~9–11 GB).

## Ризики / запасні варіанти

- bf16 на MPS капризує → `DTYPE = torch.float16` у `config.py` (fallback на CPU вже ввімкнено).
- Тісно по пам'яті → зменшити `MAX_NEW_TOKENS`, закрити важкі застосунки.
- Немає torch-wheel для 3.13 → відкотитись на `python3.11` тим самим `requirements.txt`.
