import PyPDF2
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session
import io
import logging

from app.db.models import Patient, LabResult, Vital, Medication, Report

logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self, db_session: Session):
        self.db = db_session
        
    async def process_lab_results_pdf(
        self, 
        file_content: bytes, 
        patient_id: int, 
        user_id: int,
        filename: str
    ) -> List[Dict[str, Any]]:
        """
        Process lab results PDF with table format.
        """
        text_content = self._extract_text_from_pdf(file_content)
        return await self._process_lab_results_table(text_content, patient_id, user_id, filename)
    
    def _extract_text_from_pdf(self, file_content: bytes) -> str:
        """
        Extract text content from PDF bytes.
        """
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
                
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise Exception(f"Failed to extract text from PDF: {e}")
    
    async def _process_lab_results_table(
        self, 
        text: str, 
        patient_id: int, 
        user_id: int,
        filename: str
    ) -> List[Dict[str, Any]]:
        """
        Extract and save lab results from table format text.
        Simple parsing - just extract test names and values.
        """
        lab_results = []
        
        # Debug: log the extracted text
        logger.info(f"Processing text: {text[:500]}...")
        
        # Simple patterns to extract common lab values
        patterns = {
            'Platelets': r'platelets\s+(\d+\.?\d*)\s*cells/mcl',
            'Hemoglobin': r'hemoglobin\s+(\d+\.?\d*)\s*g/dl',
            'WBC': r'wbc\s+(\d+\.?\d*)\s*cells/mcl',
            'Cholesterol': r'cholesterol\s+(\d+\.?\d*)\s*mg/dl',
            'Glucose': r'glucose\s+(\d+\.?\d*)\s*mg/dl'
        }
        
        text_lower = text.lower()
        
        for test_name, pattern in patterns.items():
            matches = re.findall(pattern, text_lower)
            for match in matches:
                # Create lab result entry
                lab_result = LabResult(
                    patient_id=patient_id,
                    user_id=user_id,
                    timestamp=datetime.now(),
                    test_name=test_name,
                    result=str(match),
                    unit=self._get_unit_for_test(test_name),
                    reference_range=self._get_reference_range(test_name)
                )
                self.db.add(lab_result)
                
                lab_results.append({
                    "test_name": test_name,
                    "result": str(match),
                    "unit": self._get_unit_for_test(test_name),
                    "reference_range": self._get_reference_range(test_name),
                    "timestamp": datetime.now().isoformat()
                })
        
        # Also store the complete report
        report = Report(
            patient_id=patient_id,
            user_id=user_id,
            content=text,
            created_at=datetime.now()
        )
        self.db.add(report)
        
        self.db.commit()
        return lab_results
    
    def _get_unit_for_test(self, test_name: str) -> str:
        """Get unit for test name."""
        units = {
            'Platelets': 'cells/mcL',
            'Hemoglobin': 'g/dL',
            'WBC': 'cells/mcL',
            'Cholesterol': 'mg/dL',
            'Glucose': 'mg/dL'
        }
        return units.get(test_name, '')
    
    def _get_reference_range(self, test_name: str) -> str:
        """Get reference range for test name."""
        ranges = {
            'Platelets': '150000-450000',
            'Hemoglobin': '12-16',
            'WBC': '4000-11000',
            'Cholesterol': '<200',
            'Glucose': '70-100'
        }
        return ranges.get(test_name, '')