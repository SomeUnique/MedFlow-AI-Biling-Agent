from pydantic import BaseModel
from typing import List


class InsurancePolicy(BaseModel):
    policy_id: str
    patient_id: str
    provider_name: str
    coverage_percentage: float
    max_limit: float | None = None
    excluded_treatments: List[str] = []
    is_expired: bool = False
