import { spawn } from 'node:child_process'
import type { ChildProcess } from 'node:child_process'
import { existsSync } from 'node:fs'
import { createServer } from 'node:net'
import { setTimeout as delay } from 'node:timers/promises'
import { fileURLToPath, URL as NodeURL } from 'node:url'

// An actual local backend, with credentials overridden even if .env exists.
// "fallback" exercises invalid Azure configuration without a model request.
export async function demoServer(provider: 'mock' | 'fallback' = 'mock') {
  const socket = createServer()
  await new Promise<void>((resolve, reject) => {
    socket.once('error', reject)
    socket.listen(0, '127.0.0.1', resolve)
  })
  const address = socket.address()
  if (!address || typeof address === 'string') throw new Error('No test port')
  const port = address.port
  await new Promise<void>((resolve, reject) =>
    socket.close((error) => (error ? reject(error) : resolve())),
  )
  const backend = fileURLToPath(new NodeURL('../../backend/', import.meta.url))
  const python =
    process.platform === 'win32'
      ? `${backend}.venv/Scripts/python.exe`
      : `${backend}.venv/bin/python`
  if (!existsSync(python))
    throw new Error(
      'Install backend/requirements-dev.txt in backend/.venv first.',
    )
  const url = `http://127.0.0.1:${port}`
  let processHandle: ChildProcess | undefined

  async function stop() {
    const child = processHandle
    processHandle = undefined
    if (!child?.pid || child.exitCode !== null || child.signalCode !== null)
      return
    await new Promise<void>((resolve) => {
      const force = setTimeout(() => child.kill('SIGKILL'), 2000)
      child.once('exit', () => {
        clearTimeout(force)
        resolve()
      })
      child.kill('SIGTERM')
    })
  }

  async function start() {
    if (processHandle) throw new Error('Test backend is already running')
    const child = spawn(
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
          LLM_PROVIDER: provider === 'fallback' ? 'azure' : 'mock',
          AZURE_OPENAI_ENDPOINT: '',
          AZURE_OPENAI_DEPLOYMENT: '',
          AZURE_OPENAI_API_KEY: '',
          AZURE_OPENAI_TIMEOUT_SECONDS: '15',
          AZURE_OPENAI_MAX_OUTPUT_TOKENS: '2048',
          FRONTEND_ORIGIN: 'http://localhost:5173',
        },
      },
    )
    processHandle = child
    let failed = false
    child.once('error', () => {
      failed = true
    })
    for (let count = 0; count < 60; count++) {
      if (failed || child.exitCode !== null) break
      try {
        if (
          (await fetch(`${url}/health`, { signal: AbortSignal.timeout(500) }))
            .ok
        )
          return
      } catch {
        /* Wait for uvicorn. */
      }
      await delay(100)
    }
    await stop()
    throw new Error(
      'FastAPI could not start. Check backend/.venv and requirements-dev.txt.',
    )
  }

  return { url, start, stop }
}
