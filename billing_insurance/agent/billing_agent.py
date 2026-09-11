# Main agent logic — understands billing/insurance queries

from typing import Dict, Any, Optional
from billing_insurance.services import billing_service, insurance_service, hospital_client


def handle_query(query: str, patient_id: str, db_path: Optional[str] = None) -> str:
    """
    Detects whether the query is billing-related or insurance-related,
    calls the appropriate service, and returns a natural-language response string.
    """
    q_lower = query.lower()

    # Insurance keywords in English and Roman Urdu
    insurance_keywords = [
        "insurance", "claim", "policy", "coverage", "expired", "bima", 
        "claim status", "status", "claim check", "eligibility"
    ]
    
    # Billing keywords in English and Roman Urdu
    billing_keywords = [
        "cost", "bill", "invoice", "price", "fee", "kharcha", "kitna", 
        "estimate", "charges", "payment", "paisa", "rupees", "usd", "mera bill", "total bill"
    ]

    # Intent detection
    is_insurance = any(kw in q_lower for kw in insurance_keywords)
    is_billing = any(kw in q_lower for kw in billing_keywords)

    # If ambiguous or both, check specific context or default to billing/general
    if is_insurance and not is_billing:
        # ... (unchanged)
        # Check if asking for claim status
        if "status" in q_lower or "claim" in q_lower:
            val = insurance_service.validate_insurance(patient_id, db_path=db_path)
            if val["is_valid"]:
                return (
                    f"Insurance status for patient {patient_id}: Active policy with "
                    f"{val['policy_details'].provider_name}. Coverage is {val['coverage_percentage']}%."
                )
            else:
                return f"Insurance status for patient {patient_id}: {val['reason']}"
        else:
            val = insurance_service.validate_insurance(patient_id, db_path=db_path)
            return f"Insurance Validation: {val['reason']} (Coverage: {val['coverage_percentage']}%)"

    elif is_billing or not is_insurance:
        # Billing query handling
        if any(kw in q_lower for kw in ["total bill", "kitna bill", "mera bill", "visit ka bill"]):
            history = hospital_client.get_patient_visit_history(patient_id)
            if not history:
                return "No visit history found to generate a bill."
            
            recent_visit = history[-1]
            bill = billing_service.generate_invoice_from_visit(patient_id, recent_visit["visit_id"], db_path=db_path)
            
            doctor_info = hospital_client.get_doctor_fee(recent_visit["doctor_id"])
            
            # Build response
            res = f"Bill for visit on {recent_visit['date']} (ID: {bill.bill_id}):\n"
            res += f"- Doctor: {doctor_info['doctor_name']} ({doctor_info['department']})\n"
            for service, cost in bill.breakdown.items():
                res += f"- {service}: {cost} USD\n"
            res += f"Total amount due: {bill.total_amount} USD"
            return res

        common_treatments = [
            "consultation", "x-ray", "blood test", "ct scan", "mri", 
            "minor surgery", "major surgery", "icu", "emergency", "medication"
        ]
        
        found_treatments = [t for t in common_treatments if t in q_lower]
        
        if found_treatments:
            est = billing_service.estimate_cost(found_treatments[0])
            return (
                f"Estimated cost for {found_treatments[0].title()} is {est['estimated_price']} {est['currency']} "
                f"(Range: {est['cost_range']['min_cost']} - {est['cost_range']['max_cost']} {est['currency']})."
            )
        else:
            # Default fallback billing response
            return (
                f"I understand you are asking about billing or charges for patient {patient_id}. "
                "You can request a cost estimate for specific treatments like X-Ray, Consultation, or Blood Test, "
                "or ask for your 'total bill' for a recent visit."
            )

    return f"I'm sorry, I couldn't clearly determine whether you need help with billing or insurance for query: '{query}'."
