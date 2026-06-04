# Doodle Jump variants — QA & fix-plan report

**Date:** 2026-06-04
**Scope:** three AI-generated Doodle Jump clones in `games/`
**Method:** static code review (no runtime testing)
**Inputs:** [`.docs/qa/`](../qa/) (per-variant audits) and [`.docs/plans/`](../plans/) (per-variant fix plans)

---

## TL;DR

| Variant | LOC | Critical | Major | Medium | Minor | Total | Fix effort |
|---|---:|---:|---:|---:|---:|---:|---|
| **gemini-cli** | 923 | 0 | 5 | 6 | 5 | 16 | ~1 h |
| **claude-opus-4-7** | 1,436 | 0 | 4 (1 retracted) | 7 | 7 | 18 | ~1 h |
| **tour-agent-maker** | 1,063 | 0 | 5 | 7 | 7 | 19 | ~1 h |

None of the three has a Critical bug — all are playable on the golden path. Most Major findings are gameplay-correctness or resource-leak issues that surface after the first round (pause/resume, music, resize, multi-touch).

---

## Highest-impact bugs per variant

| Variant | Bug to fix first | Symptom | Effort |
|---|---|---|---|
| **gemini-cli** | M1 — double `requestAnimationFrame` after resume | Game runs at 2× speed after first pause | 10 min |
| **claude-opus-4-7** | M1 — music never stops on Quit-to-Menu | `setInterval` runs for rest of session | 5 min |
| **tour-agent-maker** | M1 — dead `endGame`/`saveScore` duplicates `gameOver` | Future edits silently disagree on persisted score | 10 min |

---

## Patterns shared across all three

These came up in more than one variant and are worth knowing as a class:

1. **Mid-game resize is broken everywhere.**
   - gemini-cli M2, tour-agent-maker M3 — world coordinates stale after viewport change.
   - claude-opus is the only variant that sidesteps this — by fixing the canvas to 400×600 and scaling via CSS. That design decision pays off.

2. **`roundRect` polyfill missing.**
   - gemini-cli m1, claude-opus m3 — break on pre-Safari-16. Three-line polyfill fixes both.

3. **`localStorage` parsing without `try/catch`.**
   - gemini-cli M4 (crash) — most severe.
   - tour-agent-maker has it right (try/catch everywhere) — only variant that defends against corrupt storage out of the box.
   - claude-opus mostly defended (`|| '[]'` fallbacks), one bare `+localStorage.getItem(...)` for `dj_high` which is safe (`+null === 0`).

4. **Accessibility is uniformly poor.**
   - Toggle UIs use `<div>` with click handlers; no ARIA, no keyboard focus.
   - Only claude-opus has this on the audit list (m2); the other two have similar gaps but they weren't called out separately.

5. **Tilt permission flow is iOS-fragile.**
   - claude-opus m7 (requested even when feature off).
   - tour-agent-maker M5 (no recovery after denial).

---

## Per-variant feature & quality comparison

| Aspect | gemini-cli | claude-opus-4-7 | tour-agent-maker |
|---|---|---|---|
| Implementation size | 923 LOC | 1,436 LOC | 1,063 LOC |
| Resize handling | broken (M2) | sidestepped via fixed canvas | broken (M3) |
| Pause behavior | broken (M1) | leaks music (M1) | clean |
| Storage resilience | crashes on bad data (M4) | mostly defended | defended (try/catch) |
| Skins | none | bunny / alien / ninja | bunny / alien / ninja |
| Themes | none | day / night / space / jungle | day / night / space / jungle |
| Achievements | none | 8 with persistence + toasts | 3 |
| Music | none | 8-note triangle loop | simple beat |
| Particle pool | no | yes | yes |
| Powerup timer UI | no | yes | no |
| Stompable monsters | yes | yes (+score popup) | no (monster = death) |
| Black hole | yes | yes (with rocket bug, M4) | yes (visual/hitbox mismatch m4) |
| UFOs / projectiles | no | yes | yes |
| Input model | keyboard + touch zones | keyboard + touch + tilt | keyboard + touch + swipe + tilt |
| Design system | inline ad-hoc | inline ad-hoc | CSS custom properties (`--ink`, `--accent`, etc.) |
| DPR-aware canvas | no | n/a (CSS scaling) | yes |
| Code organization | top-level functions | IIFE, namespaced | IIFE, namespaced, more helpers |
| `localStorage` namespacing | flat (`doodle_*`) | flat (`dj_*`) | versioned (`doodle_tour_*_v1`) |

---

## Who "won" the comparison

A subjective read; the value of this playground is the data, not the verdict.

- **Best to ship as-is:** claude-opus-4-7 — most features, fewest gameplay-breaking bugs once M1 is fixed.
- **Best baseline for teaching/reading:** gemini-cli — small enough to read top-to-bottom in 15 minutes, but has the most acute bug (M1 double-loop) and the only crash-on-corrupt-storage failure.
- **Best engineering hygiene:** tour-agent-maker — design tokens, try/catch around storage, DPR scaling, versioned storage keys. Loses points for the dead-code path (M1) and the broken time-based achievement (M2).

These verdicts ignore visual taste, which the per-project notes in `memories/` already cover.

---

## Recommended fix order across the repo

If treating all three as a single backlog:

1. **gemini-cli M1** (10 min) — most acute symptom (2× game speed after pause).
2. **gemini-cli M4** (2 min) — only crash-on-load failure in the repo.
3. **claude-opus M1** (5 min) — eliminates session-long resource leak.
4. **tour-agent-maker M1** (10 min) — removes dead code, single source of truth for scoring.
5. **tour-agent-maker M2** (10 min) — restores correctness of `s60` achievement.
6. **gemini-cli M2 / tour-agent-maker M3** (15–20 min each) — pick one resize strategy per file.
7. Everything else as time allows.

Total Major-class fixes: **~1.5 hours of focused work**.

---

## Out of scope (intentionally not fixed)

Per the repo's `CLAUDE.md` and the `project-comparison-playground` memory:

- **Do not** unify the three variants into a shared module or extract common logic. The comparison value depends on each variant staying authored by its source tool.
- **Do not** port features between variants (e.g. add achievements to gemini-cli). Each variant should remain recognizably what its source tool produced.
- Inline HTML/CSS/JS is deliberate; "extract to file" is not a valid finding here.

---

## Files referenced

- QA reports: [`.docs/qa/doodle-jump_gemini-cli.md`](../qa/doodle-jump_gemini-cli.md), [`.docs/qa/doodle-jump_claude-opus-4-7.md`](../qa/doodle-jump_claude-opus-4-7.md), [`.docs/qa/doodle-jump_tour-agent-maker.md`](../qa/doodle-jump_tour-agent-maker.md)
- Fix plans: [`.docs/plans/doodle-jump_gemini-cli.md`](../plans/doodle-jump_gemini-cli.md), [`.docs/plans/doodle-jump_claude-opus-4-7.md`](../plans/doodle-jump_claude-opus-4-7.md), [`.docs/plans/doodle-jump_tour-agent-maker.md`](../plans/doodle-jump_tour-agent-maker.md)
- Per-project notes: [`memories/doodle-jump_*.md`](../../memories/)
