"""Check structured claims against canonical facts, then render controlled text.

This is a deterministic mock trust stage, not a general natural-language fact checker.
"""

from app.agents.contracts import IntelligenceResult, TacticalCandidate, TrustResult
from app.agents.tactical_explainer import importance_for, interpretation_for
from app.models.common import Audience, Language
from app.models.insight import ValidationResult
from app.models.match import DemoFixture
from app.services.narrative import render_insight


def validate_and_personalize(
    fixture: DemoFixture, facts: IntelligenceResult, candidate: TacticalCandidate,
    audience: Audience, language: Language,
) -> TrustResult:
    errors = []
    expected = {item.evidence_id: item for item in facts.evidence}
    seen = set()
    if candidate.event_id != facts.event.event_id:
        errors.append("The candidate refers to a different event.")
    for claim in candidate.claims:
        original = expected.get(claim.evidence_id)
        if claim.evidence_id in seen:
            errors.append("The candidate repeats an evidence identifier.")
        seen.add(claim.evidence_id)
        if original is None:
            errors.append(f"Unsupported claim field: {claim.source}.{claim.field}.")
        elif (
            claim.source != original.source or claim.field != original.field
            or isinstance(claim.value, bool) != isinstance(original.value, bool)
            or claim.value != original.value
        ):
            errors.append(f"Claim conflicts with canonical evidence: {original.source}.{original.field}.")
    if not set(expected).issubset(seen):
        errors.append("The candidate omitted required event facts.")
    if candidate.interpretation != interpretation_for(facts):
        errors.append("The proposed interpretation conflicts with the observed event.")
    if candidate.importance != importance_for(facts):
        errors.append("The proposed importance conflicts with the documented demo heuristic.")

    french = language == "fr"
    limitations = [
        "Données synthétiques ; les annotations tactiques ne proviennent pas d'un suivi des joueurs."
        if french else "Synthetic data; tactical annotations are authored, not player-tracking measurements.",
        "Statistiques limitées à la séquence sélectionnée ; les distances ne sont pas en mètres."
        if french else "Statistics cover only the selected sequence prefix; distances are not metres.",
        "Les positions des défenseurs et les occasions ultérieures ne sont pas établies."
        if french else "Defender positions and subsequent scoring chances are not established.",
    ]
    missing = facts.event.pressure is None or (
        facts.event.event_type == "pass" and facts.event.lines_broken is None
    )
    if missing:
        limitations.append(
            "Certaines annotations tactiques ne sont pas renseignées ; les valeurs inconnues restent inconnues."
            if french else "Some tactical annotations are unavailable; unknown values remain unknown.",
        )
    status = "rejected" if errors else "limited" if missing else "validated"
    return TrustResult(
        insight=None if errors else render_insight(fixture, facts, candidate, audience, language),
        validation=ValidationResult(
            status=status, unsupported_claims=errors, limitations=limitations,
        ),
    )
