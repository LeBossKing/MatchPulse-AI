import { useEffect, useRef, useState } from 'react'
import { ApiError, processEvent } from '../api/client'
import type {
  DashboardData,
  DashboardSamples,
  DataMode,
} from '../types/dashboard'
import type { ProcessEventRequest, ProcessEventResponse } from '../types/match'

interface Entry {
  response: ProcessEventResponse
  receivedAt: number
}
type State =
  | { key: string; status: 'loading'; entry: null; error: null; cached: false }
  | { key: string; status: 'ready'; entry: Entry; error: null; cached: boolean }
  | {
      key: string
      status: 'error'
      entry: null
      error: ApiError
      cached: false
    }
const loading = (key: string): State => ({
  key,
  status: 'loading',
  entry: null,
  error: null,
  cached: false,
})
export const ANALYSIS_DEBOUNCE_MS = 200
export const CACHE_TTL_MS = 5 * 60 * 1000

export function useAnalysis(
  mode: DataMode,
  data: DashboardData,
  request: ProcessEventRequest,
) {
  const { match_id, event_id } = request
  const audience = request.audience ?? 'analyst'
  const language = request.language ?? 'en'
  const key = JSON.stringify([match_id, event_id, audience, language])
  const cache = useRef(new Map<string, Entry>())
  const [attempt, setAttempt] = useState(0)
  const [state, setState] = useState<State>(() => loading(key))
  useEffect(() => {
    if (mode === 'sample') return
    let active = true
    const controller = new AbortController()
    const previous = cache.current.get(key)
    if (previous && Date.now() - previous.receivedAt < CACHE_TTL_MS) {
      setState({
        key,
        status: 'ready',
        entry: previous,
        cached: true,
        error: null,
      })
      return () => {
        active = false
        controller.abort()
      }
    }
    setState(loading(key))
    // Coalesce quick navigation and React StrictMode's setup/cleanup cycle
    // before starting a potentially billable POST.
    const timer = window.setTimeout(() => {
      void processEvent(
        { match_id, event_id, audience, language },
        data,
        controller.signal,
      )
        .then((response) => {
          if (!active) return
          const entry = { response, receivedAt: Date.now() }
          cache.current.delete(key)
          cache.current.set(key, entry)
          if (cache.current.size > 64)
            cache.current.delete(cache.current.keys().next().value!)
          setState({ key, status: 'ready', entry, cached: false, error: null })
        })
        .catch((error) => {
          if (active)
            setState({
              key,
              status: 'error',
              entry: null,
              error:
                error instanceof ApiError ? error : new ApiError('network'),
              cached: false,
            })
        })
    }, ANALYSIS_DEBOUNCE_MS)
    return () => {
      active = false
      window.clearTimeout(timer)
      controller.abort()
    }
  }, [mode, data, key, match_id, event_id, audience, language, attempt])

  const sample =
    mode === 'sample'
      ? (data as DashboardSamples).responses.find(
          (item) =>
            item.event_id === event_id &&
            item.audience === audience &&
            item.language === language,
        )
      : null
  const current =
    mode === 'sample' && sample
      ? {
          key,
          status: 'ready' as const,
          entry: { response: sample, receivedAt: 0 },
          error: null,
          cached: false,
        }
      : state.key === key
        ? state
        : loading(key)
  return {
    ...current,
    refresh: () => {
      cache.current.delete(key)
      setState(loading(key))
      setAttempt((value) => value + 1)
    },
  }
}
