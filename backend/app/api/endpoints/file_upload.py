from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
import io

from app.db.models import Base, User, Patient
from app.core.config import get_settings
from app.core.auth import get_current_user
from app.services.pdf_processor import PDFProcessor
from app.mcp.deps import get_db_session

router = APIRouter()
settings = get_settings()

@router.post("/upload-lab-results/")
async def upload_lab_results(
    patient_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Upload and process lab results PDF specifically.
    Only allows doctors to upload files for their own patients.
    """
    
    # Verify the patient belongs to the current user
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.user_id == current_user.id
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found or access denied"
        )
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400, 
            detail="Only PDF files are supported"
        )
    
    try:
        file_content = await file.read()
        pdf_processor = PDFProcessor(db)
        
        result = await pdf_processor.process_lab_results_pdf(
            file_content=file_content,
            patient_id=patient_id,
            user_id=current_user.id,
            filename=file.filename
        )
        
        return {
            "message": "Lab results processed successfully",
            "filename": file.filename,
            "patient_id": patient_id,
            "lab_results_added": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing lab results: {str(e)}"
        )