# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

`p31_ai` — a teaching/comparison playground for AI-assisted coding. Each subdirectory is an independent artifact produced by a different tool (Claude, Gemini CLI, Cursor, Antigravity, Tour Agent Maker, etc.). The goal is side-by-side comparison of how different AI tools tackle the same brief, not a unified application.

There is **no top-level build system**. Each project stands on its own.

## Layout

| Path | What | Build? |
|------|------|--------|
| `pong-game/` | Angular 21 CLI app — full Pong implementation with signals | yes (`npm` in that dir) |
| `games/*.html` | Three Doodle Jump variants, one per AI tool (filename suffix = tool) | no — open in browser |
| `landings/*.html` | Two personal portfolio landings (antigravity vs. cursor) | no — open in browser |
| `exp/atoms.html` | Loose canvas experiment | no — open in browser |
| `memories/` | Per-project detail notes — read these before deep work | n/a |

Filename convention for generated samples: `<topic>_<tool>.html` (e.g. `doodle-jump_gemini-cli.html`). Follow this when adding new samples so it stays clear what produced what.

## Per-project detail notes

Detail lives in `memories/` — read the relevant file before non-trivial work on a project.

- `memories/pong-game.md` — Angular 21 Pong (signals, standalone components, the only real build)
- `memories/doodle-jump_claude-opus-4-7.md` — Doodle Jump, Claude Opus 4.7 variant
- `memories/doodle-jump_gemini-cli.md` — Doodle Jump, Gemini CLI variant (leanest)
- `memories/doodle-jump_tour-agent-maker.md` — Doodle Jump, Tour Agent Maker variant
- `memories/antigravity-landing.md` — Antigravity-generated portfolio landing
- `memories/cursor-landing.md` — Cursor-generated portfolio landing
- `memories/atoms.md` — `exp/atoms.html` particle experiment

## Common commands

The only project with a build is `pong-game/`. Run from inside that directory:

```bash
cd pong-game
npm install                          # first-time setup
npm start                            # ng serve → http://localhost:4200
npm run build                        # production build → dist/
npm run watch                        # dev watch build
npx ng generate component <name>     # scaffold (inline template+style, SCSS, no tests)
```

There are **no tests configured** in `pong-game/` — `skipTests: true` is set for all schematics in `angular.json`.

For everything in `games/`, `landings/`, and `exp/`: open the `.html` file directly (`open path/to/file.html` on macOS). No bundler, no install step, no shared modules across files.

## Working principles for this repo

- **Don't cross-pollinate variants.** Each generated sample is meant to preserve what its source tool produced — when editing one Doodle Jump variant, don't refactor it to match another. The comparison value depends on each variant staying authored by its source tool.
- **No shared module/CSS to extract.** Inline styling in the HTML samples is deliberate, not tech debt.
- **`pong-game/` is the only place to add Angular-style patterns.** The HTML samples are intentionally framework-free.
- When adding a new sample, follow `<topic>_<tool>.html` naming, put it in the right folder (`games/`, `landings/`, or `exp/`), and add a matching `memories/<name>.md` note.
