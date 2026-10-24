import { vi } from 'vitest'
import { demo, selectSample } from '../src/data/demo'
import type {
  ProcessEventRequest,
  ProcessEventResponse,
} from '../src/types/match'

export const request = (
  event_id = 'evt-064',
  audience = 'analyst',
  language = 'en',
) =>
  ({
    match_id: 'match-demo-01',
    event_id,
    audience,
    language,
  }) as ProcessEventRequest

// Network test doubles only. These are never imported by the application.
export function runtime(
  input = request(),
  provider: ProcessEventResponse['provider'] = 'mock',
) {
  const value = structuredClone(
    selectSample(
      input.event_id,
      input.audience ?? 'analyst',
      input.language ?? 'en',
    ),
  )
  value.result_source = 'runtime'
  value.provider = provider
  value.warnings =
    provider === 'fallback'
      ? ['Azure timed out; mock fallback used.']
      : ['Synthetic test data.']
  value.agent_trace.forEach((step) => {
    step.summary = 'Test transport response'
    step.duration_ms = 12
  })
  value.agent_trace[1].output = {
    ...value.agent_trace[1].output,
    requested_provider: provider === 'mock' ? 'mock' : 'azure',
    actual_provider: provider === 'azure' ? 'azure' : 'mock',
    fallback_reason: provider === 'fallback' ? 'azure_timeout' : null,
  }
  return value
}

export function json(value: unknown, status = 200) {
  return new Response(JSON.stringify(value), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

export function mockApi(
  process: (
    input: ProcessEventRequest,
    init: RequestInit,
  ) => Response | Promise<Response> = (input) => json(runtime(input)),
) {
  const fetch = vi.fn(
    async (url: string | URL | Request, init: RequestInit = {}) => {
      const path = new URL(String(url)).pathname
      if (path === '/matches/demo') return json(demo.match)
      if (path === '/matches/demo/events') return json(demo.events)
      if (path === '/health')
        return json({
          status: 'ok',
          service: 'matchpulse-api',
          version: '0.4.0',
          environment: 'test',
        })
      if (path === '/events/process')
        return process(JSON.parse(init.body as string), init)
      throw new Error('Unexpected test request')
    },
  )
  vi.stubGlobal('fetch', fetch)
  return fetch
}

export function deferred<T>() {
  let resolve!: (value: T) => void
  const promise = new Promise<T>((done) => {
    resolve = done
  })
  return { promise, resolve }
}
