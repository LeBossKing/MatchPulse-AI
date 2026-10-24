// @vitest-environment node
import { afterAll, beforeAll, describe, expect, it, vi } from 'vitest'
import { demoServer } from './demo-server'

// Explicit opt-in: starts a real local FastAPI process in mock mode. Never Azure.
// The normal frontend test suite remains independent of Python installation.
describe.runIf(process.env.MATCHPULSE_RUN_API_TESTS === '1')(
  'real FastAPI HTTP integration',
  () => {
    let server: Awaited<ReturnType<typeof demoServer>> | undefined
    let base: string
    let client: typeof import('../src/api/client')

    beforeAll(async () => {
      server = await demoServer()
      await server.start()
      base = server.url
      vi.stubEnv('VITE_API_BASE_URL', base)
      vi.resetModules()
      client = await import('../src/api/client')
    }, 10000)

    afterAll(async () => {
      await server?.stop()
      vi.unstubAllEnvs()
    })

    it('renders the typed read contract and all 32 runtime event/preference variants over real HTTP', async () => {
      const data = await client.fetchDemo(new AbortController().signal)
      expect(data.events.events).toHaveLength(8)
      for (const event of data.events.events)
        for (const language of ['en', 'fr'] as const)
          for (const audience of ['fan', 'analyst'] as const) {
            const result = await client.processEvent(
              {
                match_id: data.events.match_id,
                event_id: event.event_id,
                audience,
                language,
              },
              data,
              new AbortController().signal,
            )
            expect(result.provider).toBe('mock')
            expect(result.result_source).toBe('runtime')
            expect(result.language).toBe(language)
          }
    })

    it('allows the frontend POST preflight and returns typed selector errors', async () => {
      const preflight = await fetch(`${base}/events/process`, {
        method: 'OPTIONS',
        headers: {
          Origin: 'http://localhost:5173',
          'Access-Control-Request-Method': 'POST',
          'Access-Control-Request-Headers': 'content-type',
        },
      })
      expect(preflight.status).toBe(200)
      expect(preflight.headers.get('access-control-allow-origin')).toBe(
        'http://localhost:5173',
      )
      const data = await client.fetchDemo(new AbortController().signal)
      await expect(
        client.processEvent(
          {
            match_id: 'match-demo-01',
            event_id: 'missing-event',
            audience: 'analyst',
            language: 'en',
          },
          data,
          new AbortController().signal,
        ),
      ).rejects.toMatchObject({
        kind: 'http',
        status: 404,
        code: 'event_not_found',
      })
    })
  },
)
