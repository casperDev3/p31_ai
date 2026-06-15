# Voice Assistant (Groq API)

Голосовий асистент: мікрофон → **Groq Whisper** (STT) → **Groq LLM** → **Groq PlayAI** (TTS).

План: [`.docs/plans/voice-assistant-plan.md`](../.docs/plans/voice-assistant-plan.md)

## Встановлення

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r voice_assistant/requirements.txt
```

> macOS: для `sounddevice`/`simpleaudio` потрібен PortAudio — `brew install portaudio`.

## Налаштування

```bash
cp voice_assistant/.env.example voice_assistant/.env
# відкрий .env і встав GROQ_API_KEY
```

Ключ беруть із [console.groq.com/keys](https://console.groq.com/keys). `.env` **не комітиться**.

## Запуск

З кореня проєкту (`p31_ai`):

```bash
python -m voice_assistant.main      # CLI (голос у терміналі)
python -m voice_assistant.server    # веб-інтерфейс MUI (рекомендовано)
python -m voice_assistant.gui       # десктоп GUI (PySide6, опціонально)
```

Скажи запит у мікрофон; для виходу — «вихід» / «стоп» / `Ctrl+C`.

### Веб-інтерфейс на MUI (рекомендовано)

React + Material UI: **камера** через браузер (`getUserMedia` — дозвіл питається
нативно, без проблем macOS), **графіки** звуку (форма хвилі + частотний спектр через
MUI X Charts), **чат** із транскрипцією та озвучення відповіді.

**Варіант А — одним сервером (потрібен лише Python):**
```bash
npm install --prefix voice_assistant/web   # один раз
npm run build --prefix voice_assistant/web # збирає web/dist
python -m voice_assistant.server           # відкрий http://127.0.0.1:8000
```

**Варіант Б — режим розробки (два процеси, гарячий релоад):**
```bash
python -m voice_assistant.server                 # бекенд :8000
npm run dev --prefix voice_assistant/web         # фронтенд :5173 (проксі /api -> :8000)
```
Відкрий http://127.0.0.1:5173 → **Старт** → дозволь камеру/мікрофон → **Говорити**.

### Графічний інтерфейс (`python -m voice_assistant.gui`)

Вікно показує: **вебкамеру**, **транскрипцію діалогу** (бульбашки «Ви»/«Асистент»),
**живу візуалізацію звукових хвиль** і поточний стан (Слухаю / Думаю / Говорю).
Натисни **▶ Старт**. Колір хвилі змінюється за станом.

> macOS попросить дозвіл на **камеру** і **мікрофон** при першому запуску
> (System Settings → Privacy & Security). Якщо запускаєш із терміналу — дозвіл
> питатиметься для термінала. Камеру можна змінити через `VA_CAMERA=1`.

## Тести

```bash
pytest voice_assistant/tests -q
```

## Структура

```
voice_assistant/
├── main.py            CLI головний цикл
├── config.py          налаштування (.env)
├── groq_client.py     спільний Groq client
├── audio/             recorder + player + vad (VADSegmenter)
├── stt/groq_stt.py    Groq Whisper
├── processor/         commands + llm
├── tts/groq_tts.py    Groq Orpheus (+ gTTS/pyttsx3 фолбеки)
├── server.py          FastAPI бекенд для веб-інтерфейсу
├── web/               React + MUI фронтенд (камера, графіки, чат)
├── gui/               PySide6 десктоп (app + threads + widgets)
└── tests/
```

## Примітки

- **TTS за замовчуванням — `gtts`** (українська вимова), бо Groq Orpheus (`canopylabs/orpheus-v1-english`) озвучує лише англійською. Для англійського виводу постав `VA_TTS_ENGINE=groq` у `.env`. *(`playai-tts` виведено з ладу 2025-12-31.)*
- **Відтворення на macOS** — через вбудований `afplay` (грає WAV і MP3, без зайвих залежностей). На інших ОС — `simpleaudio` (WAV) / `playsound` (MP3).
- **VAD** (енергетичний, без зайвих залежностей) увімкнено за замовчуванням: підлаштовується під фоновий шум, чекає початку мовлення й зупиняє запис після ~0.8 с тиші. Вимкнути → `VA_VAD=0` (фіксовані `record_seconds`). Тюнінг: `VA_VAD`, `vad_silence_tail`, `vad_threshold_floor`/`vad_threshold_factor`, `vad_max_seconds` у `config.py`.
