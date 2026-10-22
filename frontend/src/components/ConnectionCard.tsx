import { API_BASE_URL } from '../api/client'
import { useHealthCheck } from '../hooks/useHealthCheck'

const labels = {
  checking: 'Checking connection',
  connected: 'Backend connected',
  offline: 'Backend unavailable',
}

export function ConnectionCard() {
  const { status, health, error, retry } = useHealthCheck()

  return (
    <section className="panel connection-card" aria-labelledby="connection-title">
      <div className="panel-heading">
        <span className="eyebrow">CONNECTION CHECK</span>
        <span className={'status-tag ' + status}>
          <span className="status-dot" aria-hidden="true" />
          {status === 'connected' ? 'Online' : status === 'offline' ? 'Offline' : 'Checking'}
        </span>
      </div>

      <div className={'connection-symbol ' + status} aria-hidden="true">
        {status === 'connected' ? '✓' : status === 'offline' ? '!' : '…'}
      </div>
      <h2 id="connection-title">{labels[status]}</h2>
      <p className="connection-message" role="status" aria-live="polite">
        {error || (status === 'connected'
          ? 'React is receiving a validated response from the FastAPI health endpoint.'
          : 'Reaching the FastAPI health endpoint.')}
      </p>

      <dl className="connection-details">
        <div><dt>Endpoint</dt><dd><code>{API_BASE_URL}/health</code></dd></div>
        <div><dt>API version</dt><dd>{health?.version ?? '—'}</dd></div>
        <div><dt>Environment</dt><dd>{health?.environment ?? '—'}</dd></div>
      </dl>

      <div className="actions">
        <button type="button" onClick={retry} disabled={status === 'checking'}>
          {status === 'checking' ? 'Checking…' : 'Check connection'}
          <span aria-hidden="true">↗</span>
        </button>
        <a className="secondary-action" href={API_BASE_URL + '/docs'} target="_blank" rel="noreferrer">
          API docs <span aria-hidden="true">↗</span>
        </a>
      </div>
    </section>
  )
}
