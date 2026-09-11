from pydantic import BaseModel, model_validator
from typing import List, Dict, Optional
from datetime import datetime


class Bill(BaseModel):
    bill_id: str
    patient_id: str
    services: List[str]
    breakdown: Dict[str, float]
    total_amount: float
    currency: str
    status: str = "unpaid"
    amount_paid: float = 0.0
    amount_due: Optional[float] = None
    payment_method: Optional[str] = None
    created_at: datetime = datetime.now()

    @model_validator(mode="after")
    def compute_amount_due(self) -> 'Bill':
        if self.amount_due is None:
            self.amount_due = self.total_amount - self.amount_paid
        return self
