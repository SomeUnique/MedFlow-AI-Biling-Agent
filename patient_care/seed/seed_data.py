import sys
import os
from datetime import datetime, timedelta

# Ensure python path includes project root when run directly as `python -m patient_care.seed.seed_data`
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from patient_care.database.db import (
    reset_db,
    insert_intake,
    insert_triage,
    insert_routing,
    list_all_intakes,
    list_all_triage,
    list_all_routing
)
from patient_care.models.patient_intake import PatientIntake
from patient_care.models.triage_result import TriageResult
from patient_care.models.routing_suggestion import RoutingSuggestion


def seed():
    print("Resetting and initializing patient_care database...")
    reset_db()

    now = datetime.now()

    # 1. Patient Intakes (5-6 varied intakes)
    intakes = [
        PatientIntake(
            intake_id="INTAKE-001",
            patient_id="PAT-101",
            symptoms=["chest pain", "shortness of breath", "sweating"],
            age=58,
            gender="Male",
            additional_notes="History of hypertension.",
            created_at=now - timedelta(hours=4)
        ),
        PatientIntake(
            intake_id="INTAKE-002",
            patient_id="PAT-102",
            symptoms=["mild headache", "fatigue"],
            age=32,
            gender="Female",
            additional_notes="Started this morning after working long hours.",
            created_at=now - timedelta(hours=3)
        ),
        PatientIntake(
            intake_id="INTAKE-003",
            patient_id="PAT-103",
            symptoms=["fever", "cough", "sore throat"],
            age=25,
            gender="Male",
            additional_notes="Duration 2 days.",
            created_at=now - timedelta(hours=2)
        ),
        PatientIntake(
            intake_id="INTAKE-004",
            patient_id="PAT-104",
            symptoms=["severe bleeding from injury", "deep laceration on arm"],
            age=40,
            gender="Female",
            additional_notes="Accident with kitchen knife.",
            created_at=now - timedelta(hours=1)
        ),
        PatientIntake(
            intake_id="INTAKE-005",
            patient_id="PAT-105",
            symptoms=["stomach ache", "nausea", "mild cramps"],
            age=29,
            gender="Female",
            additional_notes="Ate outside food yesterday.",
            created_at=now - timedelta(minutes=30)
        )
    ]

    for intake in intakes:
        insert_intake(intake)
    print(f"Inserted {len(intakes)} patient intakes.")

    # 2. Triage Results corresponding to intakes
    triage_results = [
        TriageResult(
            triage_id="TRIAGE-001",
            intake_id="INTAKE-001",
            urgency_level="emergency",
            reasoning="Chest pain and shortness of breath are acute signs potentially indicating myocardial infarction.",
            created_at=now - timedelta(hours=3, minutes=55)
        ),
        TriageResult(
            triage_id="TRIAGE-002",
            intake_id="INTAKE-002",
            urgency_level="low",
            reasoning="Mild headache and fatigue consistent with tension or stress; vitals stable.",
            created_at=now - timedelta(hours=2, minutes=50)
        ),
        TriageResult(
            triage_id="TRIAGE-003",
            intake_id="INTAKE-003",
            urgency_level="medium",
            reasoning="Fever and cough indicate upper respiratory infection requiring evaluation.",
            created_at=now - timedelta(hours=1, minutes=50)
        ),
        TriageResult(
            triage_id="TRIAGE-004",
            intake_id="INTAKE-004",
            urgency_level="emergency",
            reasoning="Severe bleeding from deep laceration requires immediate surgical intervention and wound care.",
            created_at=now - timedelta(minutes=55)
        ),
        TriageResult(
            triage_id="TRIAGE-005",
            intake_id="INTAKE-005",
            urgency_level="low",
            reasoning="Stomach ache and nausea point towards acute gastritis or mild food poisoning.",
            created_at=now - timedelta(minutes=25)
        )
    ]

    for tr in triage_results:
        insert_triage(tr)
    print(f"Inserted {len(triage_results)} triage results.")

    # 3. Routing Suggestions corresponding to intakes
    routings = [
        RoutingSuggestion(
            routing_id="ROUTE-001",
            intake_id="INTAKE-001",
            suggested_department="Emergency & Cardiology",
            suggested_doctor_type="Cardiologist",
            created_at=now - timedelta(hours=3, minutes=50)
        ),
        RoutingSuggestion(
            routing_id="ROUTE-002",
            intake_id="INTAKE-002",
            suggested_department="General Medicine",
            suggested_doctor_type="General Physician",
            created_at=now - timedelta(hours=2, minutes=45)
        ),
        RoutingSuggestion(
            routing_id="ROUTE-003",
            intake_id="INTAKE-003",
            suggested_department="General Outpatient",
            suggested_doctor_type="General Practitioner",
            created_at=now - timedelta(hours=1, minutes=45)
        ),
        RoutingSuggestion(
            routing_id="ROUTE-004",
            intake_id="INTAKE-004",
            suggested_department="Emergency Trauma",
            suggested_doctor_type="Trauma Surgeon",
            created_at=now - timedelta(minutes=50)
        ),
        RoutingSuggestion(
            routing_id="ROUTE-005",
            intake_id="INTAKE-005",
            suggested_department="Gastroenterology",
            suggested_doctor_type="Gastroenterologist",
            created_at=now - timedelta(minutes=20)
        )
    ]

    for rt in routings:
        insert_routing(rt)
    print(f"Inserted {len(routings)} routing suggestions.")

    print("\nVerification:")
    print(f"Total Intakes in DB: {len(list_all_intakes())}")
    print(f"Total Triage Results in DB: {len(list_all_triage())}")
    print(f"Total Routing Suggestions in DB: {len(list_all_routing())}")
    print("\nPatient Care database successfully seeded!")


if __name__ == "__main__":
    seed()
