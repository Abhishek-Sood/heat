"""
Lab Results API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import date, datetime

from app.core.auth import get_current_user
from app.db.database import get_database
from app.db.models import User, LabResult
from pydantic import BaseModel

router = APIRouter()

class LabResultResponse(BaseModel):
    id: int
    patient_id: int
    test_name: str
    result: str
    unit: str
    reference_range: str
    timestamp: Optional[str] = None
    status: str = "normal"  # normal, high, low, unknown

    class Config:
        from_attributes = True

def analyze_result_status(result: str, reference_range: str) -> str:
    """
    Analyze if a lab result is normal, high, or low based on reference range
    """
    if not result or not reference_range:
        return "unknown"
    
    try:
        result_value = float(result)
    except ValueError:
        # If result is not numeric, check for text indicators
        result_lower = result.lower()
        if 'normal' in result_lower:
            return "normal"
        elif any(word in result_lower for word in ['high', 'elevated', 'increased']):
            return "high"
        elif any(word in result_lower for word in ['low', 'decreased', 'reduced']):
            return "low"
        return "unknown"
    
    # Parse numeric range (e.g., "12-16", "70-100", "<200", "150000-450000")
    ref_lower = reference_range.lower().strip()
    
    # Handle "<X" format
    if ref_lower.startswith('<'):
        try:
            max_val = float(ref_lower[1:])
            return "normal" if result_value < max_val else "high"
        except ValueError:
            return "unknown"
    
    # Handle ">X" format  
    if ref_lower.startswith('>'):
        try:
            min_val = float(ref_lower[1:])
            return "normal" if result_value > min_val else "low"
        except ValueError:
            return "unknown"
    
    # Handle "X-Y" range format
    if '-' in ref_lower:
        try:
            parts = ref_lower.split('-')
            if len(parts) == 2:
                min_val = float(parts[0].strip())
                max_val = float(parts[1].strip())
                
                if result_value < min_val:
                    return "low"
                elif result_value > max_val:
                    return "high"
                else:
                    return "normal"
        except ValueError:
            return "unknown"
    
    return "unknown"

@router.get("/patients/{patient_id}/lab-results", response_model=List[LabResultResponse], tags=["lab-results"])
async def get_patient_lab_results(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
) -> List[LabResultResponse]:
    """
    Get all lab results for a specific patient (filtered by user for multi-tenancy)
    """
    try:
        # Query lab results with user filtering for multi-tenancy
        lab_results = db.query(LabResult).filter(
            LabResult.patient_id == patient_id,
            LabResult.user_id == current_user.id
        ).order_by(LabResult.timestamp.desc()).all()
        
        if not lab_results:
            return []
        
        # Convert to response format with status analysis
        results = []
        for lab_result in lab_results:
            # Analyze if result is normal/high/low
            status = analyze_result_status(lab_result.result, lab_result.reference_range)
            
            # Convert timestamp to ISO string for JSON serialization
            timestamp_str = None
            if lab_result.timestamp:
                if isinstance(lab_result.timestamp, datetime):
                    timestamp_str = lab_result.timestamp.isoformat()
                elif isinstance(lab_result.timestamp, date):
                    timestamp_str = lab_result.timestamp.isoformat()
                else:
                    timestamp_str = str(lab_result.timestamp)
            
            result_data = LabResultResponse(
                id=lab_result.id,
                patient_id=lab_result.patient_id,
                test_name=lab_result.test_name,
                result=lab_result.result,
                unit=lab_result.unit or "",
                reference_range=lab_result.reference_range or "",
                timestamp=timestamp_str,
                status=status
            )
            results.append(result_data)
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching lab results: {str(e)}")

@router.get("/test/patients/{patient_id}/lab-results", response_model=List[LabResultResponse], tags=["lab-results-test"])
async def get_patient_lab_results_test(
    patient_id: int,
    db: Session = Depends(get_database)
) -> List[LabResultResponse]:
    """
    TEST ENDPOINT: Get all lab results for a specific patient (NO AUTHENTICATION)
    """
    try:
        # Query lab results without user filtering for testing
        lab_results = db.query(LabResult).filter(
            LabResult.patient_id == patient_id
        ).order_by(LabResult.timestamp.desc()).all()
        
        if not lab_results:
            return []
        
        # Convert to response format with status analysis
        results = []
        for lab_result in lab_results:
            # Analyze if result is normal/high/low
            status = analyze_result_status(lab_result.result, lab_result.reference_range)
            
            # Convert timestamp to ISO string for JSON serialization
            timestamp_str = None
            if lab_result.timestamp:
                if isinstance(lab_result.timestamp, datetime):
                    timestamp_str = lab_result.timestamp.isoformat()
                elif isinstance(lab_result.timestamp, date):
                    timestamp_str = lab_result.timestamp.isoformat()
                else:
                    timestamp_str = str(lab_result.timestamp)
            
            result_data = LabResultResponse(
                id=lab_result.id,
                patient_id=lab_result.patient_id,
                test_name=lab_result.test_name,
                result=lab_result.result,
                unit=lab_result.unit or "",
                reference_range=lab_result.reference_range or "",
                timestamp=timestamp_str,
                status=status
            )
            results.append(result_data)
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching lab results: {str(e)}")

@router.get("/patients/{patient_id}/lab-results/summary", tags=["lab-results"])
async def get_patient_lab_results_summary(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
) -> Dict[str, Any]:
    """
    Get a summary of lab results for a patient including counts of normal/abnormal results
    """
    try:
        # Get all lab results for the patient
        lab_results = db.query(LabResult).filter(
            LabResult.patient_id == patient_id,
            LabResult.user_id == current_user.id
        ).all()
        
        if not lab_results:
            return {
                "patient_id": patient_id,
                "total_tests": 0,
                "normal_count": 0,
                "abnormal_count": 0,
                "high_count": 0,
                "low_count": 0,
                "unknown_count": 0,
                "latest_test_date": None
            }
        
        # Analyze results
        normal_count = 0
        high_count = 0
        low_count = 0
        unknown_count = 0
        
        latest_date = None
        
        for lab_result in lab_results:
            status = analyze_result_status(lab_result.result, lab_result.reference_range)
            
            if status == "normal":
                normal_count += 1
            elif status == "high":
                high_count += 1
            elif status == "low":
                low_count += 1
            else:
                unknown_count += 1
            
            # Track latest date
            if lab_result.timestamp:
                if latest_date is None or lab_result.timestamp > latest_date:
                    latest_date = lab_result.timestamp
        
        abnormal_count = high_count + low_count
        
        return {
            "patient_id": patient_id,
            "total_tests": len(lab_results),
            "normal_count": normal_count,
            "abnormal_count": abnormal_count,
            "high_count": high_count,
            "low_count": low_count,
            "unknown_count": unknown_count,
            "latest_test_date": latest_date.isoformat() if latest_date else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating lab results summary: {str(e)}")