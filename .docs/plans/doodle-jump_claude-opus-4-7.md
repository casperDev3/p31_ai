# Fix plan — doodle-jump_claude-opus-4-7.html

**Artifact:** `games/doodle-jump_claude-opus-4-7.html` (1,436 LOC)
**Source QA:** [`.docs/qa/doodle-jump_claude-opus-4-7.md`](../qa/doodle-jump_claude-opus-4-7.md)
**Created:** 2026-06-04

**Scope guardrail:** keep this variant's "most feature-rich, opinionated UI" character. Fixes should preserve the achievements / skins / themes / settings systems intact. See repo `CLAUDE.md` rule "don't cross-pollinate variants."

**Note:** QA item M5 (`noGreen30` reset) was a false alarm during the audit — `runStats` IS reset per run in `startGame()` line 1077. No fix needed.

---

## Suggested order

M1 → M3 are user-facing bugs (music leaks, wasted CPU, broken mobile-controls toggle). M4 is a polish/clarity fix. Mediums are independent.

---

## Major

### Fix M1 — Music keeps playing after "Quit to Menu"
**QA ref:** M1 · **Effort:** ~5 min · **Risk:** none

Call `stopMusic()` in every state-exit handler that leaves PLAYING.

```diff
 document.getElementById('quitBtn').onclick = () => {
   state = STATE.MENU;
+  stopMusic();
   hide('pauseScreen');
   document.getElementById('hud').classList.add('hidden');
   document.getElementById('pauseBtn').classList.add('hidden');
   document.getElementById('mobileControls').classList.add('hidden');
   show('menuScreen');
 };

 document.getElementById('menuBtn').onclick = () => {
   state = STATE.MENU;
+  stopMusic();
   hide('gameOverScreen');
   show('menuScreen');
 };
```

Also pause music while game is paused (no exit, just silence):

```diff
 function togglePause() {
   if (state === STATE.PLAYING) {
     state = STATE.PAUSED;
+    stopMusic();
     show('pauseScreen');
   } else if (state === STATE.PAUSED) {
     hide('pauseScreen');
     state = STATE.PLAYING;
+    startMusic();
   }
 }
```

**Verify:** play → quit → silence in menu. Play → pause → silence. Resume → music returns.

---

### Fix M2 — Render runs full-canvas every frame regardless of state
**QA ref:** M2 · **Effort:** ~10 min · **Risk:** low

Skip rendering when nothing's animating.

```diff
 function loop() {
   update();
-  render();
+  if (state === STATE.PLAYING || state === STATE.PAUSED) {
+    render();
+  } else if (state === STATE.GAMEOVER) {
+    render(); // keep showing the death snapshot + particles
+  }
+  // STATE.MENU → DOM overlays cover the canvas, no need to redraw.
   requestAnimationFrame(loop);
 }
```

Alternative (cleaner but bigger refactor): only call `requestAnimationFrame(loop)` while playing/gameover, and re-arm it from `startGame()` and from overlay transitions that need a one-time repaint.

**Verify:** open DevTools → Performance tab → record while on menu screen; FPS should be near-idle, not 60fps with constant canvas paints.

---

### Fix M3 — Mobile controls don't toggle on resize
**QA ref:** M3 · **Effort:** ~5 min · **Risk:** none

```diff
+function syncMobileControls() {
+  const el = document.getElementById('mobileControls');
+  if (state !== STATE.PLAYING) { el.classList.add('hidden'); return; }
+  if (window.innerWidth <= 700) el.classList.remove('hidden');
+  else el.classList.add('hidden');
+}
 window.addEventListener('resize', resize);
+window.addEventListener('resize', syncMobileControls);
 resize();
```

Then in `startGame()`:

```diff
-if (window.innerWidth <= 700) document.getElementById('mobileControls').classList.remove('hidden');
+syncMobileControls();
```

**Verify:** resize browser window across 700px boundary mid-game; controls appear / disappear correctly.

---

### Fix M4 — Black hole pulls but cannot kill rocket-boosted player
**QA ref:** M4 · **Effort:** ~3 min · **Risk:** none

Decide one of two behaviors and apply consistently:

**Option A — rocket is fully immune (recommended; matches UFO/projectile treatment):**

```diff
 for (const b of blackholes) {
   b.update();
-  b.pull(player);
+  if (player.rocket <= 0) b.pull(player);
   if (player.rocket <= 0 && rectsOverlap(player.bounds(), b.bounds())) {
     gameOver(); return;
   }
 }
```

**Option B — rocket still deflects (current confusing behavior), but signal it visually:**
Keep `b.pull()` unconditional, add a particle burst when the rocket player is being pulled. (More code; skip unless you like the deflection feel.)

**Verify:** grab a rocket near a black hole; rocket should fly straight, not curve.

---

## Medium

### Fix m1 — Tilt overrides keyboard silently
**QA ref:** m1 · **Effort:** ~3 min

```diff
 let moveInput = 0;
 if (keys.left) moveInput -= 1;
 if (keys.right) moveInput += 1;
-if (Math.abs(tiltX) > 0.1) moveInput = tiltX;
+if (moveInput === 0 && Math.abs(tiltX) > 0.1) moveInput = tiltX;
```

Keyboard wins when keys are held; tilt fills in otherwise.

---

### Fix m2 — Toggle accessibility
**QA ref:** m2 · **Effort:** ~10 min

Replace toggle `<div>`s with `<button>`s and add ARIA. Touches `index.html` markup + `setupToggle()`.

```html
<button class="toggle on" id="soundToggle" role="switch" aria-checked="true">🔊 Sound: ON</button>
```

```diff
 function setupToggle(id, key, label) {
   const el = document.getElementById(id);
   function refresh() {
+    el.setAttribute('aria-checked', settings[key] ? 'true' : 'false');
     if (settings[key]) { el.classList.add('on'); el.textContent = label + ': ON'; }
     else { el.classList.remove('on'); el.textContent = label + ': OFF'; }
   }
   ...
 }
```

CSS already styles `.toggle` — buttons inherit the same look since the class is intact.

---

### Fix m3 — `roundRect` polyfill
**QA ref:** m3 · **Effort:** ~5 min

Replace the local `roundRect()` helper (line 998) with a polyfill that monkey-patches the prototype, so internal calls (`ctx.roundRect`) and the helper agree:

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

The existing `roundRect(c, x, y, w, h, r)` helper can stay or be deleted; it's safe to keep.

---

### Fix m4 — Achievement toast / powerup-timer collision on small viewports
**QA ref:** m4 · **Effort:** ~5 min

```diff
 function drawAchievementToasts() {
-  let y = 90;
+  let y = (player && (player.rocket > 0 || player.hat > 0)) ? 110 : 80;
   for (const t of achievementToasts) {
     ...
   }
 }
```

Push toasts down when the powerup bar is showing.

---

### Fix m7 — Tilt permission requested on first body click even when tilt is off
**QA ref:** m7 · **Effort:** ~2 min

```diff
 document.body.addEventListener('click', () => {
+  if (!settings.tilt) return;
   if (typeof DeviceOrientationEvent !== 'undefined' &&
       typeof DeviceOrientationEvent.requestPermission === 'function' &&
       settings.tilt) {
     DeviceOrientationEvent.requestPermission().catch(()=>{});
   }
 }, { once: true });
```

(Inner `&& settings.tilt` becomes redundant — leave or remove.)

---

## Minor — only if you're already in the file

- **n3** — Render the actual character sprite into a tiny canvas next to each skin emoji preview in the menu picker.
- **n7** — Decouple `Sound.bgTick` from frame count: schedule via `setTimeout` (e.g. every 70ms) instead of "every 4 frames."

---

## Out of scope

- Removing achievements / themes / skins to "match the gemini-cli variant" — that erases this variant's identity.
- Adding new game mechanics — fixes only.

---

## Verification checklist after all fixes

- [ ] Quit-to-menu silences music
- [ ] Pause silences music; resume restarts
- [ ] Idle on menu screen → DevTools shows minimal canvas activity
- [ ] Resize browser across 700px during play → mobile controls toggle
- [ ] Rocket near black hole → straight flight, no curving
- [ ] Keyboard input wins over tilt when keys held
- [ ] Settings toggles reachable via keyboard (Tab + Enter/Space)
- [ ] Open in a pre-Safari-16 browser (or simulate by deleting `CanvasRenderingContext2D.prototype.roundRect` before load) → game still renders
