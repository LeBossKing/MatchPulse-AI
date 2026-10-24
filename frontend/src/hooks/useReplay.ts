import { useCallback, useEffect, useState } from 'react'
import type { MatchEvent } from '../types/match'

export function useReplay(
  events: MatchEvent[],
  index: number,
  onIndexChange: (index: number) => void,
  ready = true,
) {
  const [playing, setPlaying] = useState(false)
  const [speed, setSpeed] = useState(2)
  const lastIndex = events.length - 1
  const pause = useCallback(() => setPlaying(false), [])

  useEffect(() => {
    if (!playing || !ready || index >= lastIndex) return
    const current = events[index],
      next = events[index + 1]
    const seconds = Math.max(
      1,
      (next.minute - current.minute) * 60 + next.second - current.second,
    )
    const timer = window.setTimeout(
      () => {
        const nextIndex = Math.min(index + 1, lastIndex)
        onIndexChange(nextIndex)
        if (nextIndex === lastIndex) setPlaying(false)
      },
      (seconds * 1000) / speed,
    )
    return () => window.clearTimeout(timer)
  }, [events, lastIndex, speed, index, playing, ready, onIndexChange])

  function select(nextIndex: number) {
    setPlaying(false)
    onIndexChange(Math.max(0, Math.min(nextIndex, lastIndex)))
  }
  function toggle() {
    if (index === lastIndex) onIndexChange(0)
    setPlaying((previous) => !previous)
  }
  return { index, playing, speed, setSpeed, select, toggle, pause, lastIndex }
}
