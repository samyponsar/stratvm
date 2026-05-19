from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
import re


class Event(BaseModel):
    model_config = ConfigDict(extra="ignore")

    tenant_id: str = Field(..., max_length=64)
    event_type: str = Field(..., max_length=128)
    id: Optional[int] = None
    received_at: datetime
    processed_at: Optional[datetime] = None
    committed_at: Optional[datetime] = None
    payload: Optional[dict] = None
    metadata: Optional[dict] = None

    @field_validator("event_type")
    @classmethod
    def check_event_type(cls, v: str) -> str:
        if not re.match(r"^[a-z][a-z0-9._-]*$", v):
            raise ValueError(
                "event_type must start with a letter and contain only a-z0-9._-"
            )
        return v
