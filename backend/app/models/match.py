from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from app.models.common import (
    ContractModel, Count, Identifier, ReviewStatus, SchemaVersion,
)
from app.models.event import MatchEvent


class Team(ContractModel):
    team_id: Identifier
    name: Annotated[str, Field(min_length=1, max_length=100)]


class Player(ContractModel):
    player_id: Identifier
    team_id: Identifier
    name: Annotated[str, Field(min_length=1, max_length=100)]


class Score(ContractModel):
    home: Count
    away: Count


class MatchMetadata(ContractModel):
    match_id: Identifier
    home_team: Team
    away_team: Team
    players: Annotated[list[Player], Field(min_length=2)]
    score: Score
    coordinate_system: Literal["normalized_0_100"] = "normalized_0_100"
    coordinate_origin: Literal["top_left"] = "top_left"
    description: Annotated[str, Field(min_length=1, max_length=500)]

    @model_validator(mode="after")
    def check_roster(self) -> Self:
        team_ids = {self.home_team.team_id, self.away_team.team_id}
        if len(team_ids) != 2:
            raise ValueError("Home and away teams must differ.")
        player_ids = [player.player_id for player in self.players]
        if len(set(player_ids)) != len(player_ids):
            raise ValueError("Player identifiers must be unique.")
        if any(player.team_id not in team_ids for player in self.players):
            raise ValueError("Every player must belong to a match team.")
        return self


class DemoFixture(ContractModel):
    schema_version: SchemaVersion = "1.0.0"
    data_source: Literal["synthetic"] = "synthetic"
    review_status: ReviewStatus = "pending_review"
    annotation_note: str
    match: MatchMetadata
    main_event_id: Identifier
    events: Annotated[list[MatchEvent], Field(min_length=1)]

    @model_validator(mode="after")
    def check_fixture(self) -> Self:
        event_ids = [event.event_id for event in self.events]
        if len(set(event_ids)) != len(event_ids):
            raise ValueError("Event identifiers must be unique.")
        if self.main_event_id not in event_ids:
            raise ValueError("main_event_id must reference a fixture event.")
        roster = {player.player_id: player.team_id for player in self.match.players}
        timestamps = [(event.period, event.minute, event.second) for event in self.events]
        if timestamps != sorted(timestamps):
            raise ValueError("Events must be in chronological order.")
        directions: dict[tuple[int, str], str] = {}
        for event in self.events:
            if event.match_id != self.match.match_id:
                raise ValueError("Every event must reference this match.")
            if event.team_id not in {
                self.match.home_team.team_id, self.match.away_team.team_id
            }:
                raise ValueError("The event team must belong to this match.")
            if roster.get(event.player_id) != event.team_id:
                raise ValueError("The event player must belong to its team.")
            if event.target_player_id and roster.get(event.target_player_id) != event.team_id:
                raise ValueError("The intended receiver must belong to the passing team.")
            key = (event.period, event.team_id)
            if key in directions and directions[key] != event.attacking_direction:
                raise ValueError("A team's attacking direction must stay fixed within a period.")
            directions[key] = event.attacking_direction
        for period in {event.period for event in self.events}:
            home = directions.get((period, self.match.home_team.team_id))
            away = directions.get((period, self.match.away_team.team_id))
            if home and away and home == away:
                raise ValueError("Opposing teams must attack in opposite directions.")
        return self


class TeamStatistics(ContractModel):
    team_id: Identifier
    passes_attempted: Count = 0
    passes_completed: Count = 0
    pass_accuracy_pct: Annotated[
        float, Field(ge=0, le=100, allow_inf_nan=False)
    ] | None = None
    interceptions: Count = 0
    recoveries: Count = 0

    @model_validator(mode="after")
    def check_pass_totals(self) -> Self:
        if self.passes_completed > self.passes_attempted:
            raise ValueError("Completed passes cannot exceed attempted passes.")
        expected = (
            round(100 * self.passes_completed / self.passes_attempted, 2)
            if self.passes_attempted else None
        )
        if self.pass_accuracy_pct != expected:
            raise ValueError("Pass accuracy must match the totals; use null before any attempts.")
        return self


class MatchStatistics(ContractModel):
    scope: Literal["demo_sequence"] = "demo_sequence"
    event_count: Count = 0
    through_event_id: Identifier | None = None
    teams: Annotated[list[TeamStatistics], Field(min_length=2, max_length=2)]

    @model_validator(mode="after")
    def check_statistics_scope(self) -> Self:
        if len({team.team_id for team in self.teams}) != 2:
            raise ValueError("Statistics must reference two distinct teams.")
        if (self.event_count == 0) != (self.through_event_id is None):
            raise ValueError("A nonempty prefix requires through_event_id; an empty prefix uses null.")
        return self


class DemoMatchResponse(ContractModel):
    schema_version: SchemaVersion = "1.0.0"
    data_source: Literal["synthetic"] = "synthetic"
    review_status: ReviewStatus
    annotation_note: str
    match: MatchMetadata
    statistics: MatchStatistics


class DemoEventsResponse(ContractModel):
    schema_version: SchemaVersion = "1.0.0"
    match_id: Identifier
    data_source: Literal["synthetic"] = "synthetic"
    review_status: ReviewStatus
    main_event_id: Identifier
    events: list[MatchEvent]
