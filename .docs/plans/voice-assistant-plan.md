# План створення голосового асистента на Python (Groq API)

> Програма: захоплення голосу → перетворення в текст (STT) → обробка запиту (LLM) → озвучення результату (TTS).
> Увесь «розумний» конвеєр працює через **Groq API** (Whisper + LLM + PlayAI TTS).

---

## ⚠️ Безпека ключа

- API-ключ **ніколи** не зберігається в коді чи в цьому файлі.
- Ключ кладемо в `.env`: `GROQ_API_KEY=...`, файл додаємо в `.gitignore`.
- Якщо ключ було показано публічно (чат, скріншот, репозиторій) — **негайно відкликати й перевипустити** на https://console.groq.com/keys.

---

## 1. Мета та обсяг

Створити настільний застосунок на Python, який:

1. **Слухає** мікрофон і записує мовлення користувача.
2. **Перетворює** аудіо в текст через **Groq Whisper** (STT).
3. **Обробляє** запит через **Groq LLM** (команди / питання).
4. **Озвучує** відповідь через **Groq PlayAI TTS**.

Цільовий сценарій: локальний голосовий помічник у циклі «питання — відповідь» з підтримкою української та англійської мов. Запис аудіо й відтворення — локальні; розпізнавання, обробка та синтез — у хмарі Groq (швидкий inference).

---

## 2. Архітектура

Конвеєр із чотирьох модулів. Запис/відтворення — локально, три центральні етапи — через Groq:

```
┌──────────┐  audio   ┌─────────────┐  text  ┌─────────────┐  text  ┌─────────────┐  audio
│  Mic /   │ ───────▶ │ Groq Whisper│ ─────▶ │  Groq LLM   │ ─────▶ │ Groq PlayAI │ ───────▶ Speaker
│ Recorder │          │   (STT)     │        │ (processor) │        │   (TTS)     │
└──────────┘          └─────────────┘        └─────────────┘        └─────────────┘
                              └──────────── один Groq client ───────────────┘
```

### Структура каталогів

```
voice_assistant/
├── main.py                 # точка входу, головний цикл
├── config.py               # налаштування (мова, моделі, ключ із .env)
├── .env                    # GROQ_API_KEY=...  (в .gitignore!)
├── .env.example            # шаблон без секретів
├── groq_client.py          # єдиний інстанс groq.Groq()
├── audio/
│   ├── recorder.py         # захоплення з мікрофона (+ VAD)
│   └── player.py           # відтворення аудіо-відповіді
├── stt/
│   └── groq_stt.py         # Groq Whisper transcribe
├── tts/
│   └── groq_tts.py         # Groq PlayAI synthesize
├── processor/
│   ├── commands.py         # прості локальні команди (час, вихід)
│   └── llm.py              # Groq chat completion
├── utils/
│   └── logger.py
├── requirements.txt
└── tests/
```

---

## 3. Технологічний стек

| Етап | Інструмент | Модель / бібліотека |
|------|-----------|--------------------|
| Запис аудіо | `sounddevice` + `numpy` | локально, WAV 16 kHz mono |
| Детекція мовлення | `webrtcvad` | визначення кінця фрази (VAD) |
| **STT** | **Groq API** | `whisper-large-v3` (точність) або `whisper-large-v3-turbo` (швидкість) |
| **Обробка / LLM** | **Groq API** | `llama-3.3-70b-versatile` (якість) або `llama-3.1-8b-instant` (швидкість) |
| **TTS (укр.)** | **gTTS** (дефолт) | `gTTS(lang='uk')` — Groq Orpheus української не вміє |
| **TTS (англ.)** | **Groq API** | `canopylabs/orpheus-v1-english`, голоси `troy`/`hannah`/`austin` |
| Відтворення | `afplay` (macOS) / `simpleaudio`+`playsound` | WAV і MP3 |
| Секрети / конфіг | `python-dotenv` | читання `GROQ_API_KEY` з `.env` |
| Клієнт Groq | `groq` (офіційний SDK) | `from groq import Groq` |

> **Примітка щодо української TTS:** Groq Orpheus (`canopylabs/orpheus-v1-english`) озвучує лише англійською/арабською, тому для української за замовчуванням використовуємо `gTTS(lang='uk')`. STT (Whisper) і LLM працюють з українською без проблем. *(Стара модель `playai-tts` виведена з ладу 2025-12-31 — замінена на Orpheus.)*

---

## 4. Етапи реалізації

### Етап 1 — Каркас та оточення
- [ ] Віртуальне середовище: `python -m venv .venv`.
- [ ] `requirements.txt` + встановлення залежностей.
- [ ] `.env` з `GROQ_API_KEY`, `.env.example` без секрету, додати `.env` у `.gitignore`.
- [ ] `groq_client.py` — єдиний `Groq(api_key=os.environ["GROQ_API_KEY"])`.
- [ ] `config.py` — мова, назви моделей, голос TTS, шляхи.
- [ ] Логування (`utils/logger.py`).

### Етап 2 — Захоплення аудіо (`audio/recorder.py`)
- [ ] Запис фіксованої тривалості (MVP, напр. 5 с) у WAV 16 kHz mono.
- [ ] Додати VAD (`webrtcvad`) — авто-визначення кінця фрази.
- [ ] (Опціонально) wake word.

### Етап 3 — STT через Groq (`stt/groq_stt.py`)
- [ ] `transcribe(path) -> str` через `client.audio.transcriptions.create(...)`.
- [ ] Параметри: `model="whisper-large-v3"`, `language="uk"` (або авто).
- [ ] Обробка порожнього/невпевненого результату.

### Етап 4 — Обробка (`processor/`)
- [ ] `commands.py` — локальні правила: час, дата, «стоп/вихід».
- [ ] `llm.py` — `client.chat.completions.create(...)` з system-промптом
      «Ти голосовий асистент, відповідай коротко українською».
- [ ] Маршрутизація: спершу локальні команди, інакше — LLM.
- [ ] (Опціонально) пам'ять контексту: тримати історію `messages`.

### Етап 5 — TTS через Groq (`tts/groq_tts.py`)
- [ ] `speak(text)` через `client.audio.speech.create(...)`,
      `model="playai-tts"`, `voice=...`, `response_format="wav"`.
- [ ] Зберегти у файл і відтворити через `player.py`.
- [ ] Фолбек на `gTTS`/`pyttsx3` для української за потреби.

### Етап 6 — Головний цикл (`main.py`)
- [ ] Конвеєр: record → STT → process → TTS.
- [ ] Цикл «слухати → відповідати» з командою виходу.
- [ ] Обробка помилок: порожнє розпізнавання, мережа, ліміти Groq (429), таймаут.

### Етап 7 — Якість і UX
- [ ] Тести (`tests/`) з mock відповідей Groq (без реальних викликів).
- [ ] (Опціонально) GUI (`tkinter`/`PyQt`) з кнопкою «Говорити».
- [ ] Індикація стану: слухаю / думаю / говорю.

---

## 5. Псевдокод

### Ініціалізація клієнта (`groq_client.py`)
```python
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.environ["GROQ_API_KEY"])  # ключ лише з .env
```

### STT (`stt/groq_stt.py`)
```python
def transcribe(path: str, language: str = "uk") -> str:
    with open(path, "rb") as f:
        result = client.audio.transcriptions.create(
            file=(path, f.read()),
            model="whisper-large-v3",
            language=language,
        )
    return result.text.strip()
```

### LLM (`processor/llm.py`)
```python
def process(text: str) -> str:
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Ти голосовий асистент. Відповідай коротко українською."},
            {"role": "user", "content": text},
        ],
        temperature=0.6,
    )
    return resp.choices[0].message.content
```

### TTS (`tts/groq_tts.py`)
```python
# Дефолт для української — gTTS (Groq Orpheus лише англ./араб.):
def synthesize_gtts(text: str, out_path: str = "answer.mp3") -> str:
    from gtts import gTTS
    gTTS(text=text, lang="uk").save(out_path)
    return out_path

# Англійський варіант через Groq Orpheus:
def synthesize_groq(text: str, out_path: str = "answer.wav") -> str:
    audio = client.audio.speech.create(
        model="canopylabs/orpheus-v1-english",
        voice="troy",
        input=text,
        response_format="wav",
    )
    audio.write_to_file(out_path)
    return out_path
```

### Головний цикл (`main.py`)
```python
def run():
    tts.speak("Вітаю! Чим можу допомогти?")
    while True:
        audio_path = recorder.listen()        # запис з мікрофона
        text = stt.transcribe(audio_path)     # Groq Whisper
        if not text:
            continue
        if is_exit_command(text):
            tts.speak("До побачення!")
            break
        answer = commands.handle(text) or llm.process(text)  # команда або LLM
        player.play(tts.speak(answer))        # Groq TTS -> відтворення
```

---

## 6. requirements.txt (чернетка)

```
groq
python-dotenv
sounddevice
numpy
webrtcvad
simpleaudio
gTTS         # фолбек української TTS (опціонально)
pyttsx3      # офлайн фолбек TTS (опціонально)
```

---

## 7. .env.example

```
# Скопіюй у .env і встав свій ключ. .env НЕ комітити!
GROQ_API_KEY=your_groq_api_key_here
```

---

## 8. Ризики та рішення

| Ризик | Рішення |
|-------|---------|
| Скомпрометований ключ | зберігати лише в `.env`, відкликати при витоку, ротація |
| Залежність від інтернету | Groq лише online; за потреби — офлайн-фолбек (faster-whisper + pyttsx3) |
| Українська вимова в Groq TTS | фолбек `gTTS(lang='uk')` / `pyttsx3` |
| Ліміти / 429 від Groq | backoff + повтор, вибір швидших/легших моделей |
| Затримка відповіді LLM | стрімінг (`stream=True`), модель `llama-3.1-8b-instant` |
| Шум мікрофона | VAD + нормалізація гучності, поріг енергії |
| Приватність аудіо | попередити, що аудіо йде в хмару Groq; не надсилати без згоди |

---

## 9. Критерії готовності (MVP)

- ✅ Програма запускається і слухає мікрофон.
- ✅ Groq Whisper розпізнає українське/англійське мовлення в текст.
- ✅ Відповідає на базові команди (час, дата, вихід) і вільні питання через Groq LLM.
- ✅ Groq PlayAI (або фолбек) озвучує відповідь уголос.
- ✅ Працює в циклі до команди «вихід».
- ✅ Ключ читається з `.env`, не присутній у коді/репозиторії.

### Подальший розвиток
- Wake word («Привіт, асистенте»).
- Стрімінг LLM + інкрементальний TTS для меншої затримки.
- Пам'ять контексту розмови (історія `messages`).
- GUI з візуалізацією стану.
- Плагіни (погода, нагадування, керування системою).
```
