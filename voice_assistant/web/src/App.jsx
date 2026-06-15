import {
  AppBar,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Container,
  Grid,
  Stack,
  Toolbar,
  Typography,
} from '@mui/material'
import PlayArrowIcon from '@mui/icons-material/PlayArrow'
import StopIcon from '@mui/icons-material/Stop'

import CameraCard from './components/CameraCard'
import Conversation from './components/Conversation'
import Waveform from './components/Waveform'
import { useConversation } from './hooks/useConversation'

const STATUS = {
  idle: { label: 'Очікування', color: 'default' },
  listening: { label: 'Слухаю', color: 'success' },
  recording: { label: 'Записую вас…', color: 'success' },
  thinking: { label: 'Думаю…', color: 'warning' },
  speaking: { label: 'Говорю…', color: 'primary' },
}

const USER_COLOR = '#22c55e'
const AI_COLOR = '#3b82f6'

export default function App() {
  const conv = useConversation()
  const s = STATUS[conv.status] || STATUS.idle
  const active = conv.status !== 'idle'

  const userActive = conv.status === 'listening' || conv.status === 'recording'
  const aiActive = conv.status === 'speaking' || conv.status === 'thinking'

  return (
    <Box sx={{ minHeight: '100vh' }}>
      <AppBar position="static" color="transparent" elevation={0} sx={{ borderBottom: '1px solid #1e2a44' }}>
        <Toolbar sx={{ gap: 2 }}>
          <Typography variant="h6" fontWeight={800} sx={{ flexGrow: 1 }}>
            🎙️ Голосовий асистент
          </Typography>
          <Chip color={s.color} label={`● ${s.label}`} sx={{ fontWeight: 700 }} />
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ py: 3 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={7}>
            <CameraCard />
          </Grid>
          <Grid item xs={12} md={5}>
            <Box sx={{ height: { md: 460 }, minHeight: 340 }}>
              <Conversation messages={conv.messages} />
            </Box>
          </Grid>

          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Stack spacing={2} sx={{ py: 2 }}>
                  <Waveform label="Ви" color={USER_COLOR} analyserRef={conv.micAnalyser} active={userActive} />
                  <Waveform label="Асистент" color={AI_COLOR} analyserRef={conv.aiAnalyser} active={aiActive} />
                </Stack>

                <Stack direction="row" spacing={2} alignItems="center" justifyContent="center">
                  {!active ? (
                    <Button size="large" variant="contained" startIcon={<PlayArrowIcon />} onClick={conv.start}>
                      Почати розмову
                    </Button>
                  ) : (
                    <Button
                      size="large"
                      variant="outlined"
                      color="error"
                      startIcon={<StopIcon />}
                      onClick={conv.stop}
                    >
                      Завершити
                    </Button>
                  )}
                </Stack>

                {active && (
                  <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1.5 }}>
                    Просто говоріть — асистент відповідає сам. Можна перебивати під час відповіді.
                  </Typography>
                )}
                {conv.error && (
                  <Typography color="error" variant="body2" align="center" sx={{ mt: 1 }}>
                    Мікрофон: {conv.error}
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>
    </Box>
  )
}
