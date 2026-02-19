const API_BASE = 'http://localhost:8000/api'

export async function runSimulation(payload = {}) {
  const response = await fetch(`${API_BASE}/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })

  if (!response.ok) {
    throw new Error('Failed to run simulation')
  }

  return response.json()
}
