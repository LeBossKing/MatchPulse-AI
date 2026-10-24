import Ajv2020 from 'ajv/dist/2020.js'
import schemas from './generated-schemas.json'
import type { DashboardData } from '../types/dashboard'
import type {
  DemoEventsResponse,
  DemoMatchResponse,
  ProcessEventRequest,
  ProcessEventResponse,
} from '../types/match'

// Shapes come from Pydantic exports. No coercion, default insertion, or removal
// of fields: a malformed payload must never become a plausible UI result.
const ajv = new Ajv2020({
  strict: false,
  allErrors: false,
  strictNumbers: true,
})
const matchSchema = ajv.compile<DemoMatchResponse>(
  schemas['demo-match-response'],
)
const eventsSchema = ajv.compile<DemoEventsResponse>(
  schemas['demo-events-response'],
)
const processSchema = ajv.compile<ProcessEventResponse>(
  schemas['process-response'],
)

export class InvalidResponseError extends Error {
  constructor() {
    super('The API response does not match the event contract.')
  }
}

function requireValid(condition: unknown): asserts condition {
  if (!condition) throw new InvalidResponseError()
}

function equal(left: unknown, right: unknown): boolean {
  if (left === right) return true
  if (
    left === null ||
    right === null ||
    typeof left !== 'object' ||
    typeof right !== 'object'
  )
    return false
  const a = Object.keys(left),
    b = Object.keys(right)
  return (
    a.length === b.length &&
    a.every(
      (key) =>
        Object.hasOwn(right, key) &&
        equal(
          (left as Record<string, unknown>)[key],
          (right as Record<string, unknown>)[key],
        ),
    )
  )
}

export function validateDemo(
  matchValue: unknown,
  eventsValue: unknown,
): DashboardData {
  requireValid(matchSchema(matchValue) && eventsSchema(eventsValue))
  const match = matchValue as DemoMatchResponse,
    events = eventsValue as DemoEventsResponse
  requireValid(
    match.schema_version === '1.0.0' && events.schema_version === '1.0.0',
  )
  requireValid(
    match.match.match_id === events.match_id &&
      match.review_status === events.review_status,
  )
  const teams = new Set([
    match.match.home_team.team_id,
    match.match.away_team.team_id,
  ])
  const roster = new Map(
    match.match.players.map((player) => [player.player_id, player.team_id]),
  )
  requireValid(teams.size === 2 && roster.size === match.match.players.length)
  requireValid(match.match.players.every((player) => teams.has(player.team_id)))
  requireValid(
    events.events.length > 0 &&
      new Set(events.events.map((event) => event.event_id)).size ===
        events.events.length,
  )
  requireValid(
    events.events.some((event) => event.event_id === events.main_event_id),
  )
  let previous = -1
  const directions = new Map<string, string>()
  for (const event of events.events) {
    const time = event.period * 100000 + event.minute * 60 + event.second
    requireValid(time >= previous)
    previous = time
    requireValid(
      event.match_id === events.match_id &&
        teams.has(event.team_id) &&
        roster.get(event.player_id) === event.team_id,
    )
    requireValid(
      !event.target_player_id ||
        roster.get(event.target_player_id) === event.team_id,
    )
    const directionKey = `${event.period}/${event.team_id}`
    requireValid(
      !directions.has(directionKey) ||
        directions.get(directionKey) === event.attacking_direction,
    )
    directions.set(directionKey, event.attacking_direction)
    if (event.event_type === 'pass') {
      requireValid(
        event.end &&
          (!event.successful || event.target_player_id) &&
          event.player_id !== event.target_player_id,
      )
      requireValid(event.successful || !event.lines_broken)
    } else {
      requireValid(
        event.successful &&
          event.end === null &&
          event.target_player_id === null &&
          event.lines_broken === null,
      )
    }
  }
  for (const period of [1, 2]) {
    const home = directions.get(`${period}/${match.match.home_team.team_id}`)
    const away = directions.get(`${period}/${match.match.away_team.team_id}`)
    requireValid(!home || !away || home !== away)
  }
  return { match, events }
}

export function validateProcessing(
  value: unknown,
  request: ProcessEventRequest,
  data: DashboardData,
): ProcessEventResponse {
  requireValid(processSchema(value))
  const response = value as ProcessEventResponse
  const index = data.events.events.findIndex(
    (event) => event.event_id === request.event_id,
  )
  requireValid(index >= 0)
  const event = data.events.events[index]
  requireValid(
    response.schema_version === '1.0.0' && response.result_source === 'runtime',
  )
  requireValid(
    response.match_id === request.match_id &&
      response.event_id === request.event_id,
  )
  requireValid(
    response.audience === (request.audience ?? 'analyst') &&
      response.language === (request.language ?? 'en'),
  )
  requireValid(
    response.review_status === data.match.review_status &&
      equal(response.event, event),
  )
  const length = event.end
    ? Math.round(
        Math.hypot(event.end.x - event.start.x, event.end.y - event.start.y) *
          100,
      ) / 100
    : null
  const progression = event.end
    ? (event.end.x - event.start.x) *
      (event.attacking_direction === 'left_to_right' ? 1 : -1)
    : null
  requireValid(
    response.statistics.pass_length === length &&
      response.statistics.forward_progression === progression,
  )
  requireValid(
    equal(
      response.overlay,
      event.end
        ? { kind: 'pass', start: event.start, end: event.end }
        : { kind: 'point', start: event.start, end: null },
    ),
  )
  requireValid(
    response.match_statistics.event_count === index + 1 &&
      response.match_statistics.through_event_id === event.event_id,
  )
  const expectedTeams = [
    data.match.match.home_team,
    data.match.match.away_team,
  ].map((team) => {
    const prefix = data.events.events
      .slice(0, index + 1)
      .filter((item) => item.team_id === team.team_id)
    const passes = prefix.filter((item) => item.event_type === 'pass')
    const completed = passes.filter((item) => item.successful).length
    return {
      team_id: team.team_id,
      passes_attempted: passes.length,
      passes_completed: completed,
      pass_accuracy_pct: passes.length
        ? Math.round((10000 * completed) / passes.length) / 100
        : null,
      interceptions: prefix.filter((item) => item.event_type === 'interception')
        .length,
      recoveries: prefix.filter((item) => item.event_type === 'recovery')
        .length,
    }
  })
  requireValid(
    response.match_statistics.teams.length === 2 &&
      expectedTeams.every((team) =>
        response.match_statistics.teams.some((actual) => equal(actual, team)),
      ),
  )
  const ids = new Set(response.evidence.map((item) => item.evidence_id))
  requireValid(ids.size === response.evidence.length)
  for (const item of response.evidence) {
    let source: unknown =
      item.source === 'event' ? response.event : response.statistics
    for (const field of item.field.split('.')) {
      requireValid(
        source !== null &&
          typeof source === 'object' &&
          Object.hasOwn(source, field),
      )
      source = (source as Record<string, unknown>)[field]
    }
    requireValid(source === item.value)
  }
  requireValid(
    response.insight
      ? response.validation.status !== 'rejected' &&
          response.insight.evidence_ids.every((id) => ids.has(id))
      : response.validation.status === 'rejected',
  )
  requireValid(
    response.agent_trace.map((step) => step.agent).join('/') ===
      'match_intelligence/tactical_explainer/trust_personalization',
  )
  requireValid(response.provider !== 'fallback' || response.warnings.length > 0)
  const provider = response.agent_trace[1].output
  requireValid(
    provider.requested_provider === 'mock' ||
      provider.requested_provider === 'azure',
  )
  if (response.provider === 'fallback') {
    requireValid(
      provider.actual_provider === 'mock' &&
        typeof provider.fallback_reason === 'string' &&
        provider.fallback_reason.length > 0,
    )
  } else {
    requireValid(
      provider.actual_provider === response.provider &&
        provider.requested_provider === response.provider &&
        provider.fallback_reason === null,
    )
  }
  return response
}
