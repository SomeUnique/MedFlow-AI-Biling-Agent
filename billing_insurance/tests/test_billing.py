import os
import tempfile
import pytest
from datetime import datetime

from billing_insurance.models.bill import Bill
from billing_insurance.models.insurance_policy import InsurancePolicy
from billing_insurance.models.claim import Claim
from billing_insurance.database.db import (
    create_tables,
    insert_policy,
    get_policy_by_id,
    insert_bill,
    get_bill_by_id,
    insert_claim,
    get_claim_by_id
)
from billing_insurance.services.billing_service import estimate_cost, generate_invoice, record_payment, generate_invoice_from_visit
from billing_insurance.services import hospital_client
from billing_insurance.services.insurance_service import (
    validate_insurance,
    submit_claim,
    get_claim_status,
)
from billing_insurance.agent.billing_agent import handle_query


@pytest.fixture
def temp_db():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    create_tables(db_path)
    yield db_path
    os.close(db_fd)
    if os.path.exists(db_path):
        os.remove(db_path)


def test_insurance_validation_valid_and_expired(temp_db):
    # Valid policy
    valid_policy = InsurancePolicy(
        policy_id="POL-VAL",
        patient_id="PAT-VALID",
        provider_name="EFU Life",
        coverage_percentage=85.0,
        max_limit=10000.0,
        excluded_treatments=[],
        is_expired=False
    )
    insert_policy(valid_policy, db_path=temp_db)

    res_valid = validate_insurance("PAT-VALID", db_path=temp_db)
    assert res_valid["is_valid"] is True
    assert res_valid["coverage_percentage"] == 85.0

    # Expired policy
    expired_policy = InsurancePolicy(
        policy_id="POL-EXP",
        patient_id="PAT-EXPIRED",
        provider_name="Adamjee Insurance",
        coverage_percentage=80.0,
        max_limit=5000.0,
        excluded_treatments=[],
        is_expired=True
    )
    insert_policy(expired_policy, db_path=temp_db)

    res_expired = validate_insurance("PAT-EXPIRED", db_path=temp_db)
    assert res_expired["is_valid"] is False
    assert "expired" in res_expired["reason"].lower()


def test_bill_generation_calculation_and_breakdown(temp_db):
    services = ["Consultation", "X-Ray"]
    bill = generate_invoice("PAT-BILL-1", services, db_path=temp_db)

    assert bill.patient_id == "PAT-BILL-1"
    assert "Consultation" in bill.breakdown
    assert "X-Ray" in bill.breakdown
    expected_total = bill.breakdown["Consultation"] + bill.breakdown["X-Ray"]
    assert bill.total_amount == expected_total

    # Verify saved in DB
    db_bill = get_bill_by_id(bill.bill_id, db_path=temp_db)
    assert db_bill is not None
    assert db_bill.total_amount == expected_total


def test_cost_estimation_known_treatment(temp_db):
    est = estimate_cost("CT Scan")
    assert est["treatment_type"] == "CT Scan"
    assert est["found"] is True
    assert est["estimated_price"] > 0
    assert "cost_range" in est


def test_claim_submission_pending_status(temp_db):
    policy = InsurancePolicy(
        policy_id="POL-CLM",
        patient_id="PAT-CLM-1",
        provider_name="Jubilee Insurance",
        coverage_percentage=90.0,
        max_limit=20000.0,
        excluded_treatments=[],
        is_expired=False
    )
    insert_policy(policy, db_path=temp_db)

    bill = generate_invoice("PAT-CLM-1", ["Blood Test"], db_path=temp_db)

    claim_res = submit_claim("PAT-CLM-1", bill.bill_id, db_path=temp_db)
    assert claim_res["status"] == "pending"
    assert "claim_id" in claim_res


def test_record_payment_partial_and_full(temp_db):
    bill = generate_invoice("PAT-PAY-1", ["Consultation"], db_path=temp_db)
    # total is 100.0
    
    # Partial
    res = record_payment(bill.bill_id, 40.0, "card", db_path=temp_db)
    assert res["amount_paid"] == 40.0
    assert res["amount_due"] == 60.0
    assert res["status"] == "unpaid"
    assert res["payment_method"] == "card"
    
    # Full
    res2 = record_payment(bill.bill_id, 60.0, "cash", db_path=temp_db)
    assert res2["amount_paid"] == 100.0
    assert res2["amount_due"] == 0.0
    assert res2["status"] == "paid"
    assert res2["payment_method"] == "cash"


def test_hospital_client_mocks():
    fee_info = hospital_client.get_doctor_fee("DOC-001")
    assert fee_info["doctor_name"] == "Dr. Ayesha Khan"
    assert "consultation_fee" in fee_info

    visits = hospital_client.get_patient_visit_history("PAT-101")
    assert len(visits) > 0
    assert "visit_id" in visits[0]


def test_generate_invoice_from_visit(temp_db):
    bill = generate_invoice_from_visit("PAT-101", "VISIT-001", db_path=temp_db)
    assert bill.patient_id == "PAT-101"
    # Should include consultation from doc fee
    assert any("Consultation" in s for s in bill.breakdown.keys())
    assert bill.total_amount > 1500.0 # Fee + other services


def test_agent_total_bill_query(temp_db):
    response = handle_query("What is my total bill for recent visit?", "PAT-101", db_path=temp_db)
    # The history returns 2 visits, the last one is VISIT-002, which uses DOC-004 (Dr. Bilal Hassan)
    assert "Dr. Bilal Hassan" in response
    assert "Total amount due" in response
