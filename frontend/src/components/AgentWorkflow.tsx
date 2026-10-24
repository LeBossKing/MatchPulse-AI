import type { Language, ProcessEventResponse } from '../types/match'
import { copy } from '../lib/copy'
import { Icon } from './Icon'
import { formatNumber } from '../lib/format'
import type { IconName } from './Icon'

export function AgentWorkflow({
  response,
  language,
}: {
  response: ProcessEventResponse
  language: Language
}) {
  const t = copy(language)
  const runtime = response.result_source === 'runtime'
  const labels = [t.intelligence, t.explainer, t.trust]
  const descriptions = [
    t.intelligenceDescription,
    t.explainerDescription,
    t.trustDescription,
  ]
  const icons: IconName[] = ['pitch', 'layers', 'check']
  return (
    <section
      className="agent-section"
      id="agent-workflow"
      aria-labelledby="workflow-title"
    >
      <div className="section-heading">
        <h2 id="workflow-title">{t.workflowTitle}</h2>
        <span>
          <span className="small-dot" />
          {runtime ? t.runtimeWorkflowNote : t.workflowNote}
        </span>
      </div>
      <div className="workflow-grid">
        {response.agent_trace.map((step, index) => (
          <article className="agent-card" key={step.agent}>
            <div className="agent-card-top">
              <span className="agent-number">0{index + 1}</span>
              <Icon name={icons[index]} />
              <span
                className={`sample-trace-label ${runtime ? 'stage-tag' : ''}`}
              >
                {runtime
                  ? `${step.status === 'completed' ? t.stageCompleted : step.status === 'skipped' ? t.stageSkipped : t.stageFailed} · ${formatNumber(step.duration_ms, language)} ms`
                  : t.sampleTrace}
              </span>
            </div>
            <h3>{labels[index]}</h3>
            <p>{descriptions[index]}</p>
            {runtime && <p className="runtime-step-summary">{step.summary}</p>}
            <details className="json-details">
              <summary>
                {runtime ? t.runtimeOutput : t.inspectOutput}
                <Icon name="chevron" />
              </summary>
              <pre>{JSON.stringify(runtime ? step : step.output, null, 2)}</pre>
            </details>
          </article>
        ))}
      </div>
      <p className="timing-note">{runtime ? t.runtimeTiming : t.noTimings}</p>
    </section>
  )
}
