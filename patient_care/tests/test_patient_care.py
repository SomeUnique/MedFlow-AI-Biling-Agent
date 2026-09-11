import os
import tempfile
import pytest
from datetime import datetime

from patient_care.models.patient_intake import PatientIntake
from patient_care.models.triage_result import TriageResult
from patient_care.models.routing_suggestion import RoutingSuggestion
from patient_care.database.db import (
    create_tables,
    insert_intake,
    get_intake_by_id,
    list_all_intakes,
    list_intakes_by_patient_id,
    insert_triage,
    get_triage_by_id,
    get_triage_by_intake_id,
    list_all_triage,
    insert_routing,
    get_routing_by_id,
    get_routing_by_intake_id,
    list_all_routing
)
from patient_care.services.intake_service import create_intake, get_intake
from patient_care.services.triage_service import assess_urgency, suggest_routing
from patient_care.agent.care_agent import handle_query


@pytest.fixture
def temp_db():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    create_tables(db_path)
    yield db_path
    os.close(db_fd)
    if os.path.exists(db_path):
        os.remove(db_path)


def test_patient_intake_crud(temp_db):
    intake = PatientIntake(
        intake_id="INTAKE-TEST-1",
        patient_id="PAT-TEST-1",
        symptoms=["cough", "fever"],
        age=30,
        gender="Female",
        additional_notes="Allergic to penicillin."
    )
    insert_intake(intake, db_path=temp_db)

    # get_by_id
    retrieved = get_intake_by_id("INTAKE-TEST-1", db_path=temp_db)
    assert retrieved is not None
    assert retrieved.patient_id == "PAT-TEST-1"
    assert retrieved.symptoms == ["cough", "fever"]
    assert retrieved.age == 30
    assert retrieved.gender == "Female"
    assert retrieved.additional_notes == "Allergic to penicillin."

    # list_all
    all_intakes = list_all_intakes(db_path=temp_db)
    assert len(all_intakes) == 1

    # list_by_patient_id
    patient_intakes = list_intakes_by_patient_id("PAT-TEST-1", db_path=temp_db)
    assert len(patient_intakes) == 1
    assert patient_intakes[0].intake_id == "INTAKE-TEST-1"


def test_triage_result_crud(temp_db):
    triage = TriageResult(
        triage_id="TRIAGE-TEST-1",
        intake_id="INTAKE-TEST-1",
        urgency_level="emergency",
        reasoning="Patient exhibits acute chest pain and high heart rate."
    )
    insert_triage(triage, db_path=temp_db)

    # get_by_id
    retrieved = get_triage_by_id("TRIAGE-TEST-1", db_path=temp_db)
    assert retrieved is not None
    assert retrieved.urgency_level == "emergency"
    assert retrieved.intake_id == "INTAKE-TEST-1"

    # get_by_intake_id
    retrieved_by_intake = get_triage_by_intake_id("INTAKE-TEST-1", db_path=temp_db)
    assert retrieved_by_intake is not None
    assert retrieved_by_intake.triage_id == "TRIAGE-TEST-1"

    # list_all
    all_triage = list_all_triage(db_path=temp_db)
    assert len(all_triage) == 1


def test_routing_suggestion_crud(temp_db):
    routing = RoutingSuggestion(
        routing_id="ROUTE-TEST-1",
        intake_id="INTAKE-TEST-1",
        suggested_department="Cardiology",
        suggested_doctor_type="Cardiologist"
    )
    insert_routing(routing, db_path=temp_db)

    # get_by_id
    retrieved = get_routing_by_id("ROUTE-TEST-1", db_path=temp_db)
    assert retrieved is not None
    assert retrieved.suggested_department == "Cardiology"
    assert retrieved.suggested_doctor_type == "Cardiologist"

    # get_by_intake_id
    retrieved_by_intake = get_routing_by_intake_id("INTAKE-TEST-1", db_path=temp_db)
    assert retrieved_by_intake is not None
    assert retrieved_by_intake.routing_id == "ROUTE-TEST-1"

    # list_all
    all_routings = list_all_routing(db_path=temp_db)
    assert len(all_routings) == 1


def test_intake_service(temp_db):
    intake = create_intake(
        patient_id="PAT-SV-1",
        symptoms=["chest pain", "dizziness"],
        age=50,
        gender="Male",
        additional_notes="Sudden onset",
        db_path=temp_db
    )
    assert intake.patient_id == "PAT-SV-1"
    assert "chest pain" in intake.symptoms

    retrieved = get_intake(intake.intake_id, db_path=temp_db)
    assert retrieved is not None
    assert retrieved.intake_id == intake.intake_id


def test_triage_service_urgency_and_routing(temp_db):
    # Test Emergency Urgency (severe chest pain)
    intake_emergency = create_intake(
        patient_id="PAT-EM-1",
        symptoms=["severe chest pain", "shortness of breath"],
        age=60,
        gender="Male",
        db_path=temp_db
    )
    triage_em = assess_urgency(intake_emergency.intake_id, db_path=temp_db)
    assert triage_em.urgency_level in ["emergency", "high"]
    assert "chest pain" in triage_em.reasoning

    routing_em = suggest_routing(intake_emergency.intake_id, db_path=temp_db)
    assert routing_em.suggested_department in ["Cardiology", "Emergency Medicine"]
    assert routing_em.suggested_doctor_type == "Cardiologist"

    # Test Low Urgency (mild headache)
    intake_low = create_intake(
        patient_id="PAT-LOW-1",
        symptoms=["mild headache"],
        age=24,
        gender="Female",
        db_path=temp_db
    )
    triage_low = assess_urgency(intake_low.intake_id, db_path=temp_db)
    assert triage_low.urgency_level == "low"

    # Test Routing suggestion for fever/cough symptoms (General Medicine)
    intake_fever_cough = create_intake(
        patient_id="PAT-FC-1",
        symptoms=["fever", "cough"],
        age=35,
        gender="Male",
        db_path=temp_db
    )
    routing_fc = suggest_routing(intake_fever_cough.intake_id, db_path=temp_db)
    assert routing_fc.suggested_department == "General Medicine"


def test_care_agent_handle_query(temp_db):
    # Test query handling with emergency symptom
    response = handle_query(
        query="I have severe chest pain and dizziness",
        patient_id="PAT-QUERY-1",
        age=45,
        gender="Male",
        db_path=temp_db
    )
    assert "EMERGENCY" in response
    assert "Cardiology" in response
    assert "DISCLAIMER" in response
    assert "NOT a medical diagnosis" in response
