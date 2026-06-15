import { useCallback, useEffect, useRef, useState } from 'react'
import { BrowserVAD } from '../lib/vad'
import { extForMime, pickMime, rmsFromTimeDomain } from '../lib/audio'
import { converse } from '../api'

const SPEAK_BOOST = 1.8 // raise VAD threshold while AI speaks (anti-echo)

/**
 * Hands-free conversation loop: mic -> VAD -> record -> /api/converse -> play,
 * then auto-resume listening. Barge-in stops playback when the user speaks.
 * Exposes the mic/AI AnalyserNodes (via refs) so the waveforms can read them
 * directly each frame, without pushing sample arrays through React state.
 */
export function useConversation() {
  const [status, setStatusState] = useState('idle') // idle|listening|recording|thinking|speaking
  const [messages, setMessages] = useState([])
  const [error, setError] = useState(null)

  const statusRef = useRef('idle')
  const setStatus = useCallback((s) => {
    statusRef.current = s
    setStatusState(s)
  }, [])

  const ctxRef = useRef(null)
  const streamRef = useRef(null)
  const micAnalyserRef = useRef(null)
  const micBufRef = useRef(null)
  const aiAnalyserRef = useRef(null)
  const audioElRef = useRef(null)
  const recRef = useRef(null)
  const chunksRef = useRef([])
  const vadRef = useRef(null)
  const rafRef = useRef(0)
  const runningRef = useRef(false)

  const add = useCallback((role, text) => setMessages((m) => [...m, { role, text }]), [])

  const startRecorder = useCallback(() => {
    const mime = pickMime()
    const rec = new MediaRecorder(streamRef.current, mime ? { mimeType: mime } : undefined)
    chunksRef.current = []
    rec.ondataavailable = (e) => e.data.size && chunksRef.current.push(e.data)
    recRef.current = rec
    rec.start()
  }, [])

  const stopRecorder = useCallback(
    () =>
      new Promise((resolve) => {
        const rec = recRef.current
        if (!rec || rec.state === 'inactive') return resolve(null)
        rec.onstop = () => {
          setStatus('thinking') // gate VAD while processing
          resolve(new Blob(chunksRef.current, { type: rec.mimeType || 'audio/webm' }))
        }
        rec.stop()
      }),
    [setStatus],
  )

  // Fire-and-forget playback: `onDone` runs on natural end / error, but NOT on
  // barge-in (onSpeechStart nulls `onended` first), so the turn ends cleanly.
  const playAnswer = useCallback(
    (res, onDone) => {
      const el = audioElRef.current
      if (!res.audio || !el) return onDone()
      el.onended = () => onDone()
      el.onerror = () => onDone()
      el.src = `data:${res.audio_mime || 'audio/mpeg'};base64,${res.audio}`
      setStatus('speaking')
      el.play().catch(() => onDone())
    },
    [setStatus],
  )

  const handleBlob = useCallback(
    async (blob) => {
      if (!blob || blob.size === 0) {
        setStatus('listening')
        return
      }
      try {
        const res = await converse(blob, `audio.${extForMime(blob.type)}`)
        if (res.user_text) add('user', res.user_text)
        if (res.assistant_text) add('assistant', res.assistant_text)
        playAnswer(res, () => (res.end ? stop() : setStatus('listening')))
      } catch (e) {
        add('assistant', `⚠️ Помилка: ${e.message}`)
        setStatus('listening')
      }
    },
    [add, playAnswer, setStatus],
  )

  const onSpeechStart = useCallback(() => {
    const s = statusRef.current
    if (s === 'speaking') {
      const el = audioElRef.current // barge-in: silence the assistant
      if (el) {
        el.onended = null
        el.pause()
        el.currentTime = 0
      }
    } else if (s !== 'listening') {
      return
    }
    setStatus('recording')
    startRecorder()
  }, [setStatus, startRecorder])

  const onSpeechEnd = useCallback(async () => {
    if (statusRef.current !== 'recording') return
    const blob = await stopRecorder()
    await handleBlob(blob)
  }, [stopRecorder, handleBlob])

  const loop = useCallback(() => {
    const mic = micAnalyserRef.current
    if (mic) {
      mic.getByteTimeDomainData(micBufRef.current)
      const userRms = rmsFromTimeDomain(micBufRef.current)
      const s = statusRef.current
      if (s === 'listening' || s === 'recording' || s === 'speaking') {
        const boost = s === 'speaking' ? SPEAK_BOOST : 1
        const ev = vadRef.current.feed(userRms, boost)
        if (ev === 'start') onSpeechStart()
        else if (ev === 'end') onSpeechEnd()
      }
    }
    rafRef.current = requestAnimationFrame(loop)
  }, [onSpeechStart, onSpeechEnd])

  const start = useCallback(async () => {
    if (runningRef.current) return
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true },
      })
      streamRef.current = stream
      const ctx = new (window.AudioContext || window.webkitAudioContext)()
      await ctx.resume()

      const micAnalyser = ctx.createAnalyser()
      micAnalyser.fftSize = 1024
      ctx.createMediaStreamSource(stream).connect(micAnalyser)
      micBufRef.current = new Uint8Array(micAnalyser.fftSize)

      const audioEl = new Audio()
      const aiAnalyser = ctx.createAnalyser()
      aiAnalyser.fftSize = 1024
      const aiSource = ctx.createMediaElementSource(audioEl)
      aiSource.connect(aiAnalyser)
      aiAnalyser.connect(ctx.destination)

      ctxRef.current = ctx
      micAnalyserRef.current = micAnalyser
      aiAnalyserRef.current = aiAnalyser
      audioElRef.current = audioEl
      vadRef.current = new BrowserVAD()

      runningRef.current = true
      setError(null)
      setStatus('listening')
      rafRef.current = requestAnimationFrame(loop)
    } catch (e) {
      setError(e?.message || String(e))
    }
  }, [loop, setStatus])

  const stop = useCallback(() => {
    runningRef.current = false
    cancelAnimationFrame(rafRef.current)
    try {
      recRef.current?.state === 'recording' && recRef.current.stop()
    } catch {
      /* ignore */
    }
    const el = audioElRef.current
    if (el) {
      el.onended = null
      el.pause()
    }
    streamRef.current?.getTracks().forEach((tr) => tr.stop())
    ctxRef.current?.close()
    micAnalyserRef.current = null
    aiAnalyserRef.current = null
    setStatus('idle')
  }, [setStatus])

  useEffect(() => () => stop(), [stop])

  return { status, messages, micAnalyser: micAnalyserRef, aiAnalyser: aiAnalyserRef, error, start, stop }
}
