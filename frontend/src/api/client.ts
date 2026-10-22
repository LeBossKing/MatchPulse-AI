import type { HealthResponse } from '../types/api'

export const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
).replace(/\/+$/, '')

function isHealthResponse(value: unknown): value is HealthResponse {
  if (typeof value !== 'object' || value === null) return false
  const data = value as Record<string, unknown>
  return (
    data.status === 'ok' &&
    data.service === 'matchpulse-api' &&
    typeof data.version === 'string' &&
    ['development', 'test', 'production'].includes(String(data.environment))
  )
}

export async function fetchHealth(signal: AbortSignal): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`, { signal })
  if (!response.ok) throw new Error(`The backend returned HTTP ${response.status}.`)

  const data: unknown = await response.json()
  if (!isHealthResponse(data)) {
    throw new Error('Unexpected backend response. Check the configured API URL.')
  }
  return data
}
