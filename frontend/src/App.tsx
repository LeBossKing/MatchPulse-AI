import { useEffect, useState } from 'react'
import type { AnalysisTab } from './types/dashboard'
import type { Audience, Language } from './types/match'
import { demo, selectSample } from './data/demo'
import { copy, eventLabel } from './lib/copy'
import { clock, formatNumber, playerName } from './lib/format'
import { useReplay } from './hooks/useReplay'
import { AgentWorkflow } from './components/AgentWorkflow'
import { AnalysisPanel } from './components/AnalysisPanel'
import { ConnectionCard } from './components/ConnectionCard'
import { EventTimeline } from './components/EventTimeline'
import { Icon } from './components/Icon'
import { Pitch } from './components/Pitch'
import { SequenceStats } from './components/SequenceStats'
import './App.css'

function App() {
  const [language, setLanguage] = useState<Language>('en')
  const [audience, setAudience] = useState<Audience>('analyst')
  const [activeTab, setActiveTab] = useState<AnalysisTab>('insight')
  const [showTrails, setShowTrails] = useState(false)
  const [diagnostics, setDiagnostics] = useState(false)
  const { match } = demo.match
  const events = demo.events.events
  const mainIndex = events.findIndex(
    (event) => event.event_id === demo.events.main_event_id,
  )
  const replay = useReplay(events, mainIndex)
  const event = events[replay.index]
  const response = selectSample(event.event_id, audience, language)
  const t = copy(language)

  useEffect(() => {
    document.documentElement.lang = language
    document.title = `MatchPulse AI · ${match.home_team.name} vs ${match.away_team.name}`
  }, [language, match])

  function selectEvent(index: number) {
    replay.select(index)
  }

  return (
    <div className="app-shell">
      <a className="skip-link" href="#match-workspace">
        {t.skip}
      </a>
      <aside className="sidebar" aria-label="MatchPulse AI">
        <a className="brand" href="#match-workspace" aria-label="MatchPulse AI">
          <svg viewBox="0 0 32 32" fill="none" aria-hidden="true">
            <rect x="1" y="1" width="30" height="30" rx="9" />
            <path d="M6 17h5l3-7 4 13 3-6h5" />
          </svg>
          <span>
            MatchPulse<span className="brand-ai"> AI</span>
          </span>
        </a>
        <span className="sidebar-label">{t.demoWorkspace}</span>
        <nav className="sidebar-nav">
          <a
            className="nav-item current"
            href="#match-workspace"
            aria-label={t.workspace}
          >
            <Icon name="pitch" />
            <span>{t.workspace}</span>
          </a>
          <a
            className="nav-item"
            href="#analysis-panel"
            aria-label={t.evidenceLibrary}
            onClick={() => setActiveTab('evidence')}
          >
            <Icon name="layers" />
            <span>{t.evidenceLibrary}</span>
          </a>
          <a
            className="nav-item"
            href="#agent-workflow"
            aria-label={t.agentWorkflow}
          >
            <Icon name="flow" />
            <span>{t.agentWorkflow}</span>
          </a>
          <a
            className="nav-item"
            href="#api-connection"
            aria-label={t.apiConnection}
            onClick={() => setDiagnostics(true)}
          >
            <Icon name="plug" />
            <span>{t.apiConnection}</span>
          </a>
        </nav>
        <div className="sidebar-bottom">
          <div className="demo-emblem">
            <Icon name="spark" />
          </div>
          <p>{t.synthetic}</p>
          <span>
            {demo.match.review_status === 'approved' ? t.approved : t.pending}
          </span>
          <details className="about-demo">
            <summary>
              {t.about}
              <Icon name="chevron" />
            </summary>
            <p>{t.aboutText}</p>
            <p>{t.sampleHelp}</p>
          </details>
        </div>
        <span className="sidebar-version">MATCHPULSE / 05</span>
      </aside>

      <main id="match-workspace" className="main-workspace" tabIndex={-1}>
        <header className="workspace-topbar">
          <span className="breadcrumb">{t.breadcrumb}</span>
          <span className="sample-badge">
            <span className="small-dot" />
            {t.sampleData}
          </span>
        </header>
        <div className="page-heading">
          <div>
            <h1>
              {t.headline}
              <span className="heading-dot">.</span>
            </h1>
            <p>{t.intro}</p>
          </div>
          <div className="preferences">
            <fieldset className="preference-group">
              <legend>{t.audience}</legend>
              <div className="segmented">
                {(['analyst', 'fan'] as const).map((value) => (
                  <button
                    type="button"
                    key={value}
                    aria-pressed={audience === value}
                    onClick={() => setAudience(value)}
                  >
                    {t[value]}
                  </button>
                ))}
              </div>
            </fieldset>
            <fieldset className="preference-group language-control">
              <legend>{t.language}</legend>
              <div className="segmented">
                {(['en', 'fr'] as const).map((value) => (
                  <button
                    type="button"
                    key={value}
                    lang={value}
                    aria-pressed={language === value}
                    aria-label={value === 'en' ? 'English' : 'Français'}
                    onClick={() => setLanguage(value)}
                  >
                    {value.toUpperCase()}
                  </button>
                ))}
              </div>
            </fieldset>
          </div>
        </div>

        <section
          className="match-banner panel"
          aria-label={`${match.home_team.name} ${match.score.home}–${match.score.away} ${match.away_team.name}`}
        >
          <div className="match-team home-team">
            <div className="team-crest atlas" aria-hidden="true">
              A<span>FC</span>
            </div>
            <div>
              <span className="eyebrow">{t.home}</span>
              <h2>{match.home_team.name}</h2>
            </div>
          </div>
          <div className="match-score">
            <div>
              {match.score.home}
              <span>:</span>
              {match.score.away}
            </div>
            <span className="match-clock" data-testid="match-clock">
              {clock(event)}
              <span> / {t.secondHalf}</span>
            </span>
          </div>
          <div className="match-team away-team">
            <div>
              <span className="eyebrow">{t.away}</span>
              <h2>{match.away_team.name}</h2>
            </div>
            <div className="team-crest harbor" aria-hidden="true">
              H<span>FC</span>
            </div>
          </div>
          <div className="match-provenance">
            <span>
              <span className="small-dot" />
              {t.synthetic}
            </span>
            <span>{t.sampleNote}</span>
            <span>63:08–63:38</span>
          </div>
        </section>

        <div className="analysis-grid">
          <section className="pitch-panel panel" aria-labelledby="pitch-title">
            <div className="pitch-heading">
              <div>
                <span className="eyebrow">{t.pitchTitle}</span>
                <h2 id="pitch-title">{t.pitchView}</h2>
              </div>
              <button
                type="button"
                className="key-event-button"
                onClick={() => selectEvent(mainIndex)}
              >
                <Icon name="spark" />
                {t.keyMoment}
              </button>
            </div>
            <div className="selected-event-heading">
              <span
                className={`event-outcome ${!event.successful ? 'failed' : event.team_id === match.away_team.team_id ? 'harbor' : ''}`}
              >
                <span className="small-dot" />
                {eventLabel(event, language)}
              </span>
              <span className="selected-players">
                {playerName(match, event.player_id)}
                {event.target_player_id && (
                  <>
                    {' '}
                    <span>→</span> {playerName(match, event.target_player_id)}
                  </>
                )}
              </span>
              <code>{event.event_id}</code>
            </div>
            <Pitch
              match={match}
              event={event}
              previous={events.slice(0, replay.index)}
              language={language}
              showTrails={showTrails}
            />
            <div className="pitch-options">
              <label>
                <input
                  type="checkbox"
                  checked={showTrails}
                  onChange={(change) => setShowTrails(change.target.checked)}
                />
                {t.trails}
              </label>
              <span>
                {t.pressure}:{' '}
                <strong>
                  {event.pressure ? t[event.pressure] : t.unknown}
                </strong>
              </span>
            </div>
            <div className="event-metrics" aria-label={t.insight}>
              <div>
                <span>{t.passLength}</span>
                <strong data-testid="pass-length">
                  {formatNumber(response.statistics.pass_length, language)}
                </strong>
                <small>
                  {event.event_type === 'pass'
                    ? t.normalizedUnits
                    : t.notApplicable}
                </small>
              </div>
              <div>
                <span>{t.progression}</span>
                <strong
                  className={
                    response.statistics.forward_progression !== null &&
                    response.statistics.forward_progression < 0
                      ? 'muted'
                      : 'lime-text'
                  }
                  data-testid="progression"
                >
                  {formatNumber(
                    response.statistics.forward_progression,
                    language,
                    true,
                  )}
                </strong>
                <small>
                  {event.event_type === 'pass'
                    ? t.normalizedUnits
                    : t.notApplicable}
                </small>
              </div>
              <div>
                <span>{t.lines}</span>
                <strong data-testid="lines-bypassed">
                  {event.event_type !== 'pass'
                    ? '—'
                    : event.lines_broken === null
                      ? '?'
                      : event.lines_broken}
                </strong>
                <small>
                  {event.event_type !== 'pass'
                    ? t.notApplicable
                    : event.lines_broken === null
                      ? t.unknown
                      : t.sourceAnnotation}
                </small>
              </div>
            </div>
            <div className="replay-controls">
              <div className="replay-buttons">
                <button
                  type="button"
                  className="icon-button"
                  aria-label={t.previous}
                  disabled={replay.index === 0}
                  onClick={() => selectEvent(replay.index - 1)}
                >
                  <Icon name="previous" />
                </button>
                <button
                  type="button"
                  className="play-button"
                  aria-label={replay.playing ? t.pause : t.play}
                  onClick={replay.toggle}
                >
                  <Icon name={replay.playing ? 'pause' : 'play'} />
                </button>
                <button
                  type="button"
                  className="icon-button"
                  aria-label={t.next}
                  disabled={replay.index === replay.lastIndex}
                  onClick={() => selectEvent(replay.index + 1)}
                >
                  <Icon name="next" />
                </button>
              </div>
              <input
                className="replay-seek"
                type="range"
                min={0}
                max={replay.lastIndex}
                value={replay.index}
                aria-label={t.seek}
                aria-valuetext={`${clock(event)} · ${eventLabel(event, language)}`}
                onChange={(change) => selectEvent(Number(change.target.value))}
              />
              <span className="replay-count mono">
                {String(replay.index + 1).padStart(2, '0')}
                <span> / {String(events.length).padStart(2, '0')}</span>
              </span>
              <select
                className="speed-select"
                value={replay.speed}
                aria-label={t.replaySpeed}
                onChange={(change) =>
                  replay.setSpeed(Number(change.target.value))
                }
              >
                <option value={1}>1×</option>
                <option value={2}>2×</option>
                <option value={4}>4×</option>
              </select>
              <button
                type="button"
                className="icon-button reset-button"
                aria-label={t.reset}
                onClick={() => selectEvent(0)}
              >
                <Icon name="reset" />
              </button>
            </div>
          </section>
          <aside className="insight-column">
            <AnalysisPanel
              response={response}
              language={language}
              activeTab={activeTab}
              onTabChange={setActiveTab}
            />
            <SequenceStats
              match={match}
              response={response}
              language={language}
            />
          </aside>
        </div>

        <EventTimeline
          events={events}
          match={match}
          selectedIndex={replay.index}
          mainEventId={demo.events.main_event_id}
          language={language}
          onSelect={selectEvent}
        />
        <AgentWorkflow response={response} language={language} />
        {diagnostics && (
          <section
            id="api-connection"
            className="diagnostics-section"
            aria-label={t.diagnostics}
          >
            <div className="section-heading">
              <h2>{t.diagnostics}</h2>
              <button
                type="button"
                className="icon-button"
                aria-label={t.closeDiagnostics}
                onClick={() => setDiagnostics(false)}
              >
                <Icon name="close" />
              </button>
            </div>
            <ConnectionCard language={language} />
          </section>
        )}
        <footer>
          <span>
            MatchPulse<span className="lime-text"> AI</span>
            <span className="footer-line"> / </span>
            {t.footer}
          </span>
          <span>
            {t.synthetic} ·{' '}
            {demo.match.review_status === 'approved' ? t.approved : t.pending}
          </span>
        </footer>
      </main>
    </div>
  )
}

export default App
