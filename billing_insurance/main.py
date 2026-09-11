from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from billing_insurance.database import db
from billing_insurance.services import billing_service, insurance_service

app = FastAPI(
    title="MedFlow AI - Billing & Insurance Module",
    version="1.0.0",
    description="Independent microservice module for billing and insurance operations."
)


@app.on_event("startup")
def startup_event():
    db.create_tables()


# =====================================================================
# REQUEST & RESPONSE MODELS
# =====================================================================

class EstimateRequest(BaseModel):
    patient_id: str
    treatment_type: str


class EstimateResponse(BaseModel):
    estimated_cost: float
    currency: str


class GenerateInvoiceRequest(BaseModel):
    patient_id: str
    services: List[str]


class GenerateInvoiceResponse(BaseModel):
    invoice_id: str
    total_amount: float
    breakdown: Dict[str, float]


class ValidateInsuranceResponse(BaseModel):
    is_valid: bool
    coverage_percentage: float
    policy_details: Optional[Any] = None


class SubmitClaimRequest(BaseModel):
    patient_id: str
    bill_id: str


class RecordPaymentRequest(BaseModel):
    bill_id: str
    amount: float
    payment_method: str

class SubmitClaimResponse(BaseModel):
    claim_id: str
    status: str

class RecordPaymentResponse(BaseModel):
    bill_id: str
    amount_paid: float
    amount_due: float
    status: str
    payment_method: str


class ClaimStatusResponse(BaseModel):
    status: str


# =====================================================================
# API ENDPOINTS
# =====================================================================

@app.post("/billing/estimate", response_model=EstimateResponse)
def estimate_billing_cost(payload: EstimateRequest):
    est = billing_service.estimate_cost(payload.treatment_type)
    return {
        "estimated_cost": est["estimated_price"],
        "currency": est["currency"]
    }


@app.post("/billing/generate-invoice", response_model=GenerateInvoiceResponse)
def generate_invoice(payload: GenerateInvoiceRequest):
    if not payload.services:
        raise HTTPException(status_code=400, detail="Services list cannot be empty.")
    bill = billing_service.generate_invoice(payload.patient_id, payload.services)
    return {
        "invoice_id": bill.bill_id,
        "total_amount": bill.total_amount,
        "breakdown": bill.breakdown
    }


@app.post("/billing/record-payment", response_model=RecordPaymentResponse)
def record_bill_payment(payload: RecordPaymentRequest):
    try:
        return billing_service.record_payment(payload.bill_id, payload.amount, payload.payment_method)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/insurance/validate/{patient_id}", response_model=ValidateInsuranceResponse)
def validate_patient_insurance(patient_id: str):
    res = insurance_service.validate_insurance(patient_id)
    # Convert policy_details object to dict or representation if present
    policy_dict = None
    if res["policy_details"]:
        pol = res["policy_details"]
        policy_dict = {
            "policy_id": pol.policy_id,
            "patient_id": pol.patient_id,
            "provider_name": pol.provider_name,
            "coverage_percentage": pol.coverage_percentage,
            "max_limit": pol.max_limit,
            "excluded_treatments": pol.excluded_treatments,
            "is_expired": pol.is_expired
        }
    return {
        "is_valid": res["is_valid"],
        "coverage_percentage": res["coverage_percentage"],
        "policy_details": policy_dict
    }


@app.post("/insurance/submit-claim", response_model=SubmitClaimResponse)
def submit_insurance_claim(payload: SubmitClaimRequest):
    res = insurance_service.submit_claim(payload.patient_id, payload.bill_id)
    return {
        "claim_id": res["claim_id"],
        "status": res["status"]
    }


@app.get("/insurance/claim-status/{claim_id}", response_model=ClaimStatusResponse)
def get_claim_status(claim_id: str):
    res = insurance_service.get_claim_status(claim_id)
    if not res["found"]:
        raise HTTPException(status_code=404, detail=res["message"])
    return {
        "status": res["status"]
    }
