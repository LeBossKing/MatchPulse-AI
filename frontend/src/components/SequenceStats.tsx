import type {
  Language,
  MatchMetadata,
  ProcessEventResponse,
} from '../types/match'
import { copy } from '../lib/copy'
import { clock, formatNumber } from '../lib/format'

export function SequenceStats({
  match,
  response,
  language,
}: {
  match: MatchMetadata
  response: ProcessEventResponse
  language: Language
}) {
  const t = copy(language)
  return (
    <section className="sequence-stats panel" aria-labelledby="snapshot-title">
      <div className="panel-heading">
        <h2 id="snapshot-title">{t.snapshot}</h2>
        <span className="mono muted">{clock(response.event)}</span>
      </div>
      <p className="stats-scope">
        {response.match_statistics.event_count}{' '}
        {language === 'fr' ? 'actions' : 'events'} · {t.snapshotNote}
      </p>
      <div className="team-stats-grid">
        {response.match_statistics.teams.map((team) => {
          const home = team.team_id === match.home_team.team_id
          return (
            <div
              className={`team-stats ${home ? 'atlas' : 'harbor'}`}
              key={team.team_id}
            >
              <h3>
                <span className="small-dot" />
                {home ? match.home_team.name : match.away_team.name}
              </h3>
              <div className="pass-total">
                <span>{t.passes}</span>
                <strong data-testid={`passes-${team.team_id}`}>
                  {team.passes_completed}
                  <span>/{team.passes_attempted}</span>
                </strong>
              </div>
              <div className="accuracy-track" aria-hidden="true">
                <span style={{ width: `${team.pass_accuracy_pct ?? 0}%` }} />
              </div>
              <p className="accuracy-label">
                {team.pass_accuracy_pct === null
                  ? t.noAttempts
                  : `${formatNumber(team.pass_accuracy_pct, language)}%`}
              </p>
              <dl>
                <div>
                  <dt>{t.interceptions}</dt>
                  <dd>{team.interceptions}</dd>
                </div>
                <div>
                  <dt>{t.recoveries}</dt>
                  <dd>{team.recoveries}</dd>
                </div>
              </dl>
            </div>
          )
        })}
      </div>
    </section>
  )
}
