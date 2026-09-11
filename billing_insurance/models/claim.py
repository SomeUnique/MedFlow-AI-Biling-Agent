from pydantic import BaseModel
from datetime import datetime


class Claim(BaseModel):
    claim_id: str
    patient_id: str
    bill_id: str
    status: str  # "pending", "approved", "rejected"
    submitted_at: datetime = datetime.now()
