# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

`p31_ai` is a teaching/comparison playground for AI-assisted coding — **not a single application**. Its defining structure is **branch-per-experiment**: each git branch holds one self-contained brief built (often by a different AI tool), so the same problem can be compared side by side across tools/models. There is no top-level build system; each experiment stands on its own.

Run `git branch -a` to see the experiments. Examples of prior ones (each on its own branch, with its own tailored `CLAUDE.md`):

- `main` / `*-2805` / `*-2006` — Angular `pong-game/`, standalone HTML `games/`, `landings/`, `exp/`
- `detection_and_face_id_1302` — `detection_face_id_claude/` (OpenCV + YOLO + InsightFace, PySide6 dashboard)
- `text-speach-1506` — `voice_assistant/` (Groq Whisper → LLM → TTS; CLI, FastAPI web, PySide6 GUI)
- `stable-difusion-0806` / `perserptron-1206` — `image-gen/` (diffusers/SDXL), `exp/perceptron_*`

**Do not merge experiments together or port code between branches** — the comparison value depends on each branch staying as its source tool produced it.

## Current branch (`ai-libs-2206`)

This branch is a **fresh start**: tracked content is only `README.md`, `.gitattributes`, `.idea/`. No experiment code exists yet — you are expected to create it here.

What's pre-provisioned: a Python 3.14 virtualenv at `.venv/` (Homebrew python). It is **not** a clean install — it carries the cumulative deps of the Python experiments. Already installed (no `pip install` needed for these):

- `groq` (LLM/Whisper/TTS client), `python-dotenv`, `httpx`, `requests`, `pydantic`
- `sounddevice`, `simpleaudio`, `numpy` (audio I/O)
- `gTTS` (Ukrainian TTS)
- `fastapi`, `uvicorn`, `python-multipart` (web backend)
- `PySide6` (Qt desktop GUI), `opencv-python` / `cv2` (camera/vision)

Heavy ML libs are **not** here (`torch`, `diffusers`, `ultralytics`, `insightface`, `onnxruntime`) — install per experiment if needed.

## Working with the Python venv

```bash
source .venv/bin/activate          # always activate first
python -m <experiment_pkg>.main    # run experiments as modules FROM REPO ROOT, not by file path
```

- Experiments are Python **packages** (have `__init__.py`) run with `python -m pkg.module` from the repo root — relative paths and imports assume that CWD.
- Groq-based code reads `GROQ_API_KEY` from a `.env` file (key from console.groq.com/keys). Copy a `.env.example` to `.env`; `.env` is never committed.
- Add an experiment-local `requirements.txt` for anything beyond the venv's current set; on macOS, `sounddevice`/`simpleaudio` need `brew install portaudio`.

## Conventions to follow when adding work

These hold across the playground — match them on this branch:

- **Planning docs** live in `.docs/`: `plans/` (design before building), `qa/` (review notes), `report/` (comparison write-ups). One `.md` per audited unit.
- **`memories/`** holds one detail note per artifact — write one for each non-trivial thing you build, and read the matching note before editing an existing artifact.
- **Naming for generated samples:** `<topic>_<tool-or-model>.html` (e.g. `doodle-jump_gemini-cli.html`, `pacman_claude-opus-4-8.html`) so it's clear what produced what.
- **Docs and READMEs are written in Ukrainian** in this repo; code, identifiers, and paths stay in English.
- Standalone HTML samples are intentionally framework-free and self-contained — don't extract shared modules/CSS across them.
