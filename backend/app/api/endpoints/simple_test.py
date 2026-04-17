from fastapi import APIRouter
from typing import List

router = APIRouter()

@router.get("/test/simple", tags=["test"])
async def simple_test():
    """
    Simple test endpoint without database
    """
    return {"message": "Server is working", "status": "ok"}

@router.get("/test/patients/{patient_id}/lab-results-mock", tags=["test"])
async def get_mock_lab_results(patient_id: int):
    """
    Mock lab results for testing - no database required
    """
    mock_results = [
        {
            "id": 1,
            "patient_id": patient_id,
            "test_name": "Cholesterol Total",
            "result": "180",
            "unit": "mg/dL",
            "reference_range": "<200",
            "timestamp": "2024-01-15T10:30:00",
            "status": "normal"
        },
        {
            "id": 2,
            "patient_id": patient_id,
            "test_name": "White Blood Cell Count",
            "result": "7500",
            "unit": "cells/μL",
            "reference_range": "4000-11000",
            "timestamp": "2024-01-15T10:30:00",
            "status": "normal"
        },
        {
            "id": 3,
            "patient_id": patient_id,
            "test_name": "Platelets",
            "result": "250000",
            "unit": "cells/μL",
            "reference_range": "150000-450000",
            "timestamp": "2024-01-15T10:30:00",
            "status": "normal"
        },
        {
            "id": 4,
            "patient_id": patient_id,
            "test_name": "Hemoglobin",
            "result": "14.5",
            "unit": "g/dL",
            "reference_range": "12.0-16.0",
            "timestamp": "2024-01-15T10:30:00",
            "status": "normal"
        },
        {
            "id": 5,
            "patient_id": patient_id,
            "test_name": "Blood Glucose",
            "result": "95",
            "unit": "mg/dL",
            "reference_range": "70-100",
            "timestamp": "2024-01-15T10:30:00",
            "status": "normal"
        }
    ]
    
    return mock_results