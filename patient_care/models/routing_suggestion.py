from pydantic import BaseModel, Field
from datetime import datetime


class RoutingSuggestion(BaseModel):
    routing_id: str
    intake_id: str
    suggested_department: str
    suggested_doctor_type: str
    created_at: datetime = Field(default_factory=datetime.now)
