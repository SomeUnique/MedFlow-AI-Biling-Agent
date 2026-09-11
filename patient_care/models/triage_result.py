from pydantic import BaseModel, Field
from datetime import datetime


class TriageResult(BaseModel):
    triage_id: str
    intake_id: str
    urgency_level: str  # "low", "medium", "high", "emergency"
    reasoning: str
    created_at: datetime = Field(default_factory=datetime.now)
