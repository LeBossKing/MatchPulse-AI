import type { Language, ProcessEventResponse } from '../types/match'
import { copy } from '../lib/copy'
import { Icon } from './Icon'
import type { IconName } from './Icon'

export function AgentWorkflow({
  response,
  language,
}: {
  response: ProcessEventResponse
  language: Language
}) {
  const t = copy(language)
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
          {t.workflowNote}
        </span>
      </div>
      <div className="workflow-grid">
        {response.agent_trace.map((step, index) => (
          <article className="agent-card" key={step.agent}>
            <div className="agent-card-top">
              <span className="agent-number">0{index + 1}</span>
              <Icon name={icons[index]} />
              <span className="sample-trace-label">{t.sampleTrace}</span>
            </div>
            <h3>{labels[index]}</h3>
            <p>{descriptions[index]}</p>
            <details className="json-details">
              <summary>
                {t.inspectOutput}
                <Icon name="chevron" />
              </summary>
              <pre>{JSON.stringify(step.output, null, 2)}</pre>
            </details>
          </article>
        ))}
      </div>
      <p className="timing-note">{t.noTimings}</p>
    </section>
  )
}
