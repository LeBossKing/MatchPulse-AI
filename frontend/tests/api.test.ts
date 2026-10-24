import { afterEach, describe, expect, it, vi } from 'vitest'
import { demo } from '../src/data/demo'
import { fetchDemo, processEvent, requestJson } from '../src/api/client'
import { validateDemo, validateProcessing } from '../src/api/validation'
import { json, mockApi, request, runtime } from './helpers'

afterEach(() => {
  vi.unstubAllGlobals()
  vi.useRealTimers()
})

describe('canonical API boundary', () => {
  it('accepts backend default preferences when the selector omits them', async () => {
    mockApi()
    const response = await processEvent(
      { match_id: 'match-demo-01', event_id: 'evt-064' },
      demo,
      new AbortController().signal,
    )
    expect(response.audience).toBe('analyst')
    expect(response.language).toBe('en')
  })
  it('loads both read endpoints, then posts identifiers and presentation preferences only', async () => {
    const transport = mockApi()
    const signal = new AbortController().signal
    const data = await fetchDemo(signal)
    const input = request('evt-067', 'fan', 'fr')
    const response = await processEvent(input, data, signal)
    expect(response.validation.status).toBe('limited')
    const call = transport.mock.calls.find(([url]) =>
      String(url).endsWith('/events/process'),
    )!
    expect(call[1].method).toBe('POST')
    expect(JSON.parse(call[1].body as string)).toEqual(input)
    expect(call[1].credentials).toBe('omit')
  })

  it('accepts every event, language, and audience, including regains and unknown annotations', () => {
    for (const event of demo.events.events)
      for (const language of ['en', 'fr'])
        for (const audience of ['fan', 'analyst']) {
          const input = request(event.event_id, audience, language)
          expect(validateProcessing(runtime(input), input, demo).event_id).toBe(
            event.event_id,
          )
        }
  })

  it.each([
    'empty',
    'duplicate',
    'foreign_match',
    'unknown_player',
    'chronology',
    'missing_key_event',
    'wrong_shape',
  ])('rejects invalid bootstrap data: %s', (kind) => {
    const events = structuredClone(demo.events)
    if (kind === 'empty') events.events = []
    if (kind === 'duplicate')
      events.events[1].event_id = events.events[0].event_id
    if (kind === 'foreign_match') events.match_id = 'different-match'
    if (kind === 'unknown_player') events.events[0].player_id = 'missing-player'
    if (kind === 'chronology') events.events.reverse()
    if (kind === 'missing_key_event') events.main_event_id = 'missing-event'
    if (kind === 'wrong_shape')
      return expect(() => validateDemo({}, events)).toThrow()
    expect(() => validateDemo(demo.match, events)).toThrow()
  })

  it.each([
    'example',
    'wrong_event',
    'wrong_audience',
    'wrong_language',
    'wrong_metrics',
    'wrong_prefix',
    'wrong_evidence',
    'wrong_trace',
    'wrong_provider',
    'wrong_shape',
  ])('rejects unsafe processing payload: %s', (kind) => {
    const input = request(),
      value = runtime(input)
    if (kind === 'example') value.result_source = 'example'
    if (kind === 'wrong_event') value.event.start.x += 1
    if (kind === 'wrong_audience') value.audience = 'fan'
    if (kind === 'wrong_language') value.language = 'fr'
    if (kind === 'wrong_metrics') value.statistics.pass_length = 400
    if (kind === 'wrong_prefix')
      value.match_statistics.teams[0].passes_completed = 1
    if (kind === 'wrong_evidence') value.evidence[5].value = 1
    if (kind === 'wrong_trace') value.agent_trace.reverse()
    if (kind === 'wrong_provider') value.provider = 'azure'
    if (kind === 'wrong_shape')
      return expect(() =>
        validateProcessing({ status: 'processed' }, input, demo),
      ).toThrow()
    expect(() => validateProcessing(value, input, demo)).toThrow()
  })

  it('preserves a rejected insight and a visible backend fallback as explicit outcomes', () => {
    const input = request(),
      fallback = runtime(input, 'fallback')
    expect(validateProcessing(fallback, input, demo).provider).toBe('fallback')
    const rejected = runtime(input, 'azure')
    rejected.insight = null
    rejected.validation.status = 'rejected'
    rejected.validation.unsupported_claims = ['Conflicting provider claim']
    expect(validateProcessing(rejected, input, demo).insight).toBeNull()
  })

  it('reports safe structured HTTP errors and never retries automatically', async () => {
    const transport = mockApi(() =>
      json(
        {
          schema_version: '1.0.0',
          error: {
            code: 'event_not_found',
            message: 'private-upstream-message',
          },
        },
        404,
      ),
    )
    await expect(
      processEvent(request(), demo, new AbortController().signal),
    ).rejects.toMatchObject({
      kind: 'http',
      status: 404,
      code: 'event_not_found',
    })
    expect(transport).toHaveBeenCalledTimes(1)
  })

  it('classifies HTML, network, timeout, and user cancellation separately', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(
        async () => new Response('<html>private-body</html>', { status: 200 }),
      ),
    )
    await expect(
      requestJson('/matches/demo', new AbortController().signal),
    ).rejects.toMatchObject({ kind: 'invalid_response' })
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => {
        throw new TypeError('private-network-detail')
      }),
    )
    await expect(
      requestJson('/matches/demo', new AbortController().signal),
    ).rejects.toMatchObject({ kind: 'network' })
    vi.useFakeTimers()
    vi.stubGlobal(
      'fetch',
      vi.fn(
        (_url, init) =>
          new Promise((_resolve, reject) => {
            init.signal.addEventListener('abort', () =>
              reject(new DOMException('aborted', 'AbortError')),
            )
          }),
      ),
    )
    const pending = requestJson(
      '/matches/demo',
      new AbortController().signal,
      undefined,
      30,
    )
    const check = expect(pending).rejects.toMatchObject({ kind: 'timeout' })
    await vi.advanceTimersByTimeAsync(31)
    await check
    const controller = new AbortController()
    const canceled = requestJson('/matches/demo', controller.signal)
    controller.abort()
    await expect(canceled).rejects.toMatchObject({ name: 'AbortError' })
  })
})
