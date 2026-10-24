import { useEffect, useState } from 'react'
import type { MatchEvent } from '../types/match'

export function useReplay(events: MatchEvent[], initialIndex: number) {
  const [state, setState] = useState({ index: initialIndex, playing: false })
  const [speed, setSpeed] = useState(2)
  const lastIndex = events.length - 1

  useEffect(() => {
    if (!state.playing || state.index >= lastIndex) return
    const current = events[state.index]
    const next = events[state.index + 1]
    const seconds = Math.max(
      1,
      (next.minute - current.minute) * 60 + next.second - current.second,
    )
    const timer = window.setTimeout(
      () => {
        setState((previous) => {
          const index = Math.min(previous.index + 1, lastIndex)
          return { index, playing: index < lastIndex }
        })
      },
      (seconds * 1000) / speed,
    )
    return () => window.clearTimeout(timer)
  }, [events, lastIndex, speed, state.index, state.playing])

  function select(index: number) {
    setState({ index: Math.max(0, Math.min(index, lastIndex)), playing: false })
  }

  function toggle() {
    setState((previous) => ({
      index: previous.index === lastIndex ? 0 : previous.index,
      playing: !previous.playing,
    }))
  }

  return { ...state, speed, setSpeed, select, toggle, lastIndex }
}
