from pydantic import BaseModel, Field


class HealthCheckResponseDto(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "Ok"})
