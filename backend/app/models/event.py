from typing import Annotated, Literal, Self

from pydantic import Field, StrictBool, model_validator

from app.models.common import ContractModel, Count, Direction, Identifier


class Point(ContractModel):
    x: Annotated[float, Field(strict=True, ge=0, le=100, allow_inf_nan=False)]
    y: Annotated[float, Field(strict=True, ge=0, le=100, allow_inf_nan=False)]


class MatchEvent(ContractModel):
    event_id: Identifier
    match_id: Identifier
    period: Annotated[int, Field(strict=True, ge=1, le=2)]
    minute: Annotated[int, Field(strict=True, ge=0, le=150)]
    second: Annotated[int, Field(strict=True, ge=0, le=59)]
    event_type: Literal["pass", "interception", "recovery"]
    team_id: Identifier
    player_id: Identifier
    target_player_id: Identifier | None = None
    attacking_direction: Direction
    start: Point
    end: Point | None = None
    successful: StrictBool
    pressure: Literal["low", "medium", "high"] | None = None
    lines_broken: Count | None = None

    @model_validator(mode="after")
    def check_event_semantics(self) -> Self:
        if self.event_type == "pass":
            if self.end is None:
                raise ValueError("A pass requires end coordinates.")
            if self.successful and self.target_player_id is None:
                raise ValueError("A completed pass requires a target_player_id.")
            if self.target_player_id == self.player_id:
                raise ValueError("The passer and intended receiver must differ.")
            if not self.successful and self.lines_broken not in (None, 0):
                raise ValueError("Positive lines_broken requires a completed pass.")
        else:
            if not self.successful:
                raise ValueError("Interception and recovery represent completed regains.")
            if self.end is not None or self.target_player_id is not None:
                raise ValueError("A regain is a point event without an end or receiver.")
            if self.lines_broken is not None:
                raise ValueError("lines_broken is supported only for passes.")
        return self
