import { useRef } from 'react'
import type { KeyboardEvent } from 'react'
import type { AnalysisTab } from '../types/dashboard'
import type {
  EvidenceItem,
  Language,
  ProcessEventResponse,
} from '../types/match'
import { copy } from '../lib/copy'
import { formatNumber } from '../lib/format'
import { Icon } from './Icon'

const tabs: AnalysisTab[] = ['insight', 'evidence', 'checks']

function EvidenceTable({
  items,
  language,
}: {
  items: EvidenceItem[]
  language: Language
}) {
  const t = copy(language)
  return (
    <table className="evidence-table">
      <thead>
        <tr>
          <th scope="col">{t.field}</th>
          <th scope="col">{t.value}</th>
        </tr>
      </thead>
      <tbody>
        {items.map((item) => (
          <tr key={item.evidence_id}>
            <th scope="row">
              <code>{item.field}</code>
            </th>
            <td>
              {typeof item.value === 'number'
                ? formatNumber(item.value, language)
                : typeof item.value === 'boolean'
                  ? item.value
                    ? t.trueValue
                    : t.falseValue
                  : item.value}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

interface AnalysisProps {
  response: ProcessEventResponse
  language: Language
  activeTab: AnalysisTab
  onTabChange: (tab: AnalysisTab) => void
}

export function AnalysisPanel({
  response,
  language,
  activeTab,
  onTabChange,
}: AnalysisProps) {
  const t = copy(language)
  const refs = useRef<(HTMLButtonElement | null)[]>([])
  const status = response.validation.status
  const statusText =
    status === 'validated'
      ? t.checksPassed
      : status === 'limited'
        ? t.limitedContext
        : t.rejected

  function navigateTabs(
    event: KeyboardEvent<HTMLButtonElement>,
    index: number,
  ) {
    let next = index
    if (event.key === 'ArrowRight') next = (index + 1) % tabs.length
    else if (event.key === 'ArrowLeft')
      next = (index + tabs.length - 1) % tabs.length
    else if (event.key === 'Home') next = 0
    else if (event.key === 'End') next = tabs.length - 1
    else return
    event.preventDefault()
    onTabChange(tabs[next])
    refs.current[next]?.focus()
  }

  return (
    <section
      className="analysis-panel panel"
      id="analysis-panel"
      aria-labelledby="analysis-title"
    >
      <div className="panel-heading">
        <span className="eyebrow" id="analysis-title">
          {t.analysis}
        </span>
        <Icon name="spark" className="lime-icon" />
      </div>
      <div className="analysis-tabs" role="tablist" aria-label={t.analysis}>
        {tabs.map((tab, index) => (
          <button
            key={tab}
            id={`tab-${tab}`}
            type="button"
            role="tab"
            aria-selected={activeTab === tab}
            aria-controls={`panel-${tab}`}
            tabIndex={activeTab === tab ? 0 : -1}
            ref={(element) => {
              refs.current[index] = element
            }}
            onClick={() => onTabChange(tab)}
            onKeyDown={(event) => navigateTabs(event, index)}
          >
            {t[tab]}
            {tab === 'evidence' && <span>{response.evidence.length}</span>}
          </button>
        ))}
      </div>
      <div
        id="panel-insight"
        className="analysis-content"
        role="tabpanel"
        aria-labelledby="tab-insight"
        tabIndex={0}
        hidden={activeTab !== 'insight'}
      >
        {response.insight ? (
          <>
            <span className={`importance-tag ${response.insight.importance}`}>
              <span className="small-dot" />
              {t.importance}: {t[response.insight.importance]}
            </span>
            <h2 className="insight-title">{response.insight.title}</h2>
            <p className="insight-explanation">
              {response.insight.explanation}
            </p>
            <div className="interpretation">
              <span>
                <Icon name="layers" />
                {t.interpretation}
              </span>
              <p>{response.insight.interpretation}</p>
            </div>
          </>
        ) : (
          <div className="empty-state">
            <Icon name="info" />
            <h2>{t.rejected}</h2>
            <p>{t.unavailable}</p>
          </div>
        )}
      </div>
      <div
        id="panel-evidence"
        className="analysis-content evidence-content"
        role="tabpanel"
        aria-labelledby="tab-evidence"
        tabIndex={0}
        hidden={activeTab !== 'evidence'}
      >
        <p className="panel-description">{t.evidenceIntro}</p>
        <h3>{t.eventFacts}</h3>
        <EvidenceTable
          items={response.evidence.filter((item) => item.source === 'event')}
          language={language}
        />
        {response.evidence.some((item) => item.source === 'statistics') && (
          <>
            <h3>{t.calculatedFacts}</h3>
            <EvidenceTable
              items={response.evidence.filter(
                (item) => item.source === 'statistics',
              )}
              language={language}
            />
          </>
        )}
        <details className="json-details">
          <summary>{t.rawSource}</summary>
          <pre>{JSON.stringify(response.event, null, 2)}</pre>
        </details>
      </div>
      <div
        id="panel-checks"
        className="analysis-content"
        role="tabpanel"
        aria-labelledby="tab-checks"
        tabIndex={0}
        hidden={activeTab !== 'checks'}
      >
        <p className="panel-description">{t.trustIntro}</p>
        <h3>{t.limitations}</h3>
        <ul className="limitations-list">
          {response.validation.limitations.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
        {response.validation.unsupported_claims.length > 0 && (
          <>
            <h3>{t.unsupported}</h3>
            <ul className="limitations-list">
              {response.validation.unsupported_claims.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </>
        )}
        <p className="review-note">
          <Icon name="info" />
          {response.review_status === 'approved' ? t.approved : t.pending}
        </p>
      </div>
      <div className={`validation-strip ${status}`}>
        <Icon name={status === 'validated' ? 'check' : 'info'} />
        <span>
          {statusText}
          <small>
            {response.evidence.length} {t.linkedFacts}
          </small>
        </span>
        <button
          type="button"
          aria-label={t.checks}
          onClick={() => {
            onTabChange('checks')
            refs.current[2]?.focus()
          }}
        >
          <Icon name="arrow" />
        </button>
      </div>
    </section>
  )
}
