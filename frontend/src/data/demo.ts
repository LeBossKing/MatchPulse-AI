import type { Audience, Language, ProcessEventResponse } from '../types/match'
import type { DashboardSamples } from '../types/dashboard'
import { dashboardSamples } from './dashboard-samples'

// Public API types also check the generated corpus at compile time.
export const demo: DashboardSamples = dashboardSamples

export function selectSample(
  eventId: string,
  audience: Audience,
  language: Language,
): ProcessEventResponse {
  const sample = demo.responses.find(
    (item) =>
      item.event_id === eventId &&
      item.audience === audience &&
      item.language === language,
  )
  if (!sample)
    throw new Error(
      `Missing dashboard sample: ${eventId}/${audience}/${language}`,
    )
  return sample
}
