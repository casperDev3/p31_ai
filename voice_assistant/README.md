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
python -m voice_assistant.main
```

Скажи запит у мікрофон; для виходу — «вихід» / «стоп» / `Ctrl+C`.

## Тести

```bash
pytest voice_assistant/tests -q
```

## Структура

```
voice_assistant/
├── main.py            головний цикл
├── config.py          налаштування (.env)
├── groq_client.py     спільний Groq client
├── audio/             recorder + player
├── stt/groq_stt.py    Groq Whisper
├── processor/         commands + llm
├── tts/groq_tts.py    Groq PlayAI (+ gTTS/pyttsx3 фолбеки)
└── tests/
```

## Примітки

- **TTS за замовчуванням — `gtts`** (українська вимова), бо Groq Orpheus (`canopylabs/orpheus-v1-english`) озвучує лише англійською. Для англійського виводу постав `VA_TTS_ENGINE=groq` у `.env`. *(`playai-tts` виведено з ладу 2025-12-31.)*
- **Відтворення на macOS** — через вбудований `afplay` (грає WAV і MP3, без зайвих залежностей). На інших ОС — `simpleaudio` (WAV) / `playsound` (MP3).
- **VAD** (енергетичний, без зайвих залежностей) увімкнено за замовчуванням: підлаштовується під фоновий шум, чекає початку мовлення й зупиняє запис після ~0.8 с тиші. Вимкнути → `VA_VAD=0` (фіксовані `record_seconds`). Тюнінг: `VA_VAD`, `vad_silence_tail`, `vad_threshold_floor`/`vad_threshold_factor`, `vad_max_seconds` у `config.py`.
