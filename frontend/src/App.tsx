import { ConnectionCard } from './components/ConnectionCard'
import './App.css'

const nextSteps = [
  { number: '02', title: 'Agree on the event contract', detail: 'Validated match events and a shared API response.' },
  { number: '03', title: 'Build the agent workflow', detail: 'Facts, tactical explanations, and evidence checks.' },
  { number: '04', title: 'Bring the match to the dashboard', detail: 'A pitch, event timeline, and personalized insights.' },
]

function App() {
  return (
    <div className="workspace">
      <header className="topbar">
        <a className="brand" href="/" aria-label="MatchPulse AI home">
          <svg className="brand-mark" viewBox="0 0 32 32" fill="none" aria-hidden="true">
            <rect x="1" y="1" width="30" height="30" rx="8" />
            <path d="M6 17h5l3-7 4 13 3-6h5" />
          </svg>
          <span>MatchPulse<span className="brand-ai"> AI</span></span>
        </a>
        <span className="workspace-label">DEVELOPMENT WORKSPACE</span>
        <span className="checkpoint">Checkpoint <strong>01</strong></span>
      </header>

      <main>
        <section className="intro" aria-labelledby="page-title">
          <span className="eyebrow intro-eyebrow">FROM FOOTBALL EVENTS TO UNDERSTANDING</span>
          <h1 id="page-title">Match intelligence starts<br />with a <span>connection.</span></h1>
          <p>The project foundation is in place. Verify the backend connection before building the first match event.</p>
        </section>

        <div className="workspace-grid">
          <ConnectionCard />
          <section className="panel roadmap" aria-labelledby="roadmap-title">
            <div className="panel-heading">
              <span className="eyebrow">THE BUILD AHEAD</span>
              <span className="muted-label">NEXT MILESTONES</span>
            </div>
            <h2 id="roadmap-title">One event. The complete journey.</h2>
            <p className="roadmap-intro">Build a working path through the application, then expand it.</p>
            <ol className="milestones">
              {nextSteps.map((step) => (
                <li key={step.number}>
                  <span className="step-number">{step.number}</span>
                  <div><h3>{step.title}</h3><p>{step.detail}</p></div>
                </li>
              ))}
            </ol>
            <div className="scope-note"><span className="small-dot" aria-hidden="true" />Current scope: local application setup</div>
          </section>
        </div>

        <section className="workflow-preview" aria-labelledby="workflow-title">
          <div className="workflow-heading"><h2 id="workflow-title">Planned agent workflow</h2><span>Implementation follows the data contract</span></div>
          <div className="agent-list">
            <div><span className="agent-index">01</span><p>Match Intelligence<small>Validate events & calculate facts</small></p></div>
            <div><span className="agent-index">02</span><p>Tactical Explainer<small>Explain the moment with evidence</small></p></div>
            <div><span className="agent-index">03</span><p>Trust & Personalization<small>Check claims & adapt the explanation</small></p></div>
          </div>
        </section>
      </main>

      <footer><span>MatchPulse AI</span><span>Project foundation · v0.1.0</span></footer>
    </div>
  )
}

export default App
