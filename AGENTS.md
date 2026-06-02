# Repository Guidelines

## Project Structure & Module Organization
This repo is a comparison playground for AI-generated artifacts, not a single app. Keep changes scoped to the relevant subdirectory:

- `pong-game/` - Angular 21 app with the only build pipeline.
- `games/` - standalone Doodle Jump HTML variants.
- `landings/` - standalone landing-page HTML variants.
- `exp/` - one-off experiments such as `atoms.html`.
- `memories/` - project notes; read the matching file before non-trivial edits.

Follow the existing naming pattern for generated samples: `<topic>_<tool>.html` (for example, `doodle-jump_gemini-cli.html`).

## Build, Test, and Development Commands
Run Angular commands from `pong-game/`:

```bash
npm install
npm start
npm run build
npm run watch
```

- `npm start` runs the dev server.
- `npm run build` creates the production bundle.
- `npm run watch` rebuilds on file changes.

For static HTML files in `games/`, `landings/`, and `exp/`, open the file directly in a browser. There is no shared top-level build.

## Coding Style & Naming Conventions
Use the local style already present in each artifact. In `pong-game/`, TypeScript uses 2-space indentation, single quotes, trailing commas where practical, and SCSS for styles. Prefer Angular standalone components and keep schematic defaults aligned with `angular.json` (`inlineTemplate`, `inlineStyle`, `skipTests`).

Keep filenames descriptive and tool-specific. Avoid refactoring one generated variant to match another; the differences are part of the repo’s purpose.

## Testing & Validation
There is no automated test suite configured for `pong-game/`, so validate changes with a production build:

```bash
cd pong-game && npm run build
```

If you change a static HTML artifact, do a manual browser check for layout, controls, and console errors.

## Commit & Pull Request Guidelines
Recent commits use short, imperative messages, often with Conventional Commit prefixes such as `feat:` and `fix:`. Keep commits focused on one artifact or one logical change. PRs should include a brief summary, the affected path(s), and screenshots or recordings for visible UI changes.

## Agent-Specific Instructions
Read the relevant note in `memories/` before editing a generated artifact. Do not introduce shared abstractions across the standalone HTML samples.
