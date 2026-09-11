import uuid
from datetime import datetime
from typing import List, Optional

from patient_care.models.patient_intake import PatientIntake
from patient_care.database import db


def create_intake(
    patient_id: str,
    symptoms: List[str],
    age: int,
    gender: str,
    additional_notes: Optional[str] = None,
    db_path: Optional[str] = None
) -> PatientIntake:
    """
    Creates and saves a PatientIntake record, returns the created model instance.
    """
    intake_id = f"INTAKE-{uuid.uuid4().hex[:8].upper()}"
    intake = PatientIntake(
        intake_id=intake_id,
        patient_id=patient_id,
        symptoms=symptoms,
        age=age,
        gender=gender,
        additional_notes=additional_notes,
        created_at=datetime.now()
    )

    if db_path:
        db.insert_intake(intake, db_path=db_path)
    else:
        db.insert_intake(intake)

    return intake


def get_intake(intake_id: str, db_path: Optional[str] = None) -> Optional[PatientIntake]:
    """
    Retrieves an intake record by ID from the database.
    """
    if db_path:
        return db.get_intake_by_id(intake_id, db_path=db_path)
    return db.get_intake_by_id(intake_id)
