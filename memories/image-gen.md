# image-gen

Інтерактивний CLI-генератор зображень на базі HuggingFace `diffusers` + Stable Diffusion. Єдиний Python-підпроєкт у репо (поряд з Angular-овим `pong-game/`).

## Запуск

```bash
cd image-gen
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python generate.py
```

Перший запуск завантажить ваги моделі (~6 GB) у `~/.cache/huggingface/`.

## Як працює

- `generate.py` — інтерактивний цикл: запитує промпт → кількість → кроків → генерує → зберігає у `output/`.
- Пристрій вибирається автоматично: CUDA → MPS (Apple Silicon) → CPU.
- Модель за замовчуванням: `stabilityai/sdxl-turbo` — швидка (1–4 кроки), `guidance_scale=0.0`, без негативного промпта. Якщо потрібна якість > швидкість, замінити `DEFAULT_MODEL` на `stabilityai/stable-diffusion-xl-base-1.0` і підняти `DEFAULT_STEPS` до 25–40, `DEFAULT_GUIDANCE` до 7.0.
- Імена файлів: `YYYYMMDD-HHMMSS_<slug-промпта>_<i>.png`.

## Файли

- `generate.py` — головний скрипт
- `requirements.txt` — torch, diffusers, transformers, accelerate, safetensors, Pillow
- `output/` — згенеровані зображення (в .gitignore)
- `.gitignore` — output/, .venv/, __pycache__/

## Чому не вписано у CLAUDE.md commands

`image-gen/` має власний venv і ваги моделей у користувацькому кеші — це не «загальна команда репо», а ізольований підпроєкт. Якщо стане другим Python-проєктом, варто додати окрему секцію у CLAUDE.md.
