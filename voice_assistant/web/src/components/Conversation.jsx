import { Box, Card, CardContent, Paper, Stack, Typography } from '@mui/material'
import { useEffect, useRef } from 'react'

export default function Conversation({ messages }) {
  const endRef = useRef(null)
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Typography variant="subtitle1" fontWeight={700} gutterBottom>
          Діалог
        </Typography>

        <Stack spacing={1.2} sx={{ flex: 1, overflowY: 'auto', pr: 1 }}>
          {messages.length === 0 && (
            <Typography variant="body2" color="text.secondary">
              Натисніть «Старт», дозвольте камеру й мікрофон, потім «Говорити».
            </Typography>
          )}

          {messages.map((m, i) => {
            const mine = m.role === 'user'
            return (
              <Box key={i} sx={{ display: 'flex', justifyContent: mine ? 'flex-end' : 'flex-start' }}>
                <Paper
                  elevation={0}
                  sx={{
                    px: 1.5,
                    py: 1,
                    maxWidth: '80%',
                    bgcolor: mine ? 'primary.main' : 'background.default',
                    color: mine ? '#fff' : 'text.primary',
                    border: mine ? 'none' : '1px solid #1e2a44',
                  }}
                >
                  <Typography variant="caption" sx={{ opacity: 0.8, fontWeight: 700 }}>
                    {mine ? 'Ви' : 'Асистент'}
                  </Typography>
                  <Typography variant="body2">{m.text}</Typography>
                </Paper>
              </Box>
            )
          })}
          <div ref={endRef} />
        </Stack>
      </CardContent>
    </Card>
  )
}
