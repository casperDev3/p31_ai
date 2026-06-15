// Browser energy-based VAD — mirrors voice_assistant/audio/vad.py (VADSegmenter).
// Feed it a normalized RMS level (0..1) per analysis frame; it returns
// 'start' when speech begins, 'end' when it ends, or null otherwise.

export class BrowserVAD {
  constructor({
    floor = 0.015,
    factor = 3,
    silenceTail = 0.8,
    maxSeconds = 15,
    frameSec = 1 / 60,
    voicedToStart = 2,
  } = {}) {
    this.floor = floor
    this.factor = factor
    this.tailFrames = Math.max(1, Math.round(silenceTail / frameSec))
    this.maxFrames = Math.round(maxSeconds / frameSec)
    this.voicedToStart = voicedToStart
    this.reset(true)
  }

  reset(full = false) {
    this.collecting = false
    this.voicedRun = 0
    this.silenceRun = 0
    this.frames = 0
    if (full) this.noiseFloor = this.floor / Math.max(this.factor, 1e-6)
  }

  get threshold() {
    return Math.max(this.noiseFloor * this.factor, this.floor)
  }

  /** level: normalized RMS 0..1. boost: multiply threshold (e.g. during playback). */
  feed(level, boost = 1) {
    if (!this.collecting) {
      this.noiseFloor = 0.95 * this.noiseFloor + 0.05 * level
    }
    const thr = this.threshold * boost

    if (!this.collecting) {
      if (level > thr) {
        this.voicedRun += 1
        if (this.voicedRun >= this.voicedToStart) {
          this.collecting = true
          this.frames = 0
          this.silenceRun = 0
          return 'start'
        }
      } else {
        this.voicedRun = 0
      }
      return null
    }

    this.frames += 1
    if (level <= thr) {
      this.silenceRun += 1
      if (this.silenceRun >= this.tailFrames) {
        this.reset()
        return 'end'
      }
    } else {
      this.silenceRun = 0
    }
    if (this.frames >= this.maxFrames) {
      this.reset()
      return 'end'
    }
    return null
  }
}
