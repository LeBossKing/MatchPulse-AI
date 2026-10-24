// @vitest-environment node
import { spawn } from 'node:child_process'
import type { ChildProcess } from 'node:child_process'
import { createServer } from 'node:net'
import { fileURLToPath } from 'node:url'
import { afterAll, beforeAll, describe, expect, it, vi } from 'vitest'

// Explicit opt-in: starts a real local FastAPI process in mock mode. Never Azure.
// The normal frontend test suite remains independent of Python installation.
describe.runIf(process.env.MATCHPULSE_RUN_API_TESTS === '1')(
  'real FastAPI HTTP integration',
  () => {
    let server: ChildProcess
    let base: string
    let client: typeof import('../src/api/client')

    beforeAll(async () => {
      const socket = createServer()
      await new Promise<void>((resolve) =>
        socket.listen(0, '127.0.0.1', resolve),
      )
      const address = socket.address()
      if (!address || typeof address === 'string')
        throw new Error('No test port')
      const port = address.port
      await new Promise<void>((resolve, reject) =>
        socket.close((error) => (error ? reject(error) : resolve())),
      )
      const backend = fileURLToPath(new URL('../../backend/', import.meta.url))
      const python =
        process.platform === 'win32'
          ? `${backend}.venv/Scripts/python.exe`
          : `${backend}.venv/bin/python`
      server = spawn(
        python,
        [
          '-m',
          'uvicorn',
          'app.main:app',
          '--host',
          '127.0.0.1',
          '--port',
          String(port),
        ],
        {
          cwd: backend,
          stdio: 'ignore',
          env: {
            ...process.env,
            APP_ENV: 'test',
            LLM_PROVIDER: 'mock',
            AZURE_OPENAI_ENDPOINT: '',
            AZURE_OPENAI_DEPLOYMENT: '',
            AZURE_OPENAI_API_KEY: '',
            AZURE_OPENAI_TIMEOUT_SECONDS: '15',
            AZURE_OPENAI_MAX_OUTPUT_TOKENS: '2048',
            FRONTEND_ORIGIN: 'http://localhost:5173',
          },
        },
      )
      base = `http://127.0.0.1:${port}`
      let started = false
      let launchError = false
      server.on('error', () => {
        launchError = true
      })
      for (let count = 0; count < 60; count++) {
        try {
          if ((await fetch(`${base}/health`)).ok) {
            started = true
            break
          }
        } catch {
          /* Wait for uvicorn. */
        }
        if (launchError) break
        await new Promise((resolve) => setTimeout(resolve, 100))
      }
      if (!started)
        throw new Error(
          'FastAPI could not start. Install backend/requirements-dev.txt in backend/.venv first.',
        )
      vi.stubEnv('VITE_API_BASE_URL', base)
      vi.resetModules()
      client = await import('../src/api/client')
    }, 10000)

    afterAll(async () => {
      if (server && server.exitCode === null) {
        const exited = new Promise<void>((resolve) =>
          server.once('exit', () => resolve()),
        )
        server.kill()
        await exited
      }
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
