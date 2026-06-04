# Fix plan — doodle-jump_tour-agent-maker.html

**Artifact:** `games/doodle-jump_tour-agent-maker.html` (1,063 LOC)
**Source QA:** [`.docs/qa/doodle-jump_tour-agent-maker.md`](../qa/doodle-jump_tour-agent-maker.md)
**Created:** 2026-06-04

**Scope guardrail:** keep this variant's "design-system-aware" character — CSS variables, panel/chip primitives, multi-input model. Don't refactor toward the other two variants' shapes. See repo `CLAUDE.md` rule "don't cross-pollinate variants."

---

## Suggested order

M1 (dead code) and M2 (broken time-based achievement) are quick correctness fixes — do first. M3 (resize) and M4 (bonus radius) are gameplay-facing. M5 (tilt UX) is iOS-only polish.

---

## Major

### Fix M1 — Dead `endGame` / `saveScore`, two sources of truth for score persistence
**QA ref:** M1 · **Effort:** ~10 min · **Risk:** low

Consolidate into one path. Inline scoring in `gameOver` is fine — just delete the unused helpers.

```diff
-    function saveScore() {
-      state.scores.push({ score: score | 0, skin: state.skin, theme: state.theme, t: Date.now() });
-      state.scores.sort((a, b) => b.score - a.score || b.t - a.t);
-      state.scores = state.scores.slice(0, 5);
-      state.high = Math.max(state.high, score | 0);
-      saveProgress();
-      updateLeaderboard();
-      drawScores();
-    }
-    function endGame() {
-      if (state.mode === 'over') return;
-      cancelAnimationFrame(raf);
-      audio.boom();
-      saveScore();
-      drawScores();
-      show('over');
-    }
```

Then add the one missing concern from `endGame` to the live `gameOver`:

```diff
 function gameOver() {
   if (state.mode === 'over') return;
   state.mode = 'over';
+  cancelAnimationFrame(raf);
   audio.boom();
   vibrate([80, 50, 100]);
   ...
 }
```

**Verify:** trigger game over via monster, UFO, fall, and black hole — score persists, leaderboard updates, no double rAF.

---

### Fix M2 — Time-based achievement uses wall clock, ignores pause
**QA ref:** M2 · **Effort:** ~10 min · **Risk:** low

Track *playing* time, not wall-clock time.

```diff
-    let startTime = 0;
+    let playTime = 0;
     function startGame() {
       reset();
-      startTime = Date.now();
+      playTime = 0;
       audio.ensure();
       show('playing');
       last = 0;
       raf = requestAnimationFrame(step);
     }
```

In `step()`:

```diff
       const dt = Math.min(0.033, Math.max(0.001, (ts - last) / 1000));
       last = ts;
+      playTime += dt;
```

In `unlockChecks()`:

```diff
       if (score >= 1000) unlock('h1000', 'First 1000 points');
-      if ((Date.now() - startTime) > 60000) unlock('s60', '60 seconds survived');
+      if (playTime > 60) unlock('s60', '60 seconds survived');
       if (state.scores.length >= 3 && score >= 300) unlock('mid', 'Mid climber');
```

**Verify:** pause for 90s, resume, drop immediately — `s60` should NOT unlock. Then play 60s contiguously → it should.

---

### Fix M3 — Mid-game resize leaves stale world
**QA ref:** M3 · **Effort:** ~15 min · **Risk:** medium

Pick one:

**Option A — pause on resize (simpler):**

```diff
     function resize() {
       const dpr = Math.min(2, window.devicePixelRatio || 1);
       DPR = dpr;
       W = innerWidth; H = innerHeight;
       canvas.width = Math.floor(W * dpr);
       canvas.height = Math.floor(H * dpr);
       ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
+      if (state.mode === 'playing') pauseGame();
       draw();
     }
```

**Option B — rescale world (preserves the run):**

```js
let prevW = innerWidth;
function resize() {
  const oldW = prevW;
  const dpr = Math.min(2, window.devicePixelRatio || 1);
  DPR = dpr;
  W = innerWidth; H = innerHeight;
  canvas.width = Math.floor(W * dpr);
  canvas.height = Math.floor(H * dpr);
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  if (state.mode === 'playing' && world.player) {
    const r = W / oldW;
    world.player.x *= r;
    for (const p of world.platforms) {
      p.x *= r;
      p.minX = 24;
      p.maxX = Math.max(24, W - p.w - 24);
    }
    for (const e of world.enemies)     e.x *= r;
    for (const h of world.blackholes)  h.x *= r;
    for (const pr of world.projectiles) pr.x *= r;
    for (const b of world.bonuses)     b.x *= r;
  }
  prevW = W;
  draw();
}
```

**Verify:** resize browser mid-run; player + platforms stay reachable.

---

### Fix M4 — Bonus pickup radius too tight
**QA ref:** M4 · **Effort:** ~3 min · **Risk:** low

Switch to AABB overlap (consistent with platforms and enemies):

```diff
     function updateBonuses(dt) {
       for (const b of world.bonuses) {
         if (!b.alive) continue;
         const pl = world.platforms.find(p => p.id === b.platformId && !p.removed);
         if (pl) { b.x = pl.x + pl.w * .5 - b.w * .5; b.y = pl.y - 24; }
         else { b.vy += 80 * dt; b.y += b.vy * dt; }
         b.spin += dt * 3;
-        if (circleRect(world.player.x + world.player.w * .5, world.player.y + world.player.h * .5, 20, b.x, b.y, b.w, b.h)) collectBonus(b);
+        if (collides(world.player, b)) collectBonus(b);
       }
     }
```

**Verify:** spawn-heavy run; bonuses sitting on platform corners should collect when player jumps onto the platform, not be skipped.

---

### Fix M5 — Tilt permission denial has no recovery path
**QA ref:** M5 · **Effort:** ~10 min · **Risk:** none

Re-request on every checkbox toggle, and show a small hint in the toast when denied.

```diff
     function requestTilt() {
       if (!state.tilt) return;
       if (typeof DeviceOrientationEvent !== 'undefined' && typeof DeviceOrientationEvent.requestPermission === 'function') {
-        DeviceOrientationEvent.requestPermission().then(r => tiltAllowed = r === 'granted').catch(() => tiltAllowed = false);
+        DeviceOrientationEvent.requestPermission().then(r => {
+          tiltAllowed = r === 'granted';
+          if (!tiltAllowed) showToast('Tilt denied — enable Motion access in Safari settings');
+        }).catch(() => {
+          tiltAllowed = false;
+          showToast('Tilt unavailable');
+        });
       } else {
         tiltAllowed = true;
       }
     }
```

```diff
-      ui.tiltChk.onchange = e => { setSetting('tilt', e.target.checked); if (e.target.checked) requestTilt(); };
+      ui.tiltChk.onchange = e => {
+        setSetting('tilt', e.target.checked);
+        if (e.target.checked) {
+          tiltAllowed = false; // force re-request
+          requestTilt();
+        }
+      };
```

**Verify:** on iOS, deny tilt → toast appears. Toggle off/on → permission re-prompts.

---

## Medium

### Fix m2 — `localStorage` written every frame during score climb
**QA ref:** m2 · **Effort:** ~3 min · **Risk:** none

Remove the per-frame persistence; let `saveProgress()` (called from `gameOver` and `clearScoresBtn`) handle it.

```diff
       if (score > state.high) {
         state.high = score | 0;
         bestEl.textContent = String(state.high | 0);
-        storage.set(STORAGE.high, String(state.high));
       }
```

```diff
       score = Math.max(score, Math.floor(Math.max(0, -cameraY / 70)));
-      if (score > state.high) { state.high = score | 0; bestEl.textContent = String(state.high | 0); storage.set(STORAGE.high, String(state.high | 0)); }
+      if (score > state.high) { state.high = score | 0; bestEl.textContent = String(state.high | 0); }
```

`saveProgress()` is already called from `gameOver()`, so the new high persists at end-of-run. There's also a `beforeunload` listener (line 1051) that catches mid-tab-close.

**Verify:** climb fast on a real device; no frame stutter.

---

### Fix m3 — Mobile control zones cover only 24vh
**QA ref:** m3 · **Effort:** ~2 min · **Risk:** none

Extend zone height to cover more of the screen:

```diff
     .zone {
       position: absolute;
       bottom: 0;
-      height: 24vh;
+      height: 60vh;
       pointer-events: auto;
     }
```

Pick a value that doesn't hide UI chrome — 60vh keeps the score/pause buttons clear at top.

---

### Fix m4 — Black hole hitbox vs visual mismatch
**QA ref:** m4 · **Effort:** ~1 min · **Risk:** none

Either tighten the visual or widen the hitbox to match — recommend matching them.

```diff
-        if (dist < h.r * .8) gameOver();
+        if (dist < h.r) gameOver();
```

If the previous `.8` was a deliberate "be generous" buffer, keep it but also draw the dashed inner kill-circle so the player sees the true hitbox.

---

### Fix m6 — `keys` TDZ fragility
**QA ref:** m6 · **Effort:** ~2 min · **Risk:** none

Hoist `keys` to module-level state (alongside `mobileLeft` / `tiltValue`):

```diff
     let mobileLeft = false, mobileRight = false, tiltValue = 0, tiltAllowed = false;
+    const keys = { left: false, right: false };
     ...
     function bindInput() {
-      const keys = { left: false, right: false };
       addEventListener('keydown', e => {
```

Wait — `keys` is **already** at module level (line 953, just before `bindInput`). The issue is it's declared *after* `updatePlayer` references it. Move it earlier in the IIFE, near the other state declarations:

```diff
     let cameraY = 0, highestY = 0, score = 0, comboSpring = 0;
     let mobileLeft = false, mobileRight = false, tiltValue = 0, tiltAllowed = false;
+    const keys = { left: false, right: false };
     let swipeStart = null;
```

Delete the `const keys = ...` near line 953.

---

### Fix m7 — Redundant slice in `saveProgress`
**QA ref:** m7 · **Effort:** ~1 min · **Risk:** none

Either trust the slice in `gameOver` (line 543) and drop it in `saveProgress`, or vice versa. Recommend keeping the slice in `gameOver` (it's the input boundary) and removing from `saveProgress`:

```diff
     function saveProgress() {
       storage.set(STORAGE.high, String(state.high));
-      storage.set(STORAGE.scores, JSON.stringify(state.scores.slice(0, 5)));
+      storage.set(STORAGE.scores, JSON.stringify(state.scores));
       storage.set(STORAGE.ach, JSON.stringify(state.ach));
     }
```

---

## Minor — only if you're already in the file

- **n2** — Move `unlockChecks()` out of the per-frame loop; call from event sites that change `score` / `playTime`.
- **n4** — Add a volume slider in Settings (master gain is hardcoded to 0.06).
- **n5** — Add a comment above `THEMES` explaining the `p0..p4` → platform-kind mapping.

---

## Out of scope

- Adding achievements/skins from the claude-opus variant — different design language.
- Removing the design tokens to "simplify like gemini-cli" — that's this variant's whole identity.

---

## Verification checklist after all fixes

- [ ] `endGame` / `saveScore` removed, scoring still works on death via every cause (fall, monster, UFO, black hole, projectile)
- [ ] Pause for 90s then play 5s → `s60` does NOT unlock
- [ ] Window resize mid-run → player + platforms remain reachable (or game pauses)
- [ ] Bonuses on platform corners are reliably collected
- [ ] On iOS, denying tilt shows a toast and can be re-requested
- [ ] No per-frame `localStorage` writes (check DevTools → Application → Storage events)
- [ ] Mobile touch zones cover at least the lower half of screen
- [ ] Cold load with no stored state still works (try `localStorage.clear()` + reload)
