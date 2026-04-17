"""
Test script to verify patient context agent is fetching lab results correctly
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.database import SessionLocal
from app.db.models import Patient, LabResult, Vital, Medication, Alert, Report
from app.agents.patient_context_agent import PatientContextAgent
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

def test_patient_context_agent():
    """Test if patient context agent can fetch data"""
    
    db = SessionLocal()
    agent = PatientContextAgent()
    
    try:
        # Check what patients exist
        patients = db.query(Patient).all()
        print(f"🔍 Found {len(patients)} patients in database")
        
        for patient in patients[:3]:  # Show first 3 patients
            print(f"  - Patient {patient.id}: {patient.name}")
        
        # Check lab results for patient 2
        lab_results = db.query(LabResult).filter(LabResult.patient_id == 2).all()
        print(f"🧪 Found {len(lab_results)} lab results for patient 2")
        
        for result in lab_results[:3]:  # Show first 3 results
            print(f"  - {result.test_name}: {result.result} {result.unit}")
        
        # Test the agent with patient 2
        print("\n🤖 Testing Patient Context Agent...")
        context = {'patient_id': 2}
        query = "should i recommend aspirin to patient 2"
        
        result = agent.process(query, context, db)
        
        print(f"✅ Agent result:")
        print(f"  - Has context: {result.get('has_context')}")
        print(f"  - Patient ID: {result.get('patient_id')}")
        print(f"  - Error: {result.get('error')}")
        
        if result.get('has_context'):
            print("\n📋 Patient Context Retrieved:")
            print(result.get('patient_context', '')[:500] + "...")
        else:
            print(f"❌ No context retrieved: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error testing patient context: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_patient_context_agent()