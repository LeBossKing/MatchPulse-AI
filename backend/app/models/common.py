"""Shared types for the version 1 contract."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

SchemaVersion = Literal["1.0.0"]
Identifier = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, min_length=1, max_length=64,
        pattern=r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$",
    ),
]
Count = Annotated[int, Field(strict=True, ge=0)]
Audience = Literal["fan", "analyst"]
Language = Literal["en", "fr"]
Direction = Literal["left_to_right", "right_to_left"]
ReviewStatus = Literal["pending_review", "approved"]


class ContractModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid", str_strip_whitespace=True,
        json_schema_serialization_defaults_required=True,
    )
