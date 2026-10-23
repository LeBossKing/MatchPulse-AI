"""Render approved templates only after the trust stage accepts structured claims."""

from app.agents.contracts import IntelligenceResult, TacticalCandidate
from app.models.common import Audience, Language
from app.models.insight import Insight
from app.models.match import DemoFixture


def number(value: float, language: Language, signed: bool = False) -> str:
    text = format(value, "+g" if signed else "g")
    return text.replace(".", ",") if language == "fr" else text


def render_insight(
    fixture: DemoFixture, facts: IntelligenceResult, candidate: TacticalCandidate,
    audience: Audience, language: Language,
) -> Insight:
    event = facts.event
    players = {player.player_id: player.name for player in fixture.match.players}
    teams = {
        fixture.match.home_team.team_id: fixture.match.home_team.name,
        fixture.match.away_team.team_id: fixture.match.away_team.name,
    }
    player = players[event.player_id]
    team = teams[event.team_id]
    french = language == "fr"
    target = players.get(event.target_player_id) or (
        "un destinataire non renseigné" if french else "an unspecified receiver"
    )
    if event.event_type == "pass":
        progression = facts.statistics.forward_progression
        length = number(facts.statistics.pass_length, language)
        signed = number(progression, language, signed=True)
        if french:
            title = "Passe réussie" if event.successful else "Passe non réussie"
            action = (
                f"{player} réussit une passe vers {target}." if event.successful
                else f"{player} tente une passe vers {target}, mais elle n'est pas réussie."
            )
            metrics = (
                f"Longueur enregistrée : {length} unités normalisées ; "
                f"déplacement vers le but attaqué : {signed} unités."
            )
            if audience == "fan" and event.successful:
                motion = "avance" if progression > 0 else "recule"
                metrics = (
                    f"Le ballon {motion} de "
                    f"{number(abs(progression), language)} unités normalisées."
                    if progression else "La passe ne fait pas progresser le ballon vers le but attaqué."
                )
            elif audience == "fan":
                metrics = "Cette tentative ne constitue pas une progression réussie."
            if audience == "analyst" and not event.successful:
                metrics += " Ce déplacement ne constitue pas un gain réussi."
        else:
            title = "A completed pass" if event.successful else "An unsuccessful pass"
            action = (
                f"{player} completes a pass to {target}." if event.successful
                else f"{player} attempts a pass intended for {target}, but it is not completed."
            )
            metrics = (
                f"Recorded length: {length} normalized pitch units; "
                f"displacement toward the attacking goal: {signed} units."
            )
            if audience == "fan" and event.successful:
                direction = "forward" if progression > 0 else "backward"
                metrics = (
                    f"The ball moves {direction} by "
                    f"{number(abs(progression), language)} normalized pitch units."
                    if progression else "The pass adds no forward progression."
                )
            elif audience == "fan":
                metrics = "This attempt does not count as a completed gain."
            if audience == "analyst" and not event.successful:
                metrics += " This displacement is not a completed gain."
        if event.successful and event.lines_broken:
            count = event.lines_broken
            if french:
                title = "Une passe au-delà d'une ligne adverse" if count == 1 else f"Une passe au-delà de {count} lignes adverses"
            else:
                title = "A pass beyond one opposition line" if count == 1 else f"A pass beyond {count} opposition lines"
        sentences = [action, metrics]
    else:
        x, y = number(event.start.x, language), number(event.start.y, language)
        if french:
            label = "interception" if event.event_type == "interception" else "récupération"
            title = "Interception du ballon" if event.event_type == "interception" else "Récupération du ballon"
            action = f"{player} réalise une {label} pour {team}."
            position = f"Position enregistrée : ({x}, {y}), sur l'échelle normalisée de 0 à 100."
        else:
            label = "an interception" if event.event_type == "interception" else "a recovery"
            title = "A ball interception" if event.event_type == "interception" else "A ball recovery"
            action = f"{player} records {label} for {team}."
            position = f"Recorded location: ({x}, {y}) on the normalized 0-100 pitch."
        sentences = [action]
        if audience == "analyst":
            sentences.append(position)

    if event.pressure is None:
        sentences.append("La pression n'est pas renseignée." if french else "Pressure is not supplied.")
    else:
        pressure = {"low": "faible", "medium": "moyenne", "high": "forte"}[event.pressure]
        sentences.append(
            f"Annotation synthétique : pression {pressure}."
            if french else f"Synthetic annotation: {event.pressure} pressure."
        )
    if event.event_type == "pass":
        if event.lines_broken is None:
            sentences.append(
                "Le nombre de lignes franchies n'est pas renseigné."
                if french else "No line-break annotation is supplied."
            )
        else:
            lines = "ligne adverse franchie" if event.lines_broken == 1 else "lignes adverses franchies"
            english_lines = "opposition line" if event.lines_broken == 1 else "opposition lines"
            sentences.append(
                f"L'annotation synthétique indique {event.lines_broken} {lines}."
                if french else f"The synthetic annotation records {event.lines_broken} {english_lines} bypassed."
            )

    interpretations = {
        "en": {
            "advance": f"This may help {team} advance play; a subsequent chance is not established.",
            "retain": f"This may help {team} circulate the ball; forward advancement is not established.",
            "attempt_failed": "The recorded attempt does not establish successful advancement or a scoring chance.",
            "regain": f"This may let {team} restart its attack; subsequent play is not established.",
        },
        "fr": {
            "advance": f"Cela peut aider {team} à progresser ; aucune occasion ultérieure n'est établie.",
            "retain": f"Cela peut aider {team} à faire circuler le ballon ; aucune progression vers l'avant n'est établie.",
            "attempt_failed": "Cette tentative n'établit ni progression réussie ni occasion de but.",
            "regain": f"Cela peut permettre à {team} de relancer son attaque ; la suite du jeu n'est pas établie.",
        },
    }
    return Insight(
        title=title, explanation=" ".join(sentences),
        interpretation=interpretations[language][candidate.interpretation],
        importance=candidate.importance,
        evidence_ids=[item.evidence_id for item in facts.evidence],
    )
