from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

from patient_care.database import db
from patient_care.services import intake_service, triage_service
from patient_care.agent.care_agent import handle_query

app = FastAPI(
    title="MedFlow AI - Patient Care & Triage Module",
    version="1.0.0",
    description="Independent microservice module for patient intake, triage assessment, and routing."
)


@app.on_event("startup")
def startup_event():
    db.create_tables()


# =====================================================================
# REQUEST & RESPONSE MODELS
# =====================================================================

class CreateIntakeRequest(BaseModel):
    patient_id: str
    symptoms: List[str]
    age: int
    gender: str
    additional_notes: Optional[str] = None


class CreateIntakeResponse(BaseModel):
    intake_id: str
    summary: str


class TriageResponse(BaseModel):
    urgency_level: str
    reasoning: str


class RoutingResponse(BaseModel):
    suggested_department: str
    suggested_doctor_type: str


class AgentQueryRequest(BaseModel):
    query: str
    patient_id: str
    age: Optional[int] = None
    gender: Optional[str] = None


class AgentQueryResponse(BaseModel):
    response: str


# =====================================================================
# API ENDPOINTS
# =====================================================================

@app.post("/patient-care/intake", response_model=CreateIntakeResponse)
def create_patient_intake(payload: CreateIntakeRequest):
    intake = intake_service.create_intake(
        patient_id=payload.patient_id,
        symptoms=payload.symptoms,
        age=payload.age,
        gender=payload.gender,
        additional_notes=payload.additional_notes
    )
    return {
        "intake_id": intake.intake_id,
        "summary": f"Intake registered with {len(intake.symptoms)} symptom(s) for patient {intake.patient_id}."
    }


@app.post("/patient-care/triage/{intake_id}", response_model=TriageResponse)
def triage_patient_intake(intake_id: str):
    try:
        triage = triage_service.assess_urgency(intake_id)
        return {
            "urgency_level": triage.urgency_level,
            "reasoning": triage.reasoning
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/patient-care/routing/{intake_id}", response_model=RoutingResponse)
def get_routing_suggestion(intake_id: str):
    try:
        routing = triage_service.suggest_routing(intake_id)
        return {
            "suggested_department": routing.suggested_department,
            "suggested_doctor_type": routing.suggested_doctor_type
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/patient-care/query", response_model=AgentQueryResponse)
def handle_patient_query(payload: AgentQueryRequest):
    result = handle_query(
        query=payload.query,
        patient_id=payload.patient_id,
        age=payload.age,
        gender=payload.gender
    )
    return {
        "response": result
    }
