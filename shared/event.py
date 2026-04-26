from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, model_validator


class Event(BaseModel):
    tenant_id: str = Field(..., max_length=64)
    event_type: str = Field(..., max_length=128)
    received_at: datetime
    processed_at: Optional[datetime] = None
    committed_at: Optional[datetime] = None
    success: bool
    failure_reason: Optional[str] = None
    payload: Optional[dict] = None
    metadata: Optional[dict] = None

    @model_validator(mode="after")
    def check_failure_reason(self) -> "Event":
        if not self.success and self.failure_reason is None:
            raise ValueError(
                "failure_reason is required when success is false"
            )
        return self
