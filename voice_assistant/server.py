"""FastAPI backend for the web (MUI) frontend.

Wraps the existing Groq pipeline: audio -> Groq Whisper -> command/LLM -> TTS.
The browser handles camera + microphone (so macOS camera permissions just work),
records a short clip, and POSTs it here.

Run:  python -m voice_assistant.server   (http://127.0.0.1:8000)
"""

import base64
import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from voice_assistant.config import config
from voice_assistant.processor import commands, llm
from voice_assistant.stt import groq_stt
from voice_assistant.tts import groq_tts
from voice_assistant.utils.logger import get_logger

log = get_logger("voice_assistant.server")

app = FastAPI(title="Voice Assistant API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Browser MediaRecorder mime -> file extension Groq Whisper understands.
_EXT = {
    "audio/webm": ".webm",
    "audio/ogg": ".ogg",
    "audio/mp4": ".mp4",
    "audio/mpeg": ".mp3",
    "audio/wav": ".wav",
    "audio/x-wav": ".wav",
}


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "language": config.language,
        "stt_model": config.stt_model,
        "llm_model": config.llm_model,
        "tts_engine": config.tts_engine,
        "key_configured": bool(config.groq_api_key),
    }


@app.post("/api/converse")
async def converse(audio: UploadFile = File(...)) -> dict:
    config.validate()
    data = await audio.read()
    ext = _EXT.get(audio.content_type or "", os.path.splitext(audio.filename or "")[1] or ".webm")

    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
        f.write(data)
        in_path = f.name

    try:
        text = groq_stt.transcribe(in_path)
        if not text:
            return {"user_text": "", "assistant_text": "", "audio": None, "end": False}

        end = commands.is_exit_command(text)
        if end:
            answer = "До побачення!"
        else:
            answer = commands.handle(text) or llm.process(text)

        out_path = tempfile.mktemp(suffix=".mp3")
        produced = groq_tts.synthesize(answer, out_path=out_path)
        audio_b64 = None
        mime = "audio/mpeg"
        if produced and os.path.exists(produced):
            mime = "audio/mpeg" if produced.endswith(".mp3") else "audio/wav"
            with open(produced, "rb") as af:
                audio_b64 = base64.b64encode(af.read()).decode()
            os.remove(produced)

        return {"user_text": text, "assistant_text": answer, "audio_mime": mime, "audio": audio_b64, "end": end}
    finally:
        try:
            os.remove(in_path)
        except OSError:
            pass


# Serve the built frontend (web/dist) if it exists — `npm run build` enables this.
_DIST = Path(__file__).resolve().parent / "web" / "dist"
if _DIST.exists():
    app.mount("/", StaticFiles(directory=str(_DIST), html=True), name="web")


def main() -> None:
    import uvicorn

    uvicorn.run("voice_assistant.server:app", host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
