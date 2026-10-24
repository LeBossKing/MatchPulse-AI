import type { HealthResponse } from '../types/api'
import type { DashboardData } from '../types/dashboard'
import type { ProcessEventRequest, ProcessEventResponse } from '../types/match'
import {
  InvalidResponseError,
  validateDemo,
  validateProcessing,
} from './validation'

export const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
).replace(/\/+$/, '')

export type ApiErrorKind = 'network' | 'timeout' | 'http' | 'invalid_response'
export class ApiError extends Error {
  readonly kind: ApiErrorKind
  readonly status?: number
  readonly code?: string
  constructor(kind: ApiErrorKind, status?: number, code?: string) {
    super(`API request failed: ${kind}${status ? ` (${status})` : ''}`)
    this.kind = kind
    this.status = status
    this.code = code
  }
}

// Deliberately no automatic retries: processing can make a billable Azure call.
export async function requestJson(
  path: string,
  signal: AbortSignal,
  body?: ProcessEventRequest,
  timeoutMs = body ? 75000 : 10000,
): Promise<unknown> {
  const controller = new AbortController()
  let timedOut = false
  const cancel = () => controller.abort()
  signal.addEventListener('abort', cancel, { once: true })
  if (signal.aborted) controller.abort()
  const timer = setTimeout(() => {
    timedOut = true
    controller.abort()
  }, timeoutMs)
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: body ? 'POST' : 'GET',
      signal: controller.signal,
      credentials: 'omit',
      headers: body
        ? { 'Content-Type': 'application/json', Accept: 'application/json' }
        : { Accept: 'application/json' },
      ...(body ? { body: JSON.stringify(body) } : {}),
    })
    let value: unknown
    try {
      value = await response.json()
    } catch {
      if (controller.signal.aborted)
        throw new DOMException('Request aborted', 'AbortError')
      throw new ApiError(
        response.ok ? 'invalid_response' : 'http',
        response.status,
      )
    }
    if (!response.ok) {
      const error =
        typeof value === 'object' && value !== null && 'error' in value
          ? value.error
          : null
      const code =
        typeof error === 'object' &&
        error !== null &&
        'code' in error &&
        typeof error.code === 'string' &&
        /^[a-z_]{1,64}$/.test(error.code)
          ? error.code
          : undefined
      throw new ApiError('http', response.status, code)
    }
    if (controller.signal.aborted)
      throw new DOMException('Request aborted', 'AbortError')
    return value
  } catch (error) {
    if (timedOut) throw new ApiError('timeout')
    if (signal.aborted) throw new DOMException('Request aborted', 'AbortError')
    if (error instanceof ApiError) throw error
    throw new ApiError('network')
  } finally {
    clearTimeout(timer)
    signal.removeEventListener('abort', cancel)
  }
}

function checked<T>(validate: () => T): T {
  try {
    return validate()
  } catch (error) {
    if (error instanceof InvalidResponseError)
      throw new ApiError('invalid_response')
    throw error
  }
}

export async function fetchDemo(signal: AbortSignal): Promise<DashboardData> {
  const [match, events] = await Promise.all([
    requestJson('/matches/demo', signal),
    requestJson('/matches/demo/events', signal),
  ])
  return checked(() => validateDemo(match, events))
}

export async function processEvent(
  request: ProcessEventRequest,
  data: DashboardData,
  signal: AbortSignal,
): Promise<ProcessEventResponse> {
  const value = await requestJson('/events/process', signal, request)
  return checked(() => validateProcessing(value, request, data))
}

export async function fetchHealth(
  signal: AbortSignal,
): Promise<HealthResponse> {
  const value = await requestJson('/health', signal)
  if (typeof value !== 'object' || value === null)
    throw new ApiError('invalid_response')
  const data = value as Record<string, unknown>
  if (
    data.status !== 'ok' ||
    data.service !== 'matchpulse-api' ||
    typeof data.version !== 'string' ||
    !['development', 'test', 'production'].includes(String(data.environment))
  )
    throw new ApiError('invalid_response')
  return data as unknown as HealthResponse
}
