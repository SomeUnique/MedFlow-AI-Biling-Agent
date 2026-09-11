import sqlite3
import json
import os
from typing import List, Optional
from datetime import datetime

from billing_insurance.models.bill import Bill
from billing_insurance.models.insurance_policy import InsurancePolicy
from billing_insurance.models.claim import Claim

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "billing.db")


def get_connection(db_path: str = DB_FILE) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables(db_path: str = DB_FILE) -> None:
    conn = get_connection(db_path)
    cursor = conn.cursor()

    # Insurance Policies table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS insurance_policies (
            policy_id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            provider_name TEXT NOT NULL,
            coverage_percentage REAL NOT NULL,
            max_limit REAL,
            excluded_treatments TEXT NOT NULL,
            is_expired INTEGER NOT NULL DEFAULT 0
        )
    """)

    # Bills table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bills (
            bill_id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            services TEXT NOT NULL,
            breakdown TEXT NOT NULL,
            total_amount REAL NOT NULL,
            currency TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'unpaid',
            amount_paid REAL NOT NULL DEFAULT 0.0,
            amount_due REAL NOT NULL,
            payment_method TEXT,
            created_at TEXT NOT NULL
        )
    """)

    # Claims table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS claims (
            claim_id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            bill_id TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            submitted_at TEXT NOT NULL,
            FOREIGN KEY (bill_id) REFERENCES bills (bill_id)
        )
    """)

    conn.commit()
    conn.close()


def reset_db(db_path: str = DB_FILE) -> None:
    if os.path.exists(db_path):
        os.remove(db_path)
    create_tables(db_path)


# =====================================================================
# INSURANCE POLICY CRUD
# =====================================================================

def insert_policy(policy: InsurancePolicy, db_path: str = DB_FILE) -> None:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO insurance_policies 
        (policy_id, patient_id, provider_name, coverage_percentage, max_limit, excluded_treatments, is_expired)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            policy.policy_id,
            policy.patient_id,
            policy.provider_name,
            policy.coverage_percentage,
            policy.max_limit,
            json.dumps(policy.excluded_treatments),
            1 if policy.is_expired else 0
        )
    )
    conn.commit()
    conn.close()


def get_policy_by_id(policy_id: str, db_path: str = DB_FILE) -> Optional[InsurancePolicy]:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM insurance_policies WHERE policy_id = ?", (policy_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return InsurancePolicy(
        policy_id=row["policy_id"],
        patient_id=row["patient_id"],
        provider_name=row["provider_name"],
        coverage_percentage=row["coverage_percentage"],
        max_limit=row["max_limit"],
        excluded_treatments=json.loads(row["excluded_treatments"]),
        is_expired=bool(row["is_expired"])
    )


def get_policy_by_patient_id(patient_id: str, db_path: str = DB_FILE) -> Optional[InsurancePolicy]:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM insurance_policies WHERE patient_id = ?", (patient_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return InsurancePolicy(
        policy_id=row["policy_id"],
        patient_id=row["patient_id"],
        provider_name=row["provider_name"],
        coverage_percentage=row["coverage_percentage"],
        max_limit=row["max_limit"],
        excluded_treatments=json.loads(row["excluded_treatments"]),
        is_expired=bool(row["is_expired"])
    )


def update_policy_status(policy_id: str, is_expired: bool, db_path: str = DB_FILE) -> bool:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE insurance_policies SET is_expired = ? WHERE policy_id = ?",
        (1 if is_expired else 0, policy_id)
    )
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated


def list_all_policies(db_path: str = DB_FILE) -> List[InsurancePolicy]:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM insurance_policies")
    rows = cursor.fetchall()
    conn.close()

    return [
        InsurancePolicy(
            policy_id=r["policy_id"],
            patient_id=r["patient_id"],
            provider_name=r["provider_name"],
            coverage_percentage=r["coverage_percentage"],
            max_limit=r["max_limit"],
            excluded_treatments=json.loads(r["excluded_treatments"]),
            is_expired=bool(r["is_expired"])
        )
        for r in rows
    ]


# =====================================================================
# BILL CRUD
# =====================================================================

def insert_bill(bill: Bill, db_path: str = DB_FILE) -> None:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO bills 
        (bill_id, patient_id, services, breakdown, total_amount, currency, status, amount_paid, amount_due, payment_method, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            bill.bill_id,
            bill.patient_id,
            json.dumps(bill.services),
            json.dumps(bill.breakdown),
            bill.total_amount,
            bill.currency,
            bill.status,
            bill.amount_paid,
            bill.amount_due,
            bill.payment_method,
            bill.created_at.isoformat()
        )
    )
    conn.commit()
    conn.close()


def get_bill_by_id(bill_id: str, db_path: str = DB_FILE) -> Optional[Bill]:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bills WHERE bill_id = ?", (bill_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return Bill(
        bill_id=row["bill_id"],
        patient_id=row["patient_id"],
        services=json.loads(row["services"]),
        breakdown=json.loads(row["breakdown"]),
        total_amount=row["total_amount"],
        currency=row["currency"],
        status=row["status"],
        amount_paid=row["amount_paid"],
        amount_due=row["amount_due"],
        payment_method=row["payment_method"],
        created_at=datetime.fromisoformat(row["created_at"])
    )


def update_bill_payment(bill_id: str, amount_paid: float, payment_method: str, db_path: str = DB_FILE) -> bool:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    # Fetch current bill
    cursor.execute("SELECT * FROM bills WHERE bill_id = ?", (bill_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False
    
    new_amount_paid = row["amount_paid"] + amount_paid
    new_amount_due = max(0.0, row["total_amount"] - new_amount_paid)
    new_status = "paid" if new_amount_due <= 0.0 else "unpaid"
    
    cursor.execute(
        """
        UPDATE bills 
        SET amount_paid = ?, amount_due = ?, payment_method = ?, status = ? 
        WHERE bill_id = ?
        """,
        (new_amount_paid, new_amount_due, payment_method, new_status, bill_id)
    )
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated


def update_bill_status(bill_id: str, status: str, db_path: str = DB_FILE) -> bool:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE bills SET status = ? WHERE bill_id = ?",
        (status, bill_id)
    )
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated


def list_all_bills(db_path: str = DB_FILE) -> List[Bill]:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bills")
    rows = cursor.fetchall()
    conn.close()

    return [
        Bill(
            bill_id=r["bill_id"],
            patient_id=r["patient_id"],
            services=json.loads(r["services"]),
            breakdown=json.loads(r["breakdown"]),
            total_amount=r["total_amount"],
            currency=r["currency"],
            status=r["status"],
            amount_paid=r["amount_paid"],
            amount_due=r["amount_due"],
            payment_method=r["payment_method"],
            created_at=datetime.fromisoformat(r["created_at"])
        )
        for r in rows
    ]


# =====================================================================
# CLAIM CRUD
# =====================================================================

def insert_claim(claim: Claim, db_path: str = DB_FILE) -> None:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO claims 
        (claim_id, patient_id, bill_id, status, submitted_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            claim.claim_id,
            claim.patient_id,
            claim.bill_id,
            claim.status,
            claim.submitted_at.isoformat()
        )
    )
    conn.commit()
    conn.close()


def get_claim_by_id(claim_id: str, db_path: str = DB_FILE) -> Optional[Claim]:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM claims WHERE claim_id = ?", (claim_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return Claim(
        claim_id=row["claim_id"],
        patient_id=row["patient_id"],
        bill_id=row["bill_id"],
        status=row["status"],
        submitted_at=datetime.fromisoformat(row["submitted_at"])
    )


def update_claim_status(claim_id: str, status: str, db_path: str = DB_FILE) -> bool:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE claims SET status = ? WHERE claim_id = ?",
        (status, claim_id)
    )
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated


def list_all_claims(db_path: str = DB_FILE) -> List[Claim]:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM claims")
    rows = cursor.fetchall()
    conn.close()

    return [
        Claim(
            claim_id=r["claim_id"],
            patient_id=r["patient_id"],
            bill_id=r["bill_id"],
            status=r["status"],
            submitted_at=datetime.fromisoformat(r["submitted_at"])
        )
        for r in rows
    ]
