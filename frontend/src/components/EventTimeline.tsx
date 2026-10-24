import { useState } from 'react'
import type { Language, MatchEvent, MatchMetadata } from '../types/match'
import { copy, eventLabel } from '../lib/copy'
import { clock, playerName, shirtNumber } from '../lib/format'
import { Icon } from './Icon'

interface TimelineProps {
  events: MatchEvent[]
  match: MatchMetadata
  selectedIndex: number
  mainEventId: string
  language: Language
  onSelect: (index: number) => void
}

export function EventTimeline({
  events,
  match,
  selectedIndex,
  mainEventId,
  language,
  onSelect,
}: TimelineProps) {
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState('all')
  const t = copy(language)
  const filtered = events
    .map((event, index) => ({ event, index }))
    .filter(({ event }) => {
      const text =
        `${event.event_id} ${clock(event)} ${eventLabel(event, language)} ${playerName(match, event.player_id)} ${playerName(match, event.target_player_id)} ${event.team_id}`.toLocaleLowerCase()
      return (
        (filter === 'all' || event.event_type === filter) &&
        text.includes(search.toLocaleLowerCase().trim())
      )
    })

  return (
    <section className="timeline-panel panel" aria-labelledby="timeline-title">
      <div className="timeline-heading">
        <div>
          <span className="eyebrow">{t.sequence}</span>
          <h2 id="timeline-title">
            {t.timeline}{' '}
            <span className="count-pill">
              {filtered.length}/{events.length}
            </span>
          </h2>
        </div>
        <div className="timeline-filters">
          <label className="search-field">
            <Icon name="search" />
            <span className="sr-only">{t.search}</span>
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder={t.search}
            />
          </label>
          <label className="select-field">
            <span className="sr-only">{t.filter}</span>
            <select
              aria-label={t.filter}
              value={filter}
              onChange={(event) => setFilter(event.target.value)}
            >
              <option value="all">{t.allEvents}</option>
              <option value="pass">{t.pass}</option>
              <option value="interception">{t.interception}</option>
              <option value="recovery">{t.recovery}</option>
            </select>
          </label>
        </div>
      </div>
      {filtered.length ? (
        <div className="event-track" role="group" aria-label={t.timeline}>
          {filtered.map(({ event, index }) => (
            <button
              key={event.event_id}
              type="button"
              className={`event-card ${event.team_id === match.home_team.team_id ? 'atlas' : 'harbor'} ${index === selectedIndex ? 'selected' : ''}`}
              aria-pressed={index === selectedIndex}
              aria-label={`${clock(event)} · ${eventLabel(event, language)} · ${playerName(match, event.player_id)} · ${event.event_id}`}
              data-event-id={event.event_id}
              onClick={() => onSelect(index)}
            >
              <span className="event-card-top">
                <time>{clock(event)}</time>
                {event.event_id === mainEventId ? (
                  <span className="key-star" title={t.keyEvent}>
                    <Icon name="spark" />
                  </span>
                ) : (
                  <span className="event-step">
                    {String(index + 1).padStart(2, '0')}
                  </span>
                )}
              </span>
              <span
                className={`event-type ${!event.successful ? 'failed-text' : ''}`}
              >
                {eventLabel(event, language)}
              </span>
              <span className="event-players">
                {shirtNumber(event.player_id)}{' '}
                {event.event_type === 'pass' ? (
                  <>
                    <span aria-hidden="true">→</span>{' '}
                    {shirtNumber(event.target_player_id)}
                  </>
                ) : (
                  <Icon
                    name={
                      event.event_type === 'interception' ? 'target' : 'reset'
                    }
                  />
                )}
              </span>
              <span className="event-team">
                <span className="small-dot" />
                {event.team_id === match.home_team.team_id
                  ? match.home_team.name
                  : match.away_team.name}
              </span>
            </button>
          ))}
        </div>
      ) : (
        <div className="empty-state">
          <Icon name="search" />
          <p>{t.noEvents}</p>
          <button
            type="button"
            className="text-button"
            onClick={() => {
              setSearch('')
              setFilter('all')
            }}
          >
            {t.clearFilters}
          </button>
        </div>
      )}
    </section>
  )
}
