import { useId } from 'react'
import type { Language, MatchEvent, MatchMetadata } from '../types/match'
import { copy, eventLabel } from '../lib/copy'
import { clock, shirtNumber } from '../lib/format'

interface PitchProps {
  match: MatchMetadata
  event: MatchEvent
  previous: MatchEvent[]
  language: Language
  showTrails: boolean
}

export function Pitch({
  match,
  event,
  previous,
  language,
  showTrails,
}: PitchProps) {
  const id = useId().replace(/:/g, '')
  const t = copy(language)
  const home = event.team_id === match.home_team.team_id
  const color = event.successful ? (home ? '#c3f36a' : '#b9a4f5') : '#ee9c90'
  const x1 = event.start.x * 10.5
  const y1 = event.start.y * 6.8
  const x2 = event.end ? event.end.x * 10.5 : x1
  const y2 = event.end ? event.end.y * 6.8 : y1
  const team = home ? match.home_team.name : match.away_team.name
  const direction = event.attacking_direction === 'left_to_right'

  return (
    <figure className="pitch-figure">
      <svg
        className="pitch-svg"
        viewBox="-35 -28 1120 745"
        role="img"
        aria-labelledby={`${id}-title ${id}-description`}
      >
        <title id={`${id}-title`}>
          {eventLabel(event, language)} · {clock(event)}
        </title>
        <desc id={`${id}-description`}>
          {t.startPoint}: ({event.start.x}, {event.start.y}).{' '}
          {event.end ? `${t.endPoint}: (${event.end.x}, ${event.end.y}).` : ''}{' '}
          {t.coordinates}.
        </desc>
        <defs>
          <pattern
            id={`${id}-stripes`}
            width="210"
            height="680"
            patternUnits="userSpaceOnUse"
          >
            <rect width="105" height="680" fill="#a3c0ac" opacity=".035" />
          </pattern>
          <marker
            id={`${id}-arrow`}
            viewBox="0 0 12 12"
            refX="10"
            refY="6"
            markerWidth="5"
            markerHeight="5"
            orient="auto-start-reverse"
          >
            <path d="M1 1 11 6 1 11z" fill={color} />
          </marker>
          <radialGradient id={`${id}-spot`}>
            <stop stopColor={color} stopOpacity=".16" />
            <stop offset="1" stopColor={color} stopOpacity="0" />
          </radialGradient>
        </defs>
        <rect width="1050" height="680" rx="4" fill="#15372c" />
        <rect width="1050" height="680" fill={`url(#${id}-stripes)`} />
        <g
          className="pitch-markings"
          fill="none"
          stroke="#83a18c"
          strokeWidth="1.8"
          opacity=".47"
        >
          <rect x="1" y="1" width="1048" height="678" rx="3" />
          <path d="M525 0v680" />
          <circle cx="525" cy="340" r="91.5" />
          <circle cx="525" cy="340" r="3.5" fill="#83a18c" stroke="none" />
          <path d="M0 138.5h165v403H0 M1050 138.5H885v403h165 M0 248.5h55v183H0 M1050 248.5h-55v183h55" />
          <circle cx="110" cy="340" r="3.5" fill="#83a18c" stroke="none" />
          <circle cx="940" cy="340" r="3.5" fill="#83a18c" stroke="none" />
          <path d="M165 267a91.5 91.5 0 0 1 0 146 M885 267a91.5 91.5 0 0 0 0 146 M0 14a14 14 0 0 0 14-14 M1036 0a14 14 0 0 0 14 14 M0 666a14 14 0 0 1 14 14 M1036 680a14 14 0 0 1 14-14" />
          <path d="M-12 303H0v74h-12z M1050 303h12v74h-12z" />
        </g>
        <g aria-hidden="true" className="pitch-coordinates">
          {[0, 25, 50, 75, 100].map((value) => (
            <text key={value} x={value * 10.5} y="708" textAnchor="middle">
              {value}
            </text>
          ))}
        </g>
        {showTrails && (
          <g
            fill="none"
            stroke="#9ab7a4"
            strokeWidth="2.5"
            strokeDasharray="5 8"
            opacity=".34"
            aria-hidden="true"
          >
            {previous.map(
              (item) =>
                item.end && (
                  <path
                    key={item.event_id}
                    d={`M${item.start.x * 10.5} ${item.start.y * 6.8}L${item.end.x * 10.5} ${item.end.y * 6.8}`}
                  />
                ),
            )}
          </g>
        )}
        <g key={event.event_id} className="selected-action">
          <circle cx={x1} cy={y1} r="100" fill={`url(#${id}-spot)`} />
          {event.end && (
            <>
              <path
                d={`M${x1} ${y1}L${x2} ${y2}`}
                stroke={color}
                strokeWidth="16"
                opacity=".075"
              />
              <path
                className="pass-trajectory"
                data-testid="pass-trajectory"
                data-successful={event.successful}
                d={`M${x1} ${y1}L${x2} ${y2}`}
                stroke={color}
                strokeWidth="4.5"
                fill="none"
                strokeDasharray={event.successful ? undefined : '11 8'}
                markerEnd={`url(#${id}-arrow)`}
              />
              <circle
                cx={x2}
                cy={y2}
                r="16"
                stroke={color}
                fill="#17392d"
                strokeWidth="2.5"
              />
              {event.successful ? (
                <circle cx={x2} cy={y2} r="5" fill={color} />
              ) : (
                <path
                  d={`M${x2 - 5} ${y2 - 5}l10 10m0-10-10 10`}
                  stroke={color}
                  strokeWidth="2"
                />
              )}
              <text
                className="endpoint-label"
                x={x2}
                y={y2 - 29}
                textAnchor="middle"
                fill={color}
              >
                {t.endPoint}
              </text>
            </>
          )}
          <circle
            cx={x1}
            cy={y1}
            r="27"
            fill={color}
            stroke="#10251d"
            strokeWidth="5"
          />
          <text x={x1} y={y1 + 6} textAnchor="middle" className="player-number">
            {shirtNumber(event.player_id)}
          </text>
          {event.event_type !== 'pass' && (
            <circle
              data-testid="point-overlay"
              cx={x1}
              cy={y1}
              r="42"
              fill="none"
              stroke={color}
              strokeWidth="1.5"
              opacity=".6"
            />
          )}
        </g>
      </svg>
      <figcaption>
        <span>{t.coordinates}</span>
        <span className={home ? 'atlas-text' : 'harbor-text'}>
          {!direction && '← '}
          {team} {t.attacks}
          {direction && ' →'}
        </span>
      </figcaption>
    </figure>
  )
}
