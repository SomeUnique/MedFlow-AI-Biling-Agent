from typing import Dict, List, Any

# Placeholder URL for future integration with the Hospital Operations backend
HOSPITAL_API_BASE_URL = "http://localhost:8002"

# Mock data store
MOCK_DOCTORS = {
    "DOC-001": {"doctor_id": "DOC-001", "doctor_name": "Dr. Ayesha Khan", "department": "Cardiology", "consultation_fee": 1500.0},
    "DOC-002": {"doctor_id": "DOC-002", "doctor_name": "Dr. Ahmed Raza", "department": "Neurology", "consultation_fee": 2000.0},
    "DOC-003": {"doctor_id": "DOC-003", "doctor_name": "Dr. Sarah Ahmed", "department": "Pediatrics", "consultation_fee": 1200.0},
    "DOC-004": {"doctor_id": "DOC-004", "doctor_name": "Dr. Bilal Hassan", "department": "General Medicine", "consultation_fee": 1000.0}
}

MOCK_VISITS = {
    "PAT-101": [
        {"visit_id": "VISIT-001", "patient_id": "PAT-101", "doctor_id": "DOC-001", "department": "Cardiology", "date": "2026-08-15", "services": ["Consultation", "ECG"]},
        {"visit_id": "VISIT-002", "patient_id": "PAT-101", "doctor_id": "DOC-004", "department": "General Medicine", "date": "2026-09-01", "services": ["Consultation"]}
    ],
    "PAT-102": [
        {"visit_id": "VISIT-003", "patient_id": "PAT-102", "doctor_id": "DOC-002", "department": "Neurology", "date": "2026-08-20", "services": ["Consultation", "MRI"]}
    ]
}

def get_doctor_fee(doctor_id: str) -> Dict[str, Any]:
    """
    TODO: Replace this mock with an actual HTTP call to the Hospital module's 
    GET /hospital/doctors/{doctor_id} endpoint once available using `requests` 
    library to the HOSPITAL_API_BASE_URL.
    """
    return MOCK_DOCTORS.get(doctor_id, {
        "doctor_id": doctor_id, 
        "doctor_name": "Unknown", 
        "department": "Unknown", 
        "consultation_fee": 500.0
    })

def get_patient_visit_history(patient_id: str) -> List[Dict[str, Any]]:
    """
    TODO: Replace this mock with an actual HTTP call to the Hospital module's 
    GET /hospital/patients/{patient_id}/visit-history endpoint once available 
    using `requests` library to the HOSPITAL_API_BASE_URL.
    """
    return MOCK_VISITS.get(patient_id, [])
