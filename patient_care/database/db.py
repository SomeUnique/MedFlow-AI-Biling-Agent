import sqlite3
import json
import os
from typing import List, Optional
from datetime import datetime

from patient_care.models.patient_intake import PatientIntake
from patient_care.models.triage_result import TriageResult
from patient_care.models.routing_suggestion import RoutingSuggestion

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "patient_care.db")


def get_connection(db_path: str = DB_FILE) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables(db_path: str = DB_FILE) -> None:
    conn = get_connection(db_path)
    cursor = conn.cursor()

    # Patient Intakes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patient_intakes (
            intake_id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            symptoms TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            additional_notes TEXT,
            created_at TEXT NOT NULL
        )
    """)

    # Triage Results table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS triage_results (
            triage_id TEXT PRIMARY KEY,
            intake_id TEXT NOT NULL,
            urgency_level TEXT NOT NULL,
            reasoning TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (intake_id) REFERENCES patient_intakes (intake_id)
        )
    """)

    # Routing Suggestions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS routing_suggestions (
            routing_id TEXT PRIMARY KEY,
            intake_id TEXT NOT NULL,
            suggested_department TEXT NOT NULL,
            suggested_doctor_type TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (intake_id) REFERENCES patient_intakes (intake_id)
        )
    """)

    conn.commit()
    conn.close()


def reset_db(db_path: str = DB_FILE) -> None:
    if os.path.exists(db_path):
        os.remove(db_path)
    create_tables(db_path)


# =====================================================================
# PATIENT INTAKE CRUD
# =====================================================================

def insert_intake(intake: PatientIntake, db_path: str = DB_FILE) -> None:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO patient_intakes 
        (intake_id, patient_id, symptoms, age, gender, additional_notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            intake.intake_id,
            intake.patient_id,
            json.dumps(intake.symptoms),
            intake.age,
            intake.gender,
            intake.additional_notes,
            intake.created_at.isoformat()
        )
    )
    conn.commit()
    conn.close()


def get_intake_by_id(intake_id: str, db_path: str = DB_FILE) -> Optional[PatientIntake]:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patient_intakes WHERE intake_id = ?", (intake_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return PatientIntake(
        intake_id=row["intake_id"],
        patient_id=row["patient_id"],
        symptoms=json.loads(row["symptoms"]),
        age=row["age"],
        gender=row["gender"],
        additional_notes=row["additional_notes"],
        created_at=datetime.fromisoformat(row["created_at"])
    )


def list_all_intakes(db_path: str = DB_FILE) -> List[PatientIntake]:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patient_intakes")
    rows = cursor.fetchall()
    conn.close()

    return [
        PatientIntake(
            intake_id=r["intake_id"],
            patient_id=r["patient_id"],
            symptoms=json.loads(r["symptoms"]),
            age=r["age"],
            gender=r["gender"],
            additional_notes=r["additional_notes"],
            created_at=datetime.fromisoformat(r["created_at"])
        )
        for r in rows
    ]


def list_intakes_by_patient_id(patient_id: str, db_path: str = DB_FILE) -> List[PatientIntake]:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patient_intakes WHERE patient_id = ?", (patient_id,))
    rows = cursor.fetchall()
    conn.close()

    return [
        PatientIntake(
            intake_id=r["intake_id"],
            patient_id=r["patient_id"],
            symptoms=json.loads(r["symptoms"]),
            age=r["age"],
            gender=r["gender"],
            additional_notes=r["additional_notes"],
            created_at=datetime.fromisoformat(r["created_at"])
        )
        for r in rows
    ]


# =====================================================================
# TRIAGE RESULT CRUD
# =====================================================================

def insert_triage(triage: TriageResult, db_path: str = DB_FILE) -> None:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO triage_results 
        (triage_id, intake_id, urgency_level, reasoning, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            triage.triage_id,
            triage.intake_id,
            triage.urgency_level,
            triage.reasoning,
            triage.created_at.isoformat()
        )
    )
    conn.commit()
    conn.close()


def get_triage_by_id(triage_id: str, db_path: str = DB_FILE) -> Optional[TriageResult]:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM triage_results WHERE triage_id = ?", (triage_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return TriageResult(
        triage_id=row["triage_id"],
        intake_id=row["intake_id"],
        urgency_level=row["urgency_level"],
        reasoning=row["reasoning"],
        created_at=datetime.fromisoformat(row["created_at"])
    )


def get_triage_by_intake_id(intake_id: str, db_path: str = DB_FILE) -> Optional[TriageResult]:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM triage_results WHERE intake_id = ?", (intake_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return TriageResult(
        triage_id=row["triage_id"],
        intake_id=row["intake_id"],
        urgency_level=row["urgency_level"],
        reasoning=row["reasoning"],
        created_at=datetime.fromisoformat(row["created_at"])
    )


def list_all_triage(db_path: str = DB_FILE) -> List[TriageResult]:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM triage_results")
    rows = cursor.fetchall()
    conn.close()

    return [
        TriageResult(
            triage_id=r["triage_id"],
            intake_id=r["intake_id"],
            urgency_level=r["urgency_level"],
            reasoning=r["reasoning"],
            created_at=datetime.fromisoformat(r["created_at"])
        )
        for r in rows
    ]


# =====================================================================
# ROUTING SUGGESTION CRUD
# =====================================================================

def insert_routing(routing: RoutingSuggestion, db_path: str = DB_FILE) -> None:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO routing_suggestions 
        (routing_id, intake_id, suggested_department, suggested_doctor_type, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            routing.routing_id,
            routing.intake_id,
            routing.suggested_department,
            routing.suggested_doctor_type,
            routing.created_at.isoformat()
        )
    )
    conn.commit()
    conn.close()


def get_routing_by_id(routing_id: str, db_path: str = DB_FILE) -> Optional[RoutingSuggestion]:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM routing_suggestions WHERE routing_id = ?", (routing_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return RoutingSuggestion(
        routing_id=row["routing_id"],
        intake_id=row["intake_id"],
        suggested_department=row["suggested_department"],
        suggested_doctor_type=row["suggested_doctor_type"],
        created_at=datetime.fromisoformat(row["created_at"])
    )


def get_routing_by_intake_id(intake_id: str, db_path: str = DB_FILE) -> Optional[RoutingSuggestion]:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM routing_suggestions WHERE intake_id = ?", (intake_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return RoutingSuggestion(
        routing_id=row["routing_id"],
        intake_id=row["intake_id"],
        suggested_department=row["suggested_department"],
        suggested_doctor_type=row["suggested_doctor_type"],
        created_at=datetime.fromisoformat(row["created_at"])
    )


def list_all_routing(db_path: str = DB_FILE) -> List[RoutingSuggestion]:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM routing_suggestions")
    rows = cursor.fetchall()
    conn.close()

    return [
        RoutingSuggestion(
            routing_id=r["routing_id"],
            intake_id=r["intake_id"],
            suggested_department=r["suggested_department"],
            suggested_doctor_type=r["suggested_doctor_type"],
            created_at=datetime.fromisoformat(r["created_at"])
        )
        for r in rows
    ]
