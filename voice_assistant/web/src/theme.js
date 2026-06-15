import { createTheme } from '@mui/material/styles'

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#3b82f6' },
    success: { main: '#22c55e' },
    warning: { main: '#f59e0b' },
    background: { default: '#0f172a', paper: '#111a2e' },
  },
  shape: { borderRadius: 12 },
  typography: { fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, sans-serif' },
})

export default theme
