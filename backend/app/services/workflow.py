"""Request-local three-stage orchestration with measured, inspectable traces."""

from copy import deepcopy
import logging
from time import perf_counter

from pydantic import ValidationError

from app.agents.contracts import TacticalCandidate
from app.agents.match_intelligence import analyze_event
from app.agents.trust_personalization import validate_and_personalize
from app.models.insight import AgentTraceStep, ProcessEventRequest, ProcessEventResponse
from app.models.match import DemoFixture
from app.services.providers import MockTacticalProvider, ProviderError, ProviderSelection
from app.services.provider_messages import provider_hint

logger = logging.getLogger(__name__)


class WorkflowError(Exception):
    pass


def elapsed_ms(started: float) -> float:
    return round((perf_counter() - started) * 1000, 3)


def run_workflow(
    fixture: DemoFixture, event_index: int, request: ProcessEventRequest,
    selection: ProviderSelection,
) -> ProcessEventResponse:
    traces = []
    started = perf_counter()
    facts = analyze_event(fixture, event_index)
    traces.append(AgentTraceStep(
        agent="match_intelligence", status="completed", duration_ms=elapsed_ms(started),
        summary="Calculated event geometry, canonical evidence, and sequence-prefix statistics.",
        output={
            "statistics": facts.statistics.model_dump(mode="json"),
            "match_statistics": facts.match_statistics.model_dump(mode="json"),
            "evidence_count": len(facts.evidence),
        },
    ))
    french = request.language == "fr"
    warnings = []
    if fixture.review_status == "pending_review":
        warnings.append(
            "Les données et annotations attendent la validation du membre 2."
            if french else "The fixture and tactical annotations are pending Member 2 review.",
        )
    fallback_reason = selection.fallback_reason
    if fallback_reason:
        warnings.append(
            "Configuration Azure incomplète ou invalide ; repli sur le mock, sans requête Azure."
            if french else "Azure configuration is incomplete or invalid; used the mock fallback without sending an Azure request.",
        )

    started = perf_counter()
    attempts = []
    try:
        # Providers get an isolated snapshot and cannot alter the trusted facts.
        supplied = selection.provider.generate(deepcopy(facts))
        candidate = TacticalCandidate.model_validate(
            supplied.model_dump(mode="json") if isinstance(supplied, TacticalCandidate) else supplied,
        )
        attempts.append({"provider": selection.provider.name, "status": "completed"})
    except (ProviderError, ValidationError) as error:
        logger.warning("Tactical provider failed (%s); using mock fallback.", type(error).__name__)
        attempts.append({"provider": selection.provider.name, "status": "failed"})
        fallback_reason = error.reason if isinstance(error, ProviderError) else "provider_error"
        warnings.append(
            f"Le fournisseur a échoué ({fallback_reason}) ; le mock a pris le relais."
            if french else f"{provider_hint(fallback_reason)} Used the mock fallback.",
        )
        try:
            candidate = MockTacticalProvider().generate(deepcopy(facts))
        except (ProviderError, ValidationError) as fallback_error:
            raise WorkflowError("No valid tactical candidate is available.") from fallback_error
        attempts.append({"provider": "mock", "status": "completed"})
    if selection.provider.name == "azure":
        provenance = (
            "Le modèle Azure a produit une proposition structurée ; les faits sont calculés localement."
            if french else "The Azure model produced a structured candidate; event facts were calculated locally."
        ) if not fallback_reason else (
            "Proposition mock utilisée après un échec du fournisseur Azure."
            if french else "A mock candidate was used after an Azure provider failure."
        )
    else:
        provenance = (
            "Analyse déterministe de démonstration sur données synthétiques ; aucun modèle n'a été appelé."
            if french else "Deterministic mock analysis of synthetic data; no model was called."
        )
    warnings.insert(0, provenance)
    traces.append(AgentTraceStep(
        agent="tactical_explainer", status="completed", duration_ms=elapsed_ms(started),
        summary=(
            "Created a structured tactical candidate using the deterministic mock fallback."
            if fallback_reason else "Created a structured tactical candidate using the Azure deployment."
            if selection.provider.name == "azure" else
            "Created a structured tactical candidate using the deterministic mock provider."
        ),
        output={
            "requested_provider": selection.requested,
            "actual_provider": "mock" if fallback_reason else selection.provider.name,
            "fallback_reason": fallback_reason,
            "attempts": attempts,
            "candidate": candidate.model_dump(mode="json"),
        },
    ))
    started = perf_counter()
    trusted = validate_and_personalize(
        fixture, facts, candidate, request.audience, request.language,
    )
    traces.append(AgentTraceStep(
        agent="trust_personalization", status="completed", duration_ms=elapsed_ms(started),
        summary=(
            "Rejected unsupported claims; no narrative was published."
            if trusted.insight is None else
            "Checked structured claims and rendered the approved audience/language templates."
        ),
        output={
            "validation": trusted.validation.model_dump(mode="json"),
            "audience": request.audience, "language": request.language,
            "insight": trusted.insight.model_dump(mode="json") if trusted.insight else None,
        },
    ))
    if trusted.insight is None:
        warnings.append(
            "Explication rejetée : certaines affirmations contredisent les données disponibles."
            if french else "The explanation was rejected because candidate claims conflict with available evidence.",
        )
    return ProcessEventResponse(
        result_source="runtime", review_status=fixture.review_status,
        match_id=facts.event.match_id, event_id=facts.event.event_id, event=facts.event,
        audience=request.audience, language=request.language,
        provider="fallback" if fallback_reason else selection.provider.name,
        statistics=facts.statistics, match_statistics=facts.match_statistics,
        insight=trusted.insight, evidence=facts.evidence, validation=trusted.validation,
        overlay=facts.overlay, agent_trace=traces, warnings=warnings,
    )
