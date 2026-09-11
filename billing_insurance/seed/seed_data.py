import sys
import os
from datetime import datetime, timedelta

# Ensure python path includes project root when run directly as `python seed/seed_data.py`
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from billing_insurance.database.db import (
    reset_db,
    insert_policy,
    insert_bill,
    insert_claim,
    list_all_policies,
    list_all_bills,
    list_all_claims
)
from billing_insurance.models.insurance_policy import InsurancePolicy
from billing_insurance.models.bill import Bill
from billing_insurance.models.claim import Claim


def seed():
    print("Resetting and initializing database...")
    reset_db()

    # 1. Seed Insurance Policies (3-4 companies, 6 patients, valid/expired mix)
    policies = [
        InsurancePolicy(
            policy_id="POL-001",
            patient_id="PAT-101",
            provider_name="Adamjee Insurance",
            coverage_percentage=80.0,
            max_limit=10000.0,
            excluded_treatments=["Cosmetic Surgery", "Experimental Therapy"],
            is_expired=False
        ),
        InsurancePolicy(
            policy_id="POL-002",
            patient_id="PAT-102",
            provider_name="EFU Life",
            coverage_percentage=90.0,
            max_limit=25000.0,
            excluded_treatments=["Dental Care", "Vision Care"],
            is_expired=False
        ),
        InsurancePolicy(
            policy_id="POL-003",
            patient_id="PAT-103",
            provider_name="Jubilee Insurance",
            coverage_percentage=70.0,
            max_limit=5000.0,
            excluded_treatments=["Pre-existing Conditions", "Organ Transplant"],
            is_expired=True  # Expired
        ),
        InsurancePolicy(
            policy_id="POL-004",
            patient_id="PAT-104",
            provider_name="State Life",
            coverage_percentage=100.0,
            max_limit=50000.0,
            excluded_treatments=[],
            is_expired=False
        ),
        InsurancePolicy(
            policy_id="POL-005",
            patient_id="PAT-105",
            provider_name="Adamjee Insurance",
            coverage_percentage=85.0,
            max_limit=15000.0,
            excluded_treatments=["Aesthetic Procedures"],
            is_expired=True  # Expired
        ),
        InsurancePolicy(
            policy_id="POL-006",
            patient_id="PAT-106",
            provider_name="EFU Life",
            coverage_percentage=75.0,
            max_limit=8000.0,
            excluded_treatments=["Psychotherapy"],
            is_expired=False
        )
    ]

    for p in policies:
        insert_policy(p)
    print(f"Inserted {len(policies)} insurance policies.")

    # 2. Seed Sample Bills
    now = datetime.now()
    bills = [
        Bill(
            bill_id="BILL-1001",
            patient_id="PAT-101",
            services=["General Consultation", "Blood Test", "X-Ray Chest"],
            breakdown={"General Consultation": 150.0, "Blood Test": 80.0, "X-Ray Chest": 200.0},
            total_amount=430.0,
            currency="USD",
            status="unpaid",
            created_at=now - timedelta(days=5)
        ),
        Bill(
            bill_id="BILL-1002",
            patient_id="PAT-102",
            services=["Emergency Room Visit", "CT Scan", "Medication"],
            breakdown={"Emergency Room Visit": 500.0, "CT Scan": 1200.0, "Medication": 300.0},
            total_amount=2000.0,
            currency="USD",
            status="paid",
            created_at=now - timedelta(days=3)
        ),
        Bill(
            bill_id="BILL-1003",
            patient_id="PAT-103",
            services=["Dental Surgery", "Anesthesia"],
            breakdown={"Dental Surgery": 800.0, "Anesthesia": 350.0},
            total_amount=1150.0,
            currency="USD",
            status="unpaid",
            created_at=now - timedelta(days=2)
        ),
        Bill(
            bill_id="BILL-1004",
            patient_id="PAT-104",
            services=["MRI Brain Scan", "Neurology Consultation"],
            breakdown={"MRI Brain Scan": 1800.0, "Neurology Consultation": 250.0},
            total_amount=2050.0,
            currency="USD",
            status="unpaid",
            created_at=now - timedelta(days=1)
        )
    ]

    for b in bills:
        insert_bill(b)
    print(f"Inserted {len(bills)} bills.")

    # 3. Seed Sample Claims
    claims = [
        Claim(
            claim_id="CLM-5001",
            patient_id="PAT-102",
            bill_id="BILL-1002",
            status="approved",
            submitted_at=now - timedelta(days=2)
        ),
        Claim(
            claim_id="CLM-5002",
            patient_id="PAT-101",
            bill_id="BILL-1001",
            status="pending",
            submitted_at=now - timedelta(days=1)
        )
    ]

    for c in claims:
        insert_claim(c)
    print(f"Inserted {len(claims)} claims.")

    print("\nVerification:")
    print(f"Total Policies in DB: {len(list_all_policies())}")
    print(f"Total Bills in DB: {len(list_all_bills())}")
    print(f"Total Claims in DB: {len(list_all_claims())}")
    print("\nDatabase successfully seeded!")


if __name__ == "__main__":
    seed()
