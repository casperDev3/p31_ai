export async function converse(blob, filename) {
  const form = new FormData()
  form.append('audio', blob, filename)
  const res = await fetch('/api/converse', { method: 'POST', body: form })
  if (!res.ok) throw new Error(`Сервер повернув HTTP ${res.status}`)
  return res.json()
}

export async function health() {
  const res = await fetch('/api/health')
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}
