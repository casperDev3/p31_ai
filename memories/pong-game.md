# pong-game

**Path:** `pong-game/`
**Type:** Angular 21 single-page application
**Status:** Working game, playable in browser

## What it is

A classic Pong clone (player vs. PC) built as a real Angular CLI project. The only project in this repo with a proper build pipeline — everything else is a standalone HTML file.

## Tech stack

- Angular **21.2** (standalone components, no NgModule)
- TypeScript **~5.9**
- SCSS for global styles (`src/styles.scss`); component styles are inline
- `@angular/build` builder (the new Vite-based esbuild pipeline, not the legacy Webpack builder)
- Prettier 3.8
- No test runner configured — `skipTests: true` is set for all schematics in `angular.json`

## Structure

- `src/app/app.ts` — the entire game lives here as a single standalone component
  - Inline template (uses `@if` control-flow syntax, not `*ngIf`)
  - Inline `styles: [...]`
  - State managed via Angular **signals** (`signal<GameState>(...)`)
  - Game loop runs outside Angular's zone (`zone.runOutsideAngular`) for performance
  - `@HostListener` for keyboard input
- `src/app/app.config.ts` — minimal `ApplicationConfig` with `provideBrowserGlobalErrorListeners()`
- `src/main.ts` — bootstrap entry
- `src/index.html`, `src/styles.scss`
- `public/` — static assets (favicon)

## Game mechanics

- 800×500 canvas, 7 points to win
- Player paddle: `W`/`S` or `↑`/`↓`; PC paddle tracks the ball with `PC_DIFFICULTY = 0.78`
- Ball speeds up 5% per paddle hit, capped at `BALL_MAX_SPEED = 14`
- Vertical bounce angle = (hit offset from paddle center) × 7
- `P` toggles pause; phases: `idle | playing | paused | over`

## Commands

Run from inside `pong-game/`:

```bash
npm install
npm start          # ng serve → http://localhost:4200
npm run build      # production build → dist/
npm run watch      # development watch build
npx ng generate component <name>
```

## Gotchas

- Schematics default to **inline template + inline style + SCSS + no tests** (see `angular.json`). New components will follow that pattern unless you override.
- `app.config.ts` is nearly empty — if you add router/HTTP/animations, they go in the `providers` array.
- Production build has tight budgets: 500 kB initial warning, 1 MB error, 4 kB / 8 kB per component style.
- The game loop is single-component; there's no separation into services/state stores yet.
- `node_modules/` is committed-out via `.gitignore`'s parent rules — run `npm install` after cloning.
