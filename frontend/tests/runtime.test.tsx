import { StrictMode } from 'react'
import {
  act,
  fireEvent,
  render,
  renderHook,
  screen,
  waitFor,
} from '@testing-library/react'
import { afterEach, expect, it, vi } from 'vitest'
import App from '../src/App'
import { demo } from '../src/data/demo'
import { useAnalysis, CACHE_TTL_MS } from '../src/hooks/useAnalysis'
import { useReplay } from '../src/hooks/useReplay'
import { deferred, json, mockApi, request, runtime } from './helpers'

afterEach(() => {
  vi.unstubAllGlobals()
  vi.useRealTimers()
})
const tick = () =>
  act(async () => {
    await vi.advanceTimersByTimeAsync(210)
  })

it('does not duplicate the initial billable POST under StrictMode', async () => {
  vi.useFakeTimers()
  const fetch = mockApi()
  const { result } = renderHook(() => useAnalysis('api', demo, request()), {
    wrapper: StrictMode,
  })
  await tick()
  expect(result.current.status).toBe('ready')
  expect(
    fetch.mock.calls.filter(([url]) => String(url).endsWith('/events/process')),
  ).toHaveLength(1)
})

it('coalesces rapid navigation and ignores obsolete replies even if transport ignores abort', async () => {
  vi.useFakeTimers()
  const first = deferred<Response>()
  const transport = mockApi((input) =>
    input.event_id === 'evt-064' ? first.promise : json(runtime(input)),
  )
  const { result, rerender } = renderHook(
    ({ id }) => useAnalysis('api', demo, request(id)),
    { initialProps: { id: 'evt-064' } },
  )
  await tick()
  const oldSignal = transport.mock.calls[0][1].signal!
  rerender({ id: 'evt-065' })
  expect(result.current.entry).toBeNull()
  rerender({ id: 'evt-067' })
  await tick()
  expect(oldSignal.aborted).toBe(true)
  expect(transport).toHaveBeenCalledTimes(2)
  expect(result.current.entry?.response.event_id).toBe('evt-067')
  await act(async () => first.resolve(json(runtime(request()))))
  expect(result.current.entry?.response.event_id).toBe('evt-067')
})

it('caches by event and preferences, refreshes explicitly, and expires session entries', async () => {
  vi.useFakeTimers()
  const transport = mockApi()
  const { result, rerender } = renderHook(
    ({ id, language }) =>
      useAnalysis('api', demo, request(id, 'analyst', language)),
    { initialProps: { id: 'evt-064', language: 'en' } },
  )
  await tick()
  rerender({ id: 'evt-067', language: 'en' })
  await tick()
  rerender({ id: 'evt-064', language: 'en' })
  await tick()
  expect(result.current.cached).toBe(true)
  expect(transport).toHaveBeenCalledTimes(2)
  rerender({ id: 'evt-064', language: 'fr' })
  await tick()
  expect(result.current.entry?.response.language).toBe('fr')
  expect(transport).toHaveBeenCalledTimes(3)
  act(() => result.current.refresh())
  await tick()
  expect(result.current.cached).toBe(false)
  expect(transport).toHaveBeenCalledTimes(4)
  await act(async () => {
    await vi.advanceTimersByTimeAsync(CACHE_TTL_MS + 1)
  })
  rerender({ id: 'evt-064', language: 'en' })
  await tick()
  expect(transport).toHaveBeenCalledTimes(5)
})

it('retries an error explicitly without turning it into sample output', async () => {
  vi.useFakeTimers()
  let failed = true
  const transport = mockApi((input) =>
    failed
      ? json({ error: { code: 'processing_failed' } }, 500)
      : json(runtime(input)),
  )
  const { result } = renderHook(() => useAnalysis('api', demo, request()))
  await tick()
  expect(result.current.status).toBe('error')
  expect(result.current.entry).toBeNull()
  expect(transport).toHaveBeenCalledTimes(1)
  failed = false
  act(() => result.current.refresh())
  await tick()
  expect(result.current.entry?.response.result_source).toBe('runtime')
  expect(transport).toHaveBeenCalledTimes(2)
})

it('makes no API calls in sample mode', async () => {
  vi.useFakeTimers()
  const transport = mockApi()
  const { result } = renderHook(() => useAnalysis('sample', demo, request()))
  await tick()
  expect(result.current.entry?.response.result_source).toBe('example')
  expect(transport).not.toHaveBeenCalled()
})

it('waits for processing before advancing replay and stops at the final event', async () => {
  vi.useFakeTimers()
  const change = vi.fn()
  const { result, rerender } = renderHook(
    ({ index, ready }) => useReplay(demo.events.events, index, change, ready),
    { initialProps: { index: 3, ready: false } },
  )
  act(() => result.current.toggle())
  await act(async () => {
    await vi.advanceTimersByTimeAsync(10000)
  })
  expect(change).not.toHaveBeenCalled()
  rerender({ index: 3, ready: true })
  await act(async () => {
    await vi.advanceTimersByTimeAsync(2001)
  })
  expect(change).toHaveBeenCalledWith(4)
  rerender({ index: 6, ready: true })
  await act(async () => {
    await vi.advanceTimersByTimeAsync(2001)
  })
  expect(change).toHaveBeenLastCalledWith(7)
  expect(result.current.playing).toBe(false)
})

it('shows API errors, then opens explicitly labelled samples without hidden processing calls', async () => {
  const transport = vi.fn(async () => {
    throw new TypeError('offline')
  })
  vi.stubGlobal('fetch', transport)
  render(<App />)
  await screen.findByRole('heading', { name: 'The match could not be loaded' })
  expect(screen.queryByText('SAMPLE DATA')).toBeNull()
  const count = transport.mock.calls.length
  fireEvent.click(screen.getByRole('button', { name: 'Use sample data' }))
  await screen.findByText('SAMPLE DATA')
  expect(transport.mock.calls.length).toBe(count)
  fireEvent.click(screen.getByRole('button', { name: 'API mode', exact: true }))
  await screen.findByRole('heading', { name: 'The match could not be loaded' })
  expect(screen.queryByText('SAMPLE DATA')).toBeNull()
  expect(transport.mock.calls.length).toBe(count + 2)
})

it.each(['azure', 'fallback'] as const)(
  'displays runtime provenance and real trace timings for %s',
  async (provider) => {
    mockApi((input) => json(runtime(input, provider)))
    render(<App />)
    await waitFor(() =>
      expect(screen.getByTestId('provenance').textContent).toContain(
        provider === 'azure' ? 'AZURE · RUNTIME' : 'MOCK FALLBACK',
      ),
    )
    expect(screen.queryByText('Sample output')).toBeNull()
    expect(screen.getAllByText('Completed · 12 ms')).toHaveLength(3)
    fireEvent.click(screen.getByRole('tab', { name: 'Trust notes' }))
    expect(
      screen.getByText(
        provider === 'azure'
          ? 'Synthetic test data.'
          : 'Azure timed out; mock fallback used.',
      ),
    ).toBeTruthy()
  },
)
