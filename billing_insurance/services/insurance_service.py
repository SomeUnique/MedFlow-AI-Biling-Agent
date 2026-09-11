import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from billing_insurance.models.claim import Claim
from billing_insurance.models.insurance_policy import InsurancePolicy
from billing_insurance.database import db


def validate_insurance(patient_id: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Looks up the patient's policy, checks if expired,
    and returns validation results including coverage percentage and policy details.
    """
    if db_path:
        policy = db.get_policy_by_patient_id(patient_id, db_path=db_path)
    else:
        policy = db.get_policy_by_patient_id(patient_id)

    if not policy:
        return {
            "is_valid": False,
            "coverage_percentage": 0.0,
            "policy_details": None,
            "reason": f"No policy found for patient '{patient_id}'."
        }

    if policy.is_expired:
        return {
            "is_valid": False,
            "coverage_percentage": 0.0,
            "policy_details": policy,
            "reason": f"Policy '{policy.policy_id}' for patient '{patient_id}' is expired."
        }

    return {
        "is_valid": True,
        "coverage_percentage": policy.coverage_percentage,
        "policy_details": policy,
        "reason": f"Active policy '{policy.policy_id}' verified with provider '{policy.provider_name}'."
    }


def submit_claim(patient_id: str, bill_id: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Validates insurance, creates a Claim with status "pending",
    saves to database, and returns claim_id + status details.
    """
    # Validate insurance status
    validation = validate_insurance(patient_id, db_path=db_path)

    # Fetch bill details
    if db_path:
        bill = db.get_bill_by_id(bill_id, db_path=db_path)
    else:
        bill = db.get_bill_by_id(bill_id)

    claim_id = f"CLM-{uuid.uuid4().hex[:8].upper()}"
    submitted_at = datetime.now()

    # Determine status based on validation and bill existence
    if not bill:
        status = "rejected"
        reason = f"Bill '{bill_id}' not found."
    elif not validation["is_valid"]:
        status = "rejected"
        reason = validation["reason"]
    else:
        status = "pending"
        reason = "Claim submitted successfully and pending approval."

    claim = Claim(
        claim_id=claim_id,
        patient_id=patient_id,
        bill_id=bill_id,
        status=status,
        submitted_at=submitted_at
    )

    if db_path:
        db.insert_claim(claim, db_path=db_path)
    else:
        db.insert_claim(claim)

    return {
        "claim_id": claim_id,
        "patient_id": patient_id,
        "bill_id": bill_id,
        "status": status,
        "reason": reason,
        "submitted_at": submitted_at.isoformat()
    }


def get_claim_status(claim_id: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Looks up and returns the claim's current status and details.
    """
    if db_path:
        claim = db.get_claim_by_id(claim_id, db_path=db_path)
    else:
        claim = db.get_claim_by_id(claim_id)

    if not claim:
        return {
            "found": False,
            "claim_id": claim_id,
            "status": "not_found",
            "message": f"Claim '{claim_id}' not found."
        }

    return {
        "found": True,
        "claim_id": claim.claim_id,
        "patient_id": claim.patient_id,
        "bill_id": claim.bill_id,
        "status": claim.status,
        "submitted_at": claim.submitted_at.isoformat()
    }
