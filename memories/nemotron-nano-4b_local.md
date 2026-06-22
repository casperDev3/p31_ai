# nemotron_nano_4b — локальний reasoning-чат (PyTorch)

Експеримент гілки `ai-libs-2206`: локальний інференс **`nvidia/Llama-3.1-Nemotron-Nano-4B-v1.1`**
на Apple Silicon через PyTorch+MPS. CLI-чат із перемиканням reasoning.

## Походження

Початковий запит був про `nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16`, але та модель
(31B, BF16 = 62 GB, мінімум H100 80GB, без MPS) фізично не запускається на M1 Pro / 16 GB.
Узгоджено замінити на меншу модель тієї ж родини NVIDIA Nemotron, що зберігає reasoning.
Повний розбір — `.docs/plans/nemotron-nano-4b_local-pytorch.md`.

## Що важливо знати перед редагуванням

- **Окремий venv на Python 3.13** (`nemotron_nano_4b/.venv`). Кореневий `.venv` репо = 3.14 → torch там
  не встановлюється. Запуск завжди з кореня репо як модуль: `python -m nemotron_nano_4b.chat`.
- **Reasoning = системний промпт**, не спецтокен: `detailed thinking on` / `detailed thinking off`
  (родина Llama-Nemotron). ON → семплінг `temperature=0.6, top_p=0.95`; OFF → `do_sample=False`. Це в `config.py`.
- **MPS-нюанси**: `DTYPE = torch.bfloat16`; `PYTORCH_ENABLE_MPS_FALLBACK=1` виставляється в `model.py`
  ДО завантаження torch-залежного коду. Якщо bf16 капризує — `torch.float16`.
- Ваги ~8 GB у `~/.cache/huggingface` (поза репо, у `.gitignore` не потрібні). Резидентно ~9–11 GB.

## Файли

- `config.py` — єдине місце для MODEL_ID, dtype, device, reasoning-промптів, дефолтів генерації.
- `model.py` — `load_model() -> (tokenizer, model, device)`.
- `chat.py` — REPL; команди `/think`, `/no_think`, `/reset`, `/exit`; стрімінг через `TextStreamer`.

Пов'язано: [[project_comparison_playground]], [[user_language]].
