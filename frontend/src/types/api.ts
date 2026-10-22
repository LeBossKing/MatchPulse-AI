export interface HealthResponse {
  status: 'ok'
  service: 'matchpulse-api'
  version: string
  environment: 'development' | 'test' | 'production'
}
