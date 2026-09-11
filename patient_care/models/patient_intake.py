from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class PatientIntake(BaseModel):
    intake_id: str
    patient_id: str
    symptoms: List[str]
    age: int
    gender: str
    additional_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
