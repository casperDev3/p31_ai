# GPT-2 — локальна генерація тексту (PyTorch)

Локальний інференс **`openai-community/gpt2`** на PyTorch+MPS.

> **Увага: це не чат.** GPT-2 — *базова* мовна модель (124M, ~500 MB) без інструкцій, чату й reasoning.
> Вона **продовжує** введений текст, а не відповідає на питання. Введи початок речення —
> отримаєш його продовження. Це навмисний контраст до `nemotron_nano_4b/` (instruct + reasoning).

## Запуск

GPT-2 потребує лише `torch` + `transformers` — вони вже стоять у venv від `nemotron_nano_4b`,
тож **окремий venv не потрібен**, перевикористовуємо існуючий:

```bash
cd /Users/a1d/Desktop/Teach/p31_ai
source nemotron_nano_4b/.venv/bin/activate
python -m gpt2_local.generate
```

Перший запуск тягне ~500 MB у HF-кеш (`~/.cache/huggingface`); далі — миттєво.

### Приклад

```
prompt> Once upon a time
Once upon a time, there was a small village by the sea where...
```

Команда `/exit` — вихід.

## Налаштування

Усе в `config.py`: `MAX_NEW_TOKENS`, семплінг (`temperature`, `top_p`, `top_k`) і
анти-повторення (`repetition_penalty`, `no_repeat_ngram_size` — GPT-2 без них схильна зациклюватись).
GPT-2 має контекст лише **1024 токени**.

## Структура

```
gpt2_local/
  config.py     # MODEL_ID, dtype, device, дефолти генерації
  model.py      # load_model() -> (tokenizer, model, device); pad=eos
  generate.py   # CLI text-completion REPL
```
