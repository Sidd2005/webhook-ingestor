from pydantic import BaseModel, Field, field_validator
import re
from typing import Optional
from datetime import datetime

class WebhookPayload(BaseModel):
    """
    Strict Pydantic model for webhook payload validation.
    Ensures message_id, E.164 formats, ISO-8601 dates, and text length constraints.
    """
    message_id: str = Field(..., min_length=1)
    sender: str = Field(..., alias="from")
    recipient: str = Field(..., alias="to")
    timestamp: str = Field(..., alias="ts")
    text: Optional[str] = Field(None, max_length=4096)

    @field_validator("sender", "recipient")
    @classmethod
    def validate_e164(cls, v: str):
        if not re.match(r"^\+\d+$", v):
            raise ValueError("Must be in E.164-like format (+ followed by digits only)")
        return v

    @field_validator("timestamp")
    @classmethod
    def validate_iso8601_utc(cls, v: str):
        # Strict check for 'Z' suffix as per requirement
        if not v.endswith("Z"):
            raise ValueError("Timestamp must have 'Z' suffix for UTC")
        try:
            # Validate it's a valid ISO-8601 date
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("Invalid ISO-8601 timestamp")
        return v

    class Config:
        populate_by_name = True
