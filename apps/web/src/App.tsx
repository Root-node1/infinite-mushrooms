import { useEffect, useState } from 'react'
import { getHealth, type Health } from './api'

function App() {
  const [health, setHealth] = useState<Health | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getHealth()
      .then(setHealth)
      .catch((e: Error) => setError(e.message))
  }, [])

  return (
    <main style={{ fontFamily: 'system-ui, sans-serif', padding: '2rem' }}>
      <h1>Infinite Mushrooms</h1>
      <p>Farm management and POS for reishi and oyster growers.</p>
      <h2>API status</h2>
      {health && (
        <p>
          ✓ {health.service}: {health.status}
        </p>
      )}
      {error && <p>✗ API unreachable: {error}</p>}
      {!health && !error && <p>Checking...</p>}
    </main>
  )
}

export default App
