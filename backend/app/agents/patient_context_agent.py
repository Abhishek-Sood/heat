from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from ..db.models import Patient, LabResult, Vital, Medication, Report, Alert
from ..core.logging import setup_logging
from ..core.config import get_settings
from groq import Groq
import logging

logger = logging.getLogger("patient_context_agent")
settings = get_settings()

class PatientContextAgent:
    """
    Retrieves comprehensive patient data for clinical decision making.
    """
    
    def __init__(self):
        self.name = "patient_context"
        self.description = "Retrieves patient medical data (labs, vitals, medications, alerts)"
    
    def can_handle(self, query: str, context: Dict[str, Any] = None) -> bool:
        """
        Uses LLM semantic understanding to determine if patient-specific data is needed.
        No keyword matching - analyzes semantic intent for patient information needs.
        """
        try:
            # Always handle if explicit patient_id provided
            if context and context.get('patient_id') is not None:
                return True
                
            if not settings.GROQ_API_KEY:
                # Fallback: assume patient context might be needed
                return True
            
            # Semantic analysis for patient data needs
            analysis_prompt = f"""
Analyze if this medical query requires patient-specific information:

Query: "{query}"

Does this query need:
- Individual patient data (labs, vitals, medical history)
- Specific patient demographics or records
- Personalized medical information
- Patient-specific context for accurate response

Answer: YES (if patient data needed) or NO (if general medical question)

Response:"""

            client = Groq(api_key=settings.GROQ_API_KEY) 
            response = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You are a medical query analyzer. Respond only with YES or NO."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.0,
                max_tokens=10
            )
            
            result = response.choices[0].message.content.strip().upper()
            return "YES" in result
            
        except Exception as e:
            logger.error(f"LLM classification failed for patient context agent: {e}")
            # Safe fallback - include patient context when unsure
            return True
        
        return has_patient_keywords or has_patient_id
    
    def process(self, query: str, context: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """
        Retrieve comprehensive patient context.
        
        Args:
            query: User query
            context: Must contain 'patient_id'
            db: Database session
            
        Returns:
            Dict with patient data and context
        """
        try:
            patient_id = context.get('patient_id')
            user_id = context.get('user_id')  # Get user_id for filtering
            
            if not user_id:
                return {
                    'patient_context': '',
                    'has_context': False,
                    'agent_used': self.name,
                    'error': 'No user_id provided for authentication'
                }
            
            if not patient_id:
                # Try to extract patient ID from query
                import re
                patient_match = re.search(r'patient\s+(\d+)', query.lower())
                if patient_match:
                    patient_id = int(patient_match.group(1))
                else:
                    return {
                        'patient_context': '',
                        'has_context': False,
                        'agent_used': self.name,
                        'error': 'No patient ID found in query or context'
                    }
            
            logger.info(f"Retrieving context for patient {patient_id}")
            
            # Get patient info (filtered by user_id)
            patient = db.query(Patient).filter(
                Patient.id == patient_id,
                Patient.user_id == user_id
            ).first()
            if not patient:
                return {
                    'patient_context': '',
                    'has_context': False,
                    'agent_used': self.name,
                    'error': f'Patient {patient_id} not found or access denied'
                }
            
            context_parts = [f"PATIENT INFORMATION (ID: {patient_id}):"]
            context_parts.append(f"Name: {patient.name}")
            context_parts.append(f"Gender: {patient.gender}")
            context_parts.append(f"Date of Birth: {patient.dob}")
            
            # Get recent lab results (filtered by user_id)
            lab_results = db.query(LabResult).filter(
                LabResult.patient_id == patient_id,
                LabResult.user_id == user_id
            ).order_by(LabResult.timestamp.desc()).limit(10).all()
            if lab_results:
                context_parts.append("\nRECENT LAB RESULTS:")
                for result in lab_results:
                    context_parts.append(f"- {result.test_name}: {result.result} {result.unit} (Ref: {result.reference_range}) [{result.timestamp.strftime('%Y-%m-%d')}]")
            
            # Get recent vitals (filtered by user_id)
            vitals = db.query(Vital).filter(
                Vital.patient_id == patient_id,
                Vital.user_id == user_id
            ).order_by(Vital.timestamp.desc()).limit(5).all()
            if vitals:
                context_parts.append("\nRECENT VITALS:")
                for vital in vitals:
                    context_parts.append(f"- {vital.type}: {vital.value} {vital.unit} [{vital.timestamp.strftime('%Y-%m-%d')}]")
            
            # Get current medications (filtered by user_id)
            medications = db.query(Medication).filter(
                Medication.patient_id == patient_id,
                Medication.user_id == user_id
            ).all()
            if medications:
                context_parts.append("\nCURRENT MEDICATIONS:")
                for med in medications:
                    context_parts.append(f"- {med.name}: {med.dosage}, {med.frequency}")
            
            # Get active alerts (handle potential schema mismatch, filtered by user_id)
            try:
                alerts = db.query(Alert).filter(
                    Alert.patient_id == patient_id,
                    Alert.user_id == user_id,
                    Alert.resolved == False
                ).all()
                if alerts:
                    context_parts.append("\nACTIVE ALERTS:")
                    for alert in alerts:
                        # Handle case where message column might not exist
                        try:
                            alert_text = f"- {alert.severity}: {alert.message}"
                        except AttributeError:
                            alert_text = f"- {alert.severity}: Alert ID {alert.id}"
                        context_parts.append(alert_text)
            except Exception as alert_error:
                logger.warning(f"Could not fetch alerts for patient {patient_id}: {alert_error}")
                # Rollback the transaction to continue with other queries
                db.rollback()

            # Get recent reports (handle potential transaction issues, filtered by user_id)
            try:
                reports = db.query(Report).filter(
                    Report.patient_id == patient_id,
                    Report.user_id == user_id
                ).order_by(Report.created_at.desc()).limit(3).all()
                if reports:
                    context_parts.append("\nRECENT REPORTS:")
                    for report in reports:
                        context_parts.append(f"- {report.content[:200]}... [{report.created_at.strftime('%Y-%m-%d')}]")
            except Exception as report_error:
                logger.warning(f"Could not fetch reports for patient {patient_id}: {report_error}")
                db.rollback()
            patient_context = "\n".join(context_parts)
            
            logger.info(f"Successfully retrieved context for patient {patient_id}")
            
            return {
                'patient_context': patient_context,
                'has_context': True,
                'agent_used': self.name,
                'patient_id': patient_id,
                'message': f'Retrieved comprehensive data for patient {patient_id}'
            }
            
        except Exception as e:
            logger.error(f"Error in patient context agent: {str(e)}")
            return {
                'patient_context': '',
                'has_context': False,
                'agent_used': self.name,
                'error': str(e),
                'patient_id': context.get('patient_id') if context else None
            }