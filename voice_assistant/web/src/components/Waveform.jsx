import { useEffect, useRef } from 'react'
import { Box, Typography } from '@mui/material'

/**
 * Real-time oscilloscope. Reads an AnalyserNode (via `analyserRef.current`)
 * every frame and draws the waveform on a canvas — no React state in the hot path.
 */
export default function Waveform({ analyserRef, color = '#22c55e', active = false, label, height = 96 }) {
  const canvasRef = useRef(null)
  const rafRef = useRef(0)
  const activeRef = useRef(active)
  const colorRef = useRef(color)
  activeRef.current = active
  colorRef.current = color

  useEffect(() => {
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    let buf = null

    const draw = () => {
      const dpr = window.devicePixelRatio || 1
      const w = canvas.clientWidth
      const h = canvas.clientHeight
      if (canvas.width !== Math.round(w * dpr) || canvas.height !== Math.round(h * dpr)) {
        canvas.width = Math.round(w * dpr)
        canvas.height = Math.round(h * dpr)
      }
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
      ctx.clearRect(0, 0, w, h)

      const mid = h / 2
      const an = analyserRef?.current
      const col = colorRef.current
      const on = activeRef.current

      ctx.beginPath()
      if (an) {
        if (!buf || buf.length !== an.fftSize) buf = new Uint8Array(an.fftSize)
        an.getByteTimeDomainData(buf)
        const step = buf.length / w
        for (let x = 0; x < w; x++) {
          const v = (buf[Math.floor(x * step)] - 128) / 128
          const y = mid - v * mid * 0.9
          x === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
        }
      } else {
        ctx.moveTo(0, mid)
        ctx.lineTo(w, mid)
      }

      // soft glow underlay + crisp line on top
      ctx.strokeStyle = col
      ctx.lineCap = 'round'
      ctx.lineJoin = 'round'
      ctx.globalAlpha = on ? 0.4 : 0.12
      ctx.lineWidth = 6
      ctx.stroke()
      ctx.globalAlpha = on ? 1 : 0.4
      ctx.lineWidth = 2.5
      ctx.stroke()
      ctx.globalAlpha = 1

      rafRef.current = requestAnimationFrame(draw)
    }

    rafRef.current = requestAnimationFrame(draw)
    return () => cancelAnimationFrame(rafRef.current)
  }, [analyserRef])

  return (
    <Box sx={{ width: '100%' }}>
      <Typography variant="subtitle2" sx={{ fontWeight: 800, color: active ? color : 'text.secondary', mb: 0.5 }}>
        {label}
      </Typography>
      <Box
        sx={{
          borderRadius: 2,
          bgcolor: '#0b1020',
          border: '1px solid #1e2a44',
          px: 1,
        }}
      >
        <canvas ref={canvasRef} style={{ width: '100%', height, display: 'block' }} />
      </Box>
    </Box>
  )
}
