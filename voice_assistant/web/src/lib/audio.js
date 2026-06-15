// Small audio helpers shared by the conversation hook.

export function pickMime() {
  const cands = ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4', 'audio/ogg']
  for (const c of cands) {
    if (window.MediaRecorder && MediaRecorder.isTypeSupported(c)) return c
  }
  return ''
}

export function extForMime(mime = '') {
  if (mime.includes('webm')) return 'webm'
  if (mime.includes('mp4')) return 'mp4'
  if (mime.includes('ogg')) return 'ogg'
  if (mime.includes('wav')) return 'wav'
  return 'webm'
}

/** Root-mean-square of analyser time-domain bytes, normalized to 0..1. */
export function rmsFromTimeDomain(bytes) {
  let sum = 0
  for (let i = 0; i < bytes.length; i++) {
    const v = (bytes[i] - 128) / 128
    sum += v * v
  }
  return Math.sqrt(sum / bytes.length)
}
