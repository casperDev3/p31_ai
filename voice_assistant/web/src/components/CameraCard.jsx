import { useEffect, useRef, useState } from 'react'
import { Alert, Box, Card, CardContent, Chip, Typography } from '@mui/material'
import VideocamIcon from '@mui/icons-material/Videocam'
import VideocamOffIcon from '@mui/icons-material/VideocamOff'

export default function CameraCard() {
  const videoRef = useRef(null)
  const [error, setError] = useState(null)
  const [on, setOn] = useState(false)

  useEffect(() => {
    let stream
    navigator.mediaDevices
      .getUserMedia({ video: { width: 1280, height: 720 } })
      .then((s) => {
        stream = s
        if (videoRef.current) videoRef.current.srcObject = s
        setOn(true)
      })
      .catch((e) => setError(e?.message || String(e)))
    return () => stream?.getTracks().forEach((t) => t.stop())
  }, [])

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column', gap: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="subtitle1" fontWeight={700}>
            Камера
          </Typography>
          <Chip
            size="small"
            color={on ? 'success' : 'default'}
            icon={on ? <VideocamIcon /> : <VideocamOffIcon />}
            label={on ? 'Активна' : 'Вимкнена'}
          />
        </Box>

        {error && <Alert severity="error">Камера недоступна: {error}</Alert>}

        <Box
          sx={{
            flex: 1,
            minHeight: 320,
            borderRadius: 2,
            overflow: 'hidden',
            bgcolor: '#0b1020',
            display: 'flex',
          }}
        >
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
          />
        </Box>
      </CardContent>
    </Card>
  )
}
