# ==============================================================================
# DISCLAIMER:
# This is a RULE-BASED URGENCY CLASSIFIER for demo purposes only, NOT a medical
# diagnostic tool, and should never be presented to real patients as medical advice.
# ==============================================================================

import uuid
from datetime import datetime
from typing import Optional

from patient_care.models.triage_result import TriageResult
from patient_care.models.routing_suggestion import RoutingSuggestion
from patient_care.database import db

# Keyword-severity mapping (priority order: emergency > high > medium > low)
EMERGENCY_KEYWORDS = [
    "severe bleeding", "unconscious", "not breathing", "chest pain", 
    "severe injury", "cardiac arrest", "stroke", "severe trauma"
]

HIGH_KEYWORDS = [
    "high fever", "difficulty breathing", "severe pain", "shortness of breath", 
    "fracture", "deep laceration"
]

MEDIUM_KEYWORDS = [
    "fever", "persistent cough", "vomiting", "moderate pain", "diarrhea", 
    "stomach ache", "nausea", "cramps", "sore throat"
]

LOW_KEYWORDS = [
    "mild headache", "minor cold", "small cut", "fatigue", "headache", 
    "cold", "mild rash", "sneezing"
]

# Department and Doctor routing mappings
DEPARTMENT_ROUTING_RULES = [
    {
        "keywords": ["chest pain", "heart", "cardiac", "palpitation"],
        "department": "Cardiology",
        "doctor_type": "Cardiologist"
    },
    {
        "keywords": ["severe bleeding", "injury", "trauma", "unconscious", "not breathing", "laceration", "accident"],
        "department": "Emergency Medicine",
        "doctor_type": "Emergency Specialist / Trauma Surgeon"
    },
    {
        "keywords": ["headache", "migraine", "dizziness", "seizure", "neurological"],
        "department": "Neurology",
        "doctor_type": "Neurologist"
    },
    {
        "keywords": ["stomach", "vomiting", "nausea", "cramps", "abdominal", "diarrhea"],
        "department": "Gastroenterology",
        "doctor_type": "Gastroenterologist"
    },
    {
        "keywords": ["fever", "cough", "sore throat", "cold", "fatigue", "general"],
        "department": "General Medicine",
        "doctor_type": "General Physician"
    }
]

DEFAULT_ROUTING = {
    "department": "General Medicine",
    "doctor_type": "General Physician"
}


def assess_urgency(intake_id: str, db_path: Optional[str] = None) -> TriageResult:
    """
    Looks up the intake, analyzes symptoms using a rule-based keyword system,
    saves and returns a TriageResult.
    """
    if db_path:
        intake = db.get_intake_by_id(intake_id, db_path=db_path)
    else:
        intake = db.get_intake_by_id(intake_id)

    if not intake:
        raise ValueError(f"Patient intake with ID '{intake_id}' not found.")

    all_symptoms_text = " ".join(intake.symptoms).lower()
    if intake.additional_notes:
        all_symptoms_text += " " + intake.additional_notes.lower()

    # Detect urgency level by checking from highest priority to lowest
    urgency_level = "low"
    matched_keyword = None

    for kw in EMERGENCY_KEYWORDS:
        if kw in all_symptoms_text:
            urgency_level = "emergency"
            matched_keyword = kw
            break

    if not matched_keyword:
        for kw in HIGH_KEYWORDS:
            if kw in all_symptoms_text:
                urgency_level = "high"
                matched_keyword = kw
                break

    if not matched_keyword:
        for kw in MEDIUM_KEYWORDS:
            if kw in all_symptoms_text:
                urgency_level = "medium"
                matched_keyword = kw
                break

    if not matched_keyword:
        for kw in LOW_KEYWORDS:
            if kw in all_symptoms_text:
                urgency_level = "low"
                matched_keyword = kw
                break

    if matched_keyword:
        reasoning = f"Urgency assessed as '{urgency_level}' due to detected symptom/flag: '{matched_keyword}'."
    else:
        reasoning = f"Urgency assessed as '{urgency_level}' (default baseline for non-acute symptoms)."

    triage_id = f"TRIAGE-{uuid.uuid4().hex[:8].upper()}"
    triage = TriageResult(
        triage_id=triage_id,
        intake_id=intake_id,
        urgency_level=urgency_level,
        reasoning=reasoning,
        created_at=datetime.now()
    )

    if db_path:
        db.insert_triage(triage, db_path=db_path)
    else:
        db.insert_triage(triage)

    return triage


def suggest_routing(intake_id: str, db_path: Optional[str] = None) -> RoutingSuggestion:
    """
    Based on symptoms, suggests a department and doctor type using keyword mapping,
    saves and returns a RoutingSuggestion.
    """
    if db_path:
        intake = db.get_intake_by_id(intake_id, db_path=db_path)
    else:
        intake = db.get_intake_by_id(intake_id)

    if not intake:
        raise ValueError(f"Patient intake with ID '{intake_id}' not found.")

    all_symptoms_text = " ".join(intake.symptoms).lower()
    if intake.additional_notes:
        all_symptoms_text += " " + intake.additional_notes.lower()

    suggested_dept = DEFAULT_ROUTING["department"]
    suggested_doc = DEFAULT_ROUTING["doctor_type"]

    for rule in DEPARTMENT_ROUTING_RULES:
        if any(kw in all_symptoms_text for kw in rule["keywords"]):
            suggested_dept = rule["department"]
            suggested_doc = rule["doctor_type"]
            break

    routing_id = f"ROUTE-{uuid.uuid4().hex[:8].upper()}"
    routing = RoutingSuggestion(
        routing_id=routing_id,
        intake_id=intake_id,
        suggested_department=suggested_dept,
        suggested_doctor_type=suggested_doc,
        created_at=datetime.now()
    )

    if db_path:
        db.insert_routing(routing, db_path=db_path)
    else:
        db.insert_routing(routing)

    return routing
