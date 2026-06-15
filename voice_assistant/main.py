"""Entry point: record -> Groq STT -> process -> Groq TTS, in a loop.

Run from the project root:
    python -m voice_assistant.main
"""

from voice_assistant.audio import player, recorder
from voice_assistant.config import config
from voice_assistant.processor import commands, llm
from voice_assistant.stt import groq_stt
from voice_assistant.tts import groq_tts
from voice_assistant.utils.logger import get_logger

log = get_logger("voice_assistant")


def respond(text: str) -> None:
    """Speak a response, dispatching to whichever TTS engine is configured."""
    audio_path = groq_tts.synthesize(text)
    if audio_path:  # groq/gtts return a file; pyttsx3 speaks directly
        player.play(audio_path)


def run() -> None:
    config.validate()
    log.info("Голосовий асистент запущено (мова=%s). Скажіть 'вихід' для завершення.", config.language)
    respond("Вітаю! Чим можу допомогти?")

    while True:
        try:
            audio_path = recorder.listen()
            if not audio_path:  # VAD heard no speech
                continue

            text = groq_stt.transcribe(audio_path)
            if not text:
                continue

            if commands.is_exit_command(text):
                respond("До побачення!")
                break

            answer = commands.handle(text) or llm.process(text)
            respond(answer)

        except KeyboardInterrupt:
            log.info("Зупинено користувачем.")
            break
        except Exception as exc:  # keep the loop alive on transient errors
            log.error("Помилка в циклі: %s", exc)
            respond("Вибач, сталася помилка. Спробуй ще раз.")


if __name__ == "__main__":
    run()
