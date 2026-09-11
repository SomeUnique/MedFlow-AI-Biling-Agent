import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from billing_insurance.models.bill import Bill
from billing_insurance.database import db
from billing_insurance.services import hospital_client

# Internal price table for demo purposes
PRICE_TABLE = {
    "consultation": {"min_cost": 50.0, "max_cost": 150.0, "price": 100.0},
    "general consultation": {"min_cost": 50.0, "max_cost": 150.0, "price": 100.0},
    "x-ray": {"min_cost": 100.0, "max_cost": 300.0, "price": 200.0},
    "x-ray chest": {"min_cost": 100.0, "max_cost": 300.0, "price": 200.0},
    "blood test": {"min_cost": 30.0, "max_cost": 120.0, "price": 80.0},
    "lab test": {"min_cost": 30.0, "max_cost": 120.0, "price": 75.0},
    "ct scan": {"min_cost": 800.0, "max_cost": 2000.0, "price": 1200.0},
    "mri": {"min_cost": 1200.0, "max_cost": 3000.0, "price": 1800.0},
    "mri brain scan": {"min_cost": 1200.0, "max_cost": 3000.0, "price": 1800.0},
    "minor surgery": {"min_cost": 500.0, "max_cost": 2500.0, "price": 1500.0},
    "major surgery": {"min_cost": 5000.0, "max_cost": 25000.0, "price": 15000.0},
    "icu per day": {"min_cost": 1000.0, "max_cost": 4000.0, "price": 2500.0},
    "emergency room visit": {"min_cost": 300.0, "max_cost": 1000.0, "price": 500.0},
    "medication": {"min_cost": 20.0, "max_cost": 200.0, "price": 100.0},
    "dental surgery": {"min_cost": 400.0, "max_cost": 1500.0, "price": 800.0},
    "anesthesia": {"min_cost": 200.0, "max_cost": 600.0, "price": 350.0},
    "neurology consultation": {"min_cost": 150.0, "max_cost": 400.0, "price": 250.0},
}

DEFAULT_SERVICE_COST = {"min_cost": 100.0, "max_cost": 500.0, "price": 250.0}


def estimate_cost(treatment_type: str) -> Dict[str, Any]:
    """
    Returns an estimated cost range and standard price for common treatments.
    """
    key = treatment_type.strip().lower()
    item = PRICE_TABLE.get(key)

    if not item:
        # Check partial match
        for known_service, data in PRICE_TABLE.items():
            if known_service in key or key in known_service:
                item = data
                break

    if not item:
        item = DEFAULT_SERVICE_COST

    return {
        "treatment_type": treatment_type,
        "found": key in PRICE_TABLE,
        "cost_range": {
            "min_cost": item["min_cost"],
            "max_cost": item["max_cost"]
        },
        "estimated_price": item["price"],
        "currency": "USD"
    }


def generate_invoice(patient_id: str, services: List[str], db_path: Optional[str] = None) -> Bill:
    """
    Calculates total from the price table, saves a Bill to the database,
    and returns invoice details with a cost breakdown.
    """
    breakdown: Dict[str, float] = {}
    total_amount = 0.0

    for service in services:
        estimation = estimate_cost(service)
        cost = estimation["estimated_price"]
        breakdown[service] = cost
        total_amount += cost

    bill_id = f"BILL-{uuid.uuid4().hex[:8].upper()}"

    bill = Bill(
        bill_id=bill_id,
        patient_id=patient_id,
        services=services,
        breakdown=breakdown,
        total_amount=total_amount,
        currency="USD",
        status="unpaid",
        amount_paid=0.0,
        amount_due=total_amount,
        created_at=datetime.now()
    )

    if db_path:
        db.insert_bill(bill, db_path=db_path)
    else:
        db.insert_bill(bill)

    return bill

def record_payment(bill_id: str, amount: float, payment_method: str, db_path: Optional[str] = None) -> Dict:
    """
    Validates the bill exists, updates it in the database, and returns updated status.
    """
    if db_path:
        bill = db.get_bill_by_id(bill_id, db_path=db_path)
        if not bill:
            raise ValueError(f"Bill '{bill_id}' not found.")
        db.update_bill_payment(bill_id, amount, payment_method, db_path=db_path)
        updated_bill = db.get_bill_by_id(bill_id, db_path=db_path)
    else:
        bill = db.get_bill_by_id(bill_id)
        if not bill:
            raise ValueError(f"Bill '{bill_id}' not found.")
        db.update_bill_payment(bill_id, amount, payment_method)
        updated_bill = db.get_bill_by_id(bill_id)

    if not updated_bill:
        raise ValueError(f"Bill '{bill_id}' could not be retrieved after payment update.")

    return {
        "bill_id": updated_bill.bill_id,
        "amount_paid": updated_bill.amount_paid,
        "amount_due": updated_bill.amount_due,
        "status": updated_bill.status,
        "payment_method": updated_bill.payment_method
    }


def generate_invoice_from_visit(patient_id: str, visit_id: str, db_path: Optional[str] = None) -> Bill:
    """
    Fetches visit details from Hospital API, calculates costs including doctor fee,
    and generates a full Bill.
    """
    history = hospital_client.get_patient_visit_history(patient_id)
    visit = next((v for v in history if v["visit_id"] == visit_id), None)
    if not visit:
        raise ValueError(f"Visit '{visit_id}' not found for patient '{patient_id}'.")

    doctor_info = hospital_client.get_doctor_fee(visit["doctor_id"])
    
    # Calculate costs
    breakdown: Dict[str, float] = {}
    total_amount = 0.0
    
    # Add doctor fee as "Consultation"
    doctor_fee = doctor_info["consultation_fee"]
    breakdown[f"Consultation ({doctor_info['doctor_name']} - {doctor_info['department']})"] = doctor_fee
    total_amount += doctor_fee
    
    # Process other services
    for service in visit["services"]:
        if service.lower() == "consultation":
            continue
        estimation = estimate_cost(service)
        cost = estimation["estimated_price"]
        breakdown[service] = cost
        total_amount += cost
        
    bill_id = f"BILL-{uuid.uuid4().hex[:8].upper()}"
    bill = Bill(
        bill_id=bill_id,
        patient_id=patient_id,
        services=visit["services"] + ["Consultation"],
        breakdown=breakdown,
        total_amount=total_amount,
        currency="USD",
        amount_paid=0.0,
        amount_due=total_amount,
        created_at=datetime.now()
    )
    
    if db_path:
        db.insert_bill(bill, db_path=db_path)
    else:
        db.insert_bill(bill)
        
    return bill
