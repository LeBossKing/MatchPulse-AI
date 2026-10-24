export type IconName =
  | 'pitch'
  | 'layers'
  | 'flow'
  | 'plug'
  | 'arrow'
  | 'play'
  | 'pause'
  | 'previous'
  | 'next'
  | 'reset'
  | 'check'
  | 'info'
  | 'search'
  | 'close'
  | 'chevron'
  | 'spark'
  | 'target'

const paths: Record<IconName, string> = {
  pitch:
    'M3 5h18v14H3z M12 5v14 M3 9h4v6H3 M21 9h-4v6h4 M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0',
  layers: 'm12 3 9 5-9 5-9-5 9-5 M3 12l9 5 9-5 M3 16l9 5 9-5',
  flow: 'M5 5h5v5H5z M14 14h5v5h-5z M10 7h6v7 M7 10v7h7',
  plug: 'M8 3v5 M16 3v5 M6 8h12v3a6 6 0 0 1-12 0V8 M12 17v4',
  arrow: 'M5 12h14 M14 7l5 5-5 5',
  play: 'm9 5 11 7-11 7V5',
  pause: 'M8 5v14 M16 5v14',
  previous: 'M6 5v14 M18 5l-9 7 9 7V5',
  next: 'M18 5v14 M6 5l9 7-9 7V5',
  reset: 'M4 4v6h6 M4 10a8 8 0 1 1 1 7',
  check: 'm5 12 4 4L19 6',
  info: 'M12 11v6 M12 7h.01 M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0',
  search: 'm15 15 5 5 M17 10a7 7 0 1 1-14 0 7 7 0 0 1 14 0',
  close: 'm6 6 12 12 M18 6 6 18',
  chevron: 'm6 9 6 6 6-6',
  spark: 'm12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5L12 3',
  target:
    'M12 3v4 M12 17v4 M3 12h4 M17 12h4 M18 12a6 6 0 1 1-12 0 6 6 0 0 1 12 0',
}

export function Icon({
  name,
  className = '',
}: {
  name: IconName
  className?: string
}) {
  return (
    <svg
      className={`icon ${className}`}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d={paths[name]} />
    </svg>
  )
}
