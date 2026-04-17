from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Any, Dict
from pydantic import BaseModel
from datetime import datetime

from app.mcp.deps import get_db_session
from app.db.models import LabResult, User
from app.core.auth import get_current_user

router = APIRouter()

class LabResultResponse(BaseModel):
    id: int
    patient_id: int
    test_name: str
    result: str
    unit: str
    reference_range: str
    timestamp: str
    status: str  # "normal", "high", "low", "unknown"

def analyze_result_status(result: str, reference_range: str = None) -> str:
    """
    Analyze the lab result status based on result value and reference range
    """
    if not result or not reference_range:
        return "unknown"
    
    try:
        # Clean the result value - remove units and extra text
        result_clean = result.strip()
        
        # Extract numeric value if possible
        numeric_value = None
        result_parts = result_clean.split()
        for part in result_parts:
            try:
                numeric_value = float(part.replace(',', ''))
                break
            except ValueError:
                continue
        
        if numeric_value is None:
            return "unknown"
        
        # Parse reference range
        ref_range_clean = reference_range.strip()
        
        # Handle different reference range formats
        if '-' in ref_range_clean:
            # Format: "12.0-16.0" or "150000-450000"
            try:
                range_parts = ref_range_clean.split('-')
                min_val = float(range_parts[0].strip().replace(',', ''))
                max_val = float(range_parts[1].strip().replace(',', ''))
                
                if numeric_value < min_val:
                    return "low"
                elif numeric_value > max_val:
                    return "high"
                else:
                    return "normal"
            except (ValueError, IndexError):
                pass
        
        elif ref_range_clean.startswith('<'):
            # Format: "<200"
            try:
                max_val = float(ref_range_clean[1:].strip().replace(',', ''))
                if numeric_value >= max_val:
                    return "high"
                else:
                    return "normal"
            except ValueError:
                pass
        
        elif ref_range_clean.startswith('>'):
            # Format: ">5.0"
            try:
                min_val = float(ref_range_clean[1:].strip().replace(',', ''))
                if numeric_value <= min_val:
                    return "low"
                else:
                    return "normal"
            except ValueError:
                pass
        
        return "unknown"
        
    except Exception:
        return "unknown"

@router.get("/patients/{patient_id}/lab-results", response_model=List[LabResultResponse], tags=["lab-results"])
async def get_patient_lab_results(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
) -> List[LabResultResponse]:
    """
    Get all lab results for a specific patient
    """
    try:
        # Get lab results for the patient (filtering by user_id for multi-tenancy)
        lab_results = db.query(LabResult).filter(
            LabResult.patient_id == patient_id,
            LabResult.user_id == current_user.id
        ).order_by(LabResult.timestamp.desc()).all()
        
        results = []
        for lab_result in lab_results:
            # Analyze the result status
            status = analyze_result_status(lab_result.result, lab_result.reference_range)
            
            # Handle timestamp conversion
            if hasattr(lab_result.timestamp, 'isoformat'):
                if hasattr(lab_result.timestamp, 'tzinfo') and lab_result.timestamp.tzinfo is not None:
                    timestamp_str = lab_result.timestamp.isoformat()
                else:
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

@router.get("/test/patients/{patient_id}/lab-results", response_model=List[LabResultResponse], tags=["lab-results"])
async def get_patient_lab_results_test(
    patient_id: int,
    db: Session = Depends(get_db_session)
) -> List[LabResultResponse]:
    """
    Test endpoint - Get all lab results for a specific patient (no auth)
    """
    try:
        # Get lab results for the patient (no auth filtering for testing)
        lab_results = db.query(LabResult).filter(
            LabResult.patient_id == patient_id
        ).order_by(LabResult.timestamp.desc()).all()
        
        results = []
        for lab_result in lab_results:
            # Analyze the result status
            status = analyze_result_status(lab_result.result, lab_result.reference_range)
            
            # Handle timestamp conversion
            if hasattr(lab_result.timestamp, 'isoformat'):
                if hasattr(lab_result.timestamp, 'tzinfo') and lab_result.timestamp.tzinfo is not None:
                    timestamp_str = lab_result.timestamp.isoformat()
                else:
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
    db: Session = Depends(get_db_session)
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
        
        total_results = len(lab_results)
        normal_count = 0
        high_count = 0
        low_count = 0
        unknown_count = 0
        
        # Analyze each result
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
        
        return {
            "patient_id": patient_id,
            "total_results": total_results,
            "normal_count": normal_count,
            "high_count": high_count,
            "low_count": low_count,
            "unknown_count": unknown_count,
            "abnormal_count": high_count + low_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching lab results summary: {str(e)}")