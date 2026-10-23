from pydantic import Field

from app.models.common import ContractModel, SchemaVersion


class ErrorDetail(ContractModel):
    field: str
    message: str
    type: str


class ApiError(ContractModel):
    code: str
    message: str
    details: list[ErrorDetail] = Field(default_factory=list)


class ErrorResponse(ContractModel):
    schema_version: SchemaVersion = "1.0.0"
    error: ApiError
