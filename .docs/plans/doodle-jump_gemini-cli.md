# Fix plan — doodle-jump_gemini-cli.html

**Artifact:** `games/doodle-jump_gemini-cli.html` (923 LOC)
**Source QA:** [`.docs/qa/doodle-jump_gemini-cli.md`](../qa/doodle-jump_gemini-cli.md)
**Created:** 2026-06-04

**Scope guardrail:** keep the file's "leanest of the three" character. Do not import features, classes, or visual conventions from the other two variants — just fix what's broken. See repo `CLAUDE.md` rule "don't cross-pollinate variants."

---

## Suggested order

Fix Major bugs first (M1 → M4) — they affect gameplay correctness. Medium polish (m1–m4) is independent and can ship in any order. Skip Minors unless you're already in the file.

---

## Major

### Fix M1 — Double rAF loop after resume
**QA ref:** M1 · **Effort:** ~10 min · **Risk:** low

Cancel any in-flight animation frame before resuming.

```diff
 function togglePause() {
   if (gameState === 'playing') {
     isPaused = !isPaused;
     if (!isPaused) {
       pauseScreen.classList.remove('active');
-      gameLoop();
+      cancelAnimationFrame(animationId);
+      animationId = requestAnimationFrame(gameLoop);
     } else {
       pauseScreen.classList.add('active');
     }
   }
 }
```

Also short-circuit the rAF chain while paused so the loop genuinely stops instead of spinning:

```diff
 function gameLoop() {
-  if (!isPaused) {
-    update();
-    draw();
-  }
+  if (isPaused) return;
+  update();
+  draw();
   ...
-  animationId = requestAnimationFrame(gameLoop);
+  if (gameState === 'playing' || (gameState === 'gameover' && particles.length > 0)) {
+    animationId = requestAnimationFrame(gameLoop);
+  }
 }
```

**Verify:** start a run, press P twice, watch player movement speed (should match initial), confirm score doesn't tick while paused.

---

### Fix M2 — Mid-game resize leaves world misaligned
**QA ref:** M2 · **Effort:** ~20 min · **Risk:** medium

Two options — pick one:

**Option A (simpler):** pause the game on resize and require manual resume.

```diff
 window.addEventListener('resize', () => {
+  if (gameState === 'playing' && !isPaused) togglePause();
   resizeCanvas();
 });
```

**Option B (preserves the run):** rescale world coordinates by the W ratio.

```js
let prevW = CANVAS_WIDTH;
window.addEventListener('resize', () => {
  const oldW = prevW;
  resizeCanvas();
  if (gameState === 'playing') {
    const ratio = CANVAS_WIDTH / oldW;
    player.x *= ratio;
    for (const p of platforms) p.x *= ratio;
    for (const e of enemies)   e.x *= ratio;
    for (const it of items)    it.x *= ratio;
  }
  prevW = CANVAS_WIDTH;
});
```

Y-axis usually doesn't need rescaling — gravity / cameraY are in absolute pixels.

**Verify:** start a run on desktop, drag the window narrower → wider; confirm player stays inside, platforms span the new width.

---

### Fix M3 — Multi-touch breaks input
**QA ref:** M3 · **Effort:** ~15 min · **Risk:** low

Track touches by `identifier` instead of using a global pair of booleans.

```js
const activeTouches = new Map(); // id → 'left' | 'right'

gameContainer.addEventListener('touchstart', (e) => {
  if (gameState !== 'playing' || isPaused) return;
  if (e.target.id === 'pauseBtnUI') return;
  e.preventDefault();
  const rect = gameContainer.getBoundingClientRect();
  for (const t of e.changedTouches) {
    const side = (t.clientX - rect.left < CANVAS_WIDTH / 2) ? 'left' : 'right';
    activeTouches.set(t.identifier, side);
  }
  touchLeft  = [...activeTouches.values()].includes('left');
  touchRight = [...activeTouches.values()].includes('right');
}, { passive: false });

function endTouches(e) {
  if (e.target.id === 'pauseBtnUI') return;
  e.preventDefault();
  for (const t of e.changedTouches) activeTouches.delete(t.identifier);
  touchLeft  = [...activeTouches.values()].includes('left');
  touchRight = [...activeTouches.values()].includes('right');
}
gameContainer.addEventListener('touchend',    endTouches, { passive: false });
gameContainer.addEventListener('touchcancel', endTouches, { passive: false });
```

**Verify:** two fingers, one each side; release one — the other should still register.

---

### Fix M4 — Corrupt localStorage crashes load
**QA ref:** M4 · **Effort:** ~2 min · **Risk:** none

```diff
-let leaderBoard = JSON.parse(localStorage.getItem('doodle_leaderboard')) || [0,0,0,0,0];
+let leaderBoard;
+try {
+  leaderBoard = JSON.parse(localStorage.getItem('doodle_leaderboard')) || [];
+  if (!Array.isArray(leaderBoard)) leaderBoard = [];
+} catch {
+  leaderBoard = [];
+}
```

Pair with **m2** (initialize as empty array, render "No scores yet" until populated).

**Verify:** open DevTools → set `localStorage.doodle_leaderboard = 'garbage'` → reload. Menu should still render.

---

### Fix M5 — Post-game-over particle loop entanglement
**QA ref:** M5 · **Effort:** included in M1
Resolved by M1's correct guard around `requestAnimationFrame`. No separate change needed.

---

## Medium

### Fix m1 — `roundRect` fallback
**QA ref:** m1 · **Effort:** ~5 min

Add once near the top of the script:

```js
if (!CanvasRenderingContext2D.prototype.roundRect) {
  CanvasRenderingContext2D.prototype.roundRect = function (x, y, w, h, r) {
    r = Math.min(r, w / 2, h / 2);
    this.beginPath();
    this.moveTo(x + r, y);
    this.arcTo(x + w, y,     x + w, y + h, r);
    this.arcTo(x + w, y + h, x,     y + h, r);
    this.arcTo(x,     y + h, x,     y,     r);
    this.arcTo(x,     y,     x + w, y,     r);
    this.closePath();
    return this;
  };
}
```

---

### Fix m2 — Empty leaderboard display
**QA ref:** m2 · **Effort:** ~3 min (pair with M4)

```diff
-let leaderBoard = ... || [0,0,0,0,0];
+let leaderBoard = ... || [];
 function renderLeaderboard() {
-  let html = leaderBoard.map((s,i) => `<div>${i+1}. ${s}</div>`).join('');
+  let html = leaderBoard.length
+    ? leaderBoard.map((s,i) => `<div>${i+1}. ${s}</div>`).join('')
+    : `<div style="color:#888">No scores yet</div>`;
   ...
 }
```

---

### Fix m4 — Enemy AABB lets grazing collisions kill
**QA ref:** m4 · **Effort:** ~10 min

Black hole hit logic is already deadly by design — leave it. Monster check already distinguishes stomp from kill (line 789). The bug is that the **grazing top-frame** of a stomp can register as a kill if the player is still moving up at the exact contact frame. Tighten the kill arm:

```diff
 if (enemy.type === 0 && player.vy > 0 && player.y + player.height < enemy.y + enemy.height / 2) {
   // stomp
 } else {
-  gameOver();
+  // Only kill if the player is meaningfully overlapping vertically.
+  if (player.y + player.height > enemy.y + 4) gameOver();
 }
```

(Adjust the `+4` margin if the feel is off.)

---

### Fix m6 — "New record" indicator
**QA ref:** m6 · **Effort:** ~5 min

In `gameOver()`:

```js
const isRecord = leaderBoard.length === 0 || score > leaderBoard[0];
// ...after pushing/sorting:
if (isRecord && score > 0) {
  const tag = document.createElement('div');
  tag.textContent = '🎉 NEW BEST';
  tag.style.cssText = 'color:#e67e22;font-weight:bold;margin:8px 0';
  gameOverScreen.insertBefore(tag, gameOverScreen.querySelector('h3'));
}
```

---

## Minor — only if you're already in the file

- **n1** — Add `<meta name="apple-mobile-web-app-capable" content="yes">` and `<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">`.
- **n3** — Replace magic numbers `0..4` with `const PLAT_TYPES = { NORMAL: 0, MOVING: 1, BREAKABLE: 2, SPRING: 3, DISAPPEAR: 4 }`.
- **n4** — Replace pause button text `II` with `⏸`.

---

## Out of scope

- Adding skins, themes, achievements, music — those are claude-opus / tour-agent-maker territory. Importing them would erase this variant's identity as "the lean baseline."
- Performance optimizations (pooling, etc.) — not warranted at this scale.

---

## Verification checklist after all fixes

- [ ] Pause/resume keeps gameplay at 1× speed
- [ ] Window resize during play leaves player visible and platforms reachable
- [ ] Two-finger touch input works on mobile
- [ ] Corrupt `localStorage.doodle_leaderboard` doesn't break menu
- [ ] First-time player sees "No scores yet" not five zeros
- [ ] Beating top score shows a 🎉 indicator
