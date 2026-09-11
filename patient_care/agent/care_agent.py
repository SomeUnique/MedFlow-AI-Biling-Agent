# Main agent logic — understands patient care, triage & routing queries

import re
from typing import Optional, List
from patient_care.services import intake_service, triage_service


def _extract_symptoms(query: str) -> List[str]:
    """
    Extracts symptom-like phrases or splits raw query into searchable symptom fragments.
    """
    # Clean text and split on common conjunctions or punctuation
    cleaned = re.split(r"[,;.]|\band\b|\balso\b", query, flags=re.IGNORECASE)
    symptoms = [s.strip() for s in cleaned if len(s.strip()) > 2]
    if not symptoms:
        symptoms = [query.strip()]
    return symptoms


def handle_query(
    query: str,
    patient_id: str,
    age: Optional[int] = None,
    gender: Optional[str] = None,
    db_path: Optional[str] = None
) -> str:
    """
    Handles conversational query:
    1. Extracts symptoms from query
    2. Creates PatientIntake record
    3. Runs urgency assessment & department routing
    4. Returns a natural language response with necessary medical disclaimer
    """
    symptoms = _extract_symptoms(query)
    effective_age = age if age is not None else 30
    effective_gender = gender if gender is not None else "Unspecified"

    # 1. Create Patient Intake
    intake = intake_service.create_intake(
        patient_id=patient_id,
        symptoms=symptoms,
        age=effective_age,
        gender=effective_gender,
        additional_notes=f"Query text: '{query}'",
        db_path=db_path
    )

    # 2. Run Triage & Routing
    triage = triage_service.assess_urgency(intake.intake_id, db_path=db_path)
    routing = triage_service.suggest_routing(intake.intake_id, db_path=db_path)

    # 3. Format Natural Language Response with Disclaimer
    urgency_upper = triage.urgency_level.upper()
    
    if triage.urgency_level == "emergency":
        urgency_msg = "⚠️ IMMEDIATE ATTENTION NEEDED (EMERGENCY)"
    elif triage.urgency_level == "high":
        urgency_msg = "⚡ HIGH PRIORITY"
    elif triage.urgency_level == "medium":
        urgency_msg = "ℹ️ MEDIUM PRIORITY"
    else:
        urgency_msg = "🟢 LOW PRIORITY (Routine Care)"

    response = (
        f"Assessment for Patient {patient_id}:\n"
        f"- Triage Urgency: {urgency_msg} ({urgency_upper})\n"
        f"- Reasoning: {triage.reasoning}\n"
        f"- Recommended Department: {routing.suggested_department}\n"
        f"- Suggested Specialist: {routing.suggested_doctor_type}\n\n"
        f"DISCLAIMER: This is a preliminary triage assessment and NOT a medical diagnosis. "
        f"Please consult a qualified medical professional or visit the {routing.suggested_department} department for proper clinical evaluation."
    )

    return response
