import { API_BASE_URL } from '../api/client'
import { useHealthCheck } from '../hooks/useHealthCheck'
import type { Language } from '../types/match'

const labels = {
  checking: 'Checking connection',
  connected: 'Backend connected',
  offline: 'Backend unavailable',
}

export function ConnectionCard({ language = 'en' }: { language?: Language }) {
  const { status, health, error, retry } = useHealthCheck()
  const french = language === 'fr'
  const statusLabel = french
    ? {
        checking: 'Vérification en cours',
        connected: 'Backend connecté',
        offline: 'Backend indisponible',
      }[status]
    : labels[status]

  return (
    <section
      className="panel connection-card"
      aria-labelledby="connection-title"
    >
      <div className="panel-heading">
        <span className="eyebrow">
          {french ? 'VÉRIFICATION DE CONNEXION' : 'CONNECTION CHECK'}
        </span>
        <span className={'status-tag ' + status}>
          <span className="status-dot" aria-hidden="true" />
          {french
            ? status === 'connected'
              ? 'Connecté'
              : status === 'offline'
                ? 'Hors ligne'
                : 'Vérification'
            : status === 'connected'
              ? 'Online'
              : status === 'offline'
                ? 'Offline'
                : 'Checking'}
        </span>
      </div>

      <div className={'connection-symbol ' + status} aria-hidden="true">
        {status === 'connected' ? '✓' : status === 'offline' ? '!' : '…'}
      </div>
      <h2 id="connection-title">{statusLabel}</h2>
      <p className="connection-message" role="status" aria-live="polite">
        {french
          ? error
            ? 'La connexion au backend est indisponible. Vérifiez son adresse et son démarrage.'
            : status === 'connected'
              ? 'React reçoit une réponse valide du point de contrôle FastAPI.'
              : 'Vérification de la disponibilité de FastAPI.'
          : error ||
            (status === 'connected'
              ? 'React is receiving a validated response from the FastAPI health endpoint.'
              : 'Reaching the FastAPI health endpoint.')}
      </p>

      <dl className="connection-details">
        <div>
          <dt>{french ? 'Adresse' : 'Endpoint'}</dt>
          <dd>
            <code>{API_BASE_URL}/health</code>
          </dd>
        </div>
        <div>
          <dt>API version</dt>
          <dd>{health?.version ?? '—'}</dd>
        </div>
        <div>
          <dt>{french ? 'Environnement' : 'Environment'}</dt>
          <dd>{health?.environment ?? '—'}</dd>
        </div>
      </dl>

      <div className="actions">
        <button type="button" onClick={retry} disabled={status === 'checking'}>
          {french
            ? status === 'checking'
              ? 'Vérification…'
              : 'Vérifier la connexion'
            : status === 'checking'
              ? 'Checking…'
              : 'Check connection'}
          <span aria-hidden="true">↗</span>
        </button>
        <a
          className="secondary-action"
          href={API_BASE_URL + '/docs'}
          target="_blank"
          rel="noreferrer"
        >
          {french ? 'Documentation API' : 'API docs'}{' '}
          <span aria-hidden="true">↗</span>
        </a>
      </div>
    </section>
  )
}
