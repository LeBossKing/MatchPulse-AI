import type {
  DemoEventsResponse,
  DemoMatchResponse,
  ProcessEventResponse,
} from './match'

export interface DashboardSamples {
  match: DemoMatchResponse
  events: DemoEventsResponse
  responses: ProcessEventResponse[]
}

export type AnalysisTab = 'insight' | 'evidence' | 'checks'
