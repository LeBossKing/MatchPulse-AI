import type { ApiError } from '../api/client'
import type { Language } from '../types/match'
import { copy } from '../lib/copy'
import { Icon } from './Icon'

export function RequestState({
  language,
  error,
  title,
  onRetry,
  onSamples,
  bootstrap = false,
  description,
}: {
  language: Language
  error: ApiError | null
  title: string
  onRetry: () => void
  onSamples: () => void
  bootstrap?: boolean
  description?: string
}) {
  const t = copy(language)
  const message = error
    ? {
        network: t.errorNetwork,
        timeout: t.errorTimeout,
        invalid_response: t.errorInvalid,
        http: t.errorHttp,
      }[error.kind]
    : (description ?? (bootstrap ? t.loadingMatchHelp : t.processingHelp))
  return (
    <section
      className={`request-state panel ${error ? 'request-error' : ''}`}
      role={error ? 'alert' : 'status'}
      aria-live="polite"
    >
      {error ? (
        <Icon name="info" />
      ) : (
        <span className="request-spinner" aria-hidden="true" />
      )}
      <h2>{title}</h2>
      <p>{message}</p>
      {error?.status && (
        <code>
          HTTP {error.status}
          {error.code ? ` · ${error.code}` : ''}
        </code>
      )}
      <div className="request-actions">
        {error && (
          <button type="button" onClick={onRetry}>
            {t.retry}
          </button>
        )}
        <button className="secondary-request" type="button" onClick={onSamples}>
          {t.useSamples}
        </button>
      </div>
    </section>
  )
}
