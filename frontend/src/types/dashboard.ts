import type {
  DemoEventsResponse,
  DemoMatchResponse,
  ProcessEventResponse,
} from './match'

export interface DashboardData {
  match: DemoMatchResponse
  events: DemoEventsResponse
}

export interface DashboardSamples extends DashboardData {
  responses: ProcessEventResponse[]
}

export type AnalysisTab = 'insight' | 'evidence' | 'checks'
export type DataMode = 'api' | 'sample'
