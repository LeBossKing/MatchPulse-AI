import { useEffect, useState } from 'react'
import { ApiError, fetchDemo } from '../api/client'
import type { DashboardData, DataMode } from '../types/dashboard'

type State =
  | { status: 'loading'; data: null; error: null }
  | { status: 'ready'; data: DashboardData; error: null }
  | { status: 'error'; data: null; error: ApiError }

export function useDemoData(mode: DataMode) {
  const [attempt, setAttempt] = useState(0)
  const [state, setState] = useState<State>({
    status: 'loading',
    data: null,
    error: null,
  })
  useEffect(() => {
    let active = true
    const controller = new AbortController()
    const load =
      mode === 'sample'
        ? import('../data/demo').then((module) => module.demo)
        : fetchDemo(controller.signal)
    void load
      .then((data) => {
        if (active) setState({ status: 'ready', data, error: null })
      })
      .catch((error) => {
        if (active)
          setState({
            status: 'error',
            data: null,
            error: error instanceof ApiError ? error : new ApiError('network'),
          })
      })
    return () => {
      active = false
      controller.abort()
    }
  }, [attempt, mode])
  return {
    ...state,
    retry: () => {
      setState({ status: 'loading', data: null, error: null })
      setAttempt((value) => value + 1)
    },
  }
}
