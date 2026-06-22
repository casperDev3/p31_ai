# Nemotron-Nano-4B — локальний reasoning-чат (PyTorch)

Локальний інференс **`nvidia/Llama-3.1-Nemotron-Nano-4B-v1.1`** на Apple Silicon через PyTorch+MPS.
Text-only reasoning-модель родини NVIDIA Nemotron, ~4B / **~8 GB BF16** — комфортно влазить у 16 GB.

> **Чому не `Nemotron-3-Nano-Omni-30B`?** Вихідна 30B-Omni модель потребує BF16 = 62 GB ваг і
> мінімум H100 80GB, без підтримки MPS — на M1 Pro / 16 GB не запускається. Тут — менша модель тієї ж
> родини, що зберігає reasoning. Деталі рішення: [`.docs/plans/nemotron-nano-4b_local-pytorch.md`](../.docs/plans/nemotron-nano-4b_local-pytorch.md).

## Встановлення

Потрібен **окремий venv на Python 3.13** — кореневий `.venv` репозиторію має Python 3.14, для якого
ще немає wheel'ів PyTorch.

```bash
python3.13 -m venv nemotron_nano_4b/.venv
source nemotron_nano_4b/.venv/bin/activate
pip install -U pip
pip install -r nemotron_nano_4b/requirements.txt
```

(Опційно) попередньо завантажити ваги ~8 GB із відновленням:

```bash
huggingface-cli download nvidia/Llama-3.1-Nemotron-Nano-4B-v1.1
```

## Запуск

З кореня репозиторію (`p31_ai`), з активованим venv:

```bash
python -m nemotron_nano_4b.chat
```

Перший запуск тягне ваги у HF-кеш (`~/.cache/huggingface`). Далі — миттєво.

### Команди в діалозі

| Команда     | Дія                                                            |
|-------------|----------------------------------------------------------------|
| `/think`    | міркування **ON** (`detailed thinking on`, семплінг 0.6/0.95)  |
| `/no_think` | міркування **OFF** (жадібне декодування)                       |
| `/reset`    | очистити історію діалогу                                       |
| `/exit`     | вихід                                                          |

Перемикання reasoning у цій родині — через **системний промпт** `detailed thinking on/off`,
а не спецтокен; це інкапсульовано в `config.py` і `chat.py`.

## Нотатки про пам'ять / продуктивність

- Ваги ~8 GB + KV-кеш; перед запуском варто закрити важкі застосунки. Очікувано ~9–11 GB резидентно.
- **Швидкість (перевірено на M1 Pro / MPS):** ~2–3 tok/s у reasoning-режимі; перша генерація має ~10 с
  прогріву (компіляція MPS-ядер), далі швидше. Завантаження ваг ~8 GB — одноразово (~5 хв).
- `DTYPE = torch.bfloat16` (MPS, macOS 14+). Якщо bf16-операції капризують — змінити на `torch.float16` у `config.py`.
- `PYTORCH_ENABLE_MPS_FALLBACK=1` (виставляється в `model.py`) відправляє непідтримані на Metal операції на CPU.
- Довгі ланцюжки міркувань — обмежуються `MAX_NEW_TOKENS` у `config.py`.

## Структура

```
nemotron_nano_4b/
  config.py    # MODEL_ID, dtype, device, reasoning-промпти, дефолти генерації
  model.py     # load_model() -> (tokenizer, model, device)
  chat.py      # CLI-REPL із перемиканням reasoning
  requirements.txt
```
