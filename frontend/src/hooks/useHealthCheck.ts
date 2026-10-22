import { useEffect, useState } from 'react'
import { fetchHealth } from '../api/client'
import type { HealthResponse } from '../types/api'

type ConnectionState =
  | { status: 'checking'; health: null; error: null }
  | { status: 'connected'; health: HealthResponse; error: null }
  | { status: 'offline'; health: null; error: string }

export function useHealthCheck() {
  const [attempt, setAttempt] = useState(0)
  const [state, setState] = useState<ConnectionState>({
    status: 'checking', health: null, error: null,
  })

  useEffect(() => {
    let active = true
    const controller = new AbortController()
    const timeout = window.setTimeout(() => controller.abort(), 5000)

    async function check() {
      setState({ status: 'checking', health: null, error: null })
      try {
        const health = await fetchHealth(controller.signal)
        if (active) setState({ status: 'connected', health, error: null })
      } catch (error) {
        if (!active) return
        const message = controller.signal.aborted
          ? 'Connection timed out. Start the FastAPI server and retry.'
          : error instanceof TypeError
            ? 'Cannot reach the backend. Start FastAPI and check the API URL and CORS configuration.'
            : error instanceof Error
              ? error.message
              : 'The backend connection could not be checked.'
        setState({ status: 'offline', health: null, error: message })
      } finally {
        window.clearTimeout(timeout)
      }
    }

    void check()
    return () => {
      active = false
      window.clearTimeout(timeout)
      controller.abort()
    }
  }, [attempt])

  return { ...state, retry: () => setAttempt((value) => value + 1) }
}
