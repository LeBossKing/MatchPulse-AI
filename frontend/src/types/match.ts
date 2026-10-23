import type { components } from './generated-api'

export type MatchEvent = components['schemas']['MatchEvent']
export type MatchMetadata = components['schemas']['MatchMetadata']
export type MatchStatistics = components['schemas']['MatchStatistics']
export type DemoMatchResponse = components['schemas']['DemoMatchResponse']
export type DemoEventsResponse = components['schemas']['DemoEventsResponse']
export type ProcessEventRequest = components['schemas']['ProcessEventRequest']
export type ProcessEventResponse = components['schemas']['ProcessEventResponse']
export type EvidenceItem = components['schemas']['EvidenceItem']
export type AgentTraceStep = components['schemas']['AgentTraceStep']
export type Audience = NonNullable<ProcessEventRequest['audience']>
export type Language = NonNullable<ProcessEventRequest['language']>
