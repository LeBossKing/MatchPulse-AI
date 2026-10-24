import type { Language, MatchEvent, MatchMetadata } from '../types/match'

export function clock(event: MatchEvent): string {
  return `${event.minute}:${String(event.second).padStart(2, '0')}`
}

export function formatNumber(
  value: number | null,
  language: Language,
  signed = false,
): string {
  if (value === null) return '—'
  return new Intl.NumberFormat(language === 'fr' ? 'fr-FR' : 'en-GB', {
    maximumFractionDigits: 2,
    signDisplay: signed ? 'exceptZero' : 'auto',
  }).format(value)
}

export function playerName(match: MatchMetadata, id: string | null): string {
  return match.players.find((player) => player.player_id === id)?.name ?? '—'
}

export function shirtNumber(id: string | null): string {
  return id?.split('-').at(-1) ?? '•'
}
