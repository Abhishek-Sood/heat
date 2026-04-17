"""
LLM endpoint with Groq integration and database schema context
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import json
from groq import Groq

from app.core.config import get_settings
from app.core.auth import get_current_user
from app.db.database import get_database
from app.db.models import User, Patient, LabResult, Vital, Medication, Report, Alert, Conversation, Message
from app.agents.langgraph_orchestrator import get_orchestrator

router = APIRouter()
settings = get_settings()

# Add Groq API key to settings if not already there
# You'll need to add GROQ_API_KEY to your .env file



class LLMQuery(BaseModel):
    query: str
    patient_id: Optional[int] = None

class LLMResponse(BaseModel):
    response: str
    patient_id: Optional[int] = None
    source: str = "groq"
    agents_used: Optional[List[str]] = []
    query_categories: Optional[List[str]] = []
    has_research_context: Optional[bool] = False

def get_database_schema() -> str:
    """
    Generate database schema context for the LLM.
    """
    schema_context = """
    MEDICAL DATABASE SCHEMA:
    
    Table: patients
    - id (integer, primary key)
    - name (string)
    - dob (date)
    - gender (string)  
    - contact (string)
    - address (string)
    - created_at (datetime)
    - updated_at (datetime)
    
    Table: lab_results
    - id (integer, primary key)
    - patient_id (integer, foreign key to patients.id)
    - timestamp (datetime)
    - test_name (string)
    - result (string)
    - unit (string)
    - reference_range (string)
    
    Table: vitals
    - id (integer, primary key)
    - patient_id (integer, foreign key to patients.id)
    - timestamp (datetime)
    - type (string) - e.g., "Blood Pressure", "Heart Rate", "Temperature"
    - value (float)
    - unit (string)
    
    Table: medications
    - id (integer, primary key)
    - patient_id (integer, foreign key to patients.id)
    - name (string)
    - dosage (string)
    - frequency (string)
    - start_date (date)
    - end_date (date)
    
    Table: reports
    - id (integer, primary key)
    - patient_id (integer, foreign key to patients.id)
    - content (text)
    - created_at (datetime)
    
    Table: alerts
    - id (integer, primary key)
    - patient_id (integer, foreign key to patients.id)
    - message (string)
    - severity (string)
    - created_at (datetime)
    - resolved (boolean)
    
    Table: conversations
    - id (integer, primary key)
    - patient_id (integer, foreign key to patients.id)
    - title (string)
    - created_at (datetime)
    
    Table: messages
    - id (integer, primary key)
    - conversation_id (integer, foreign key to conversations.id)
    - role (string)
    - content (text)
    - timestamp (datetime)
    """
    return schema_context

def get_patient_context(db: Session, patient_id: int, user_id: int) -> str:
    """
    Get patient-specific data as context when patient_id is provided.
    Filtered by user_id for multi-tenancy.
    """
    try:
        # Get patient info (filtered by user_id)
        patient = db.query(Patient).filter(
            Patient.id == patient_id, 
            Patient.user_id == user_id
        ).first()
        if not patient:
            return f"No patient found with ID {patient_id} or access denied."
        
        context_parts = [f"PATIENT INFORMATION (ID: {patient_id}):"]
        context_parts.append(f"Name: {patient.name}")
        context_parts.append(f"Gender: {patient.gender}")
        context_parts.append(f"Date of Birth: {patient.dob}")
        
        # Get lab results (filtered by user_id)
        lab_results = db.query(LabResult).filter(
            LabResult.patient_id == patient_id,
            LabResult.user_id == user_id
        ).order_by(LabResult.timestamp.desc()).limit(10).all()
        if lab_results:
            context_parts.append("\nRECENT LAB RESULTS:")
            for result in lab_results:
                context_parts.append(f"- {result.test_name}: {result.result} {result.unit} (Ref: {result.reference_range}) [{result.timestamp.strftime('%Y-%m-%d')}]")
        
        # Get vitals (filtered by user_id)
        vitals = db.query(Vital).filter(
            Vital.patient_id == patient_id,
            Vital.user_id == user_id
        ).order_by(Vital.timestamp.desc()).limit(5).all()
        if vitals:
            context_parts.append("\nRECENT VITALS:")
            for vital in vitals:
                context_parts.append(f"- {vital.type}: {vital.value} {vital.unit} [{vital.timestamp.strftime('%Y-%m-%d')}]")
        
        # Get medications (filtered by user_id)
        medications = db.query(Medication).filter(
            Medication.patient_id == patient_id,
            Medication.user_id == user_id
        ).all()
        if medications:
            context_parts.append("\nCURRENT MEDICATIONS:")
            for med in medications:
                context_parts.append(f"- {med.name}: {med.dosage}, {med.frequency}")
        
        return "\n".join(context_parts)
    
    except Exception as e:
        return f"Error retrieving patient data: {str(e)}"




STRICT_MEDICAL_PROMPT = """
You are a clinical AI assistant integrated with a healthcare database.

Your task is to generate responses ONLY based on the data retrieved from the database.

STRICT RULES:

1. SOURCE OF TRUTH:
- Use ONLY the provided database context.
- Do NOT use prior knowledge.
- Do NOT assume or infer missing values.

2. MISSING DATA:
- If required data is missing, respond EXACTLY:
"Relevant data not present in the database."

3. NO HALLUCINATION:
- Do NOT generate information not explicitly present.
- Do NOT interpret or analyze beyond given data.

4. NO MEDICAL ADVICE:
- Do NOT provide diagnosis, treatment, or recommendations.

5. DOMAIN RESTRICTION:
- If query is outside database/medical scope:
"Query outside the supported medical domain."

6. IGNORE EMOTIONAL INPUT:
- Do NOT respond to emotional or casual conversation.

7. OUTPUT FORMAT:
- Return structured factual data and explanation ONLY based on database context.
- DO NOT include any SQL queries, markdown tables, or technical formatting in the response.
- Speak naturally as if talking to a doctor or patient, but only using actual data from the database.
- No extra text.

You will be given:
- Database schema
- Patient data (if available)
- Doctor query

Return ONLY grounded response from database.
"""










async def query_groq_llm(prompt: str) -> str:
    """
    Query the Groq LLM using the official Groq client.
    """
    try:
        if not settings.GROQ_API_KEY:
            return "Please configure GROQ_API_KEY in your environment variables to enable AI responses."
            
        # Initialize Groq client
        client = Groq(api_key=settings.GROQ_API_KEY)
        
        # Create completion using Groq
        completion = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {
                    "role": "system", 
                    "content": STRICT_MEDICAL_PROMPT
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            max_tokens=1200,
            temperature=0.0
        )
        
        return completion.choices[0].message.content
        
    except Exception as e:
        # Fallback for development/testing  
        return f"Medical AI Response: I can analyze the provided medical data context. However, there was an issue connecting to the AI service: {str(e)}. Please check your Groq API configuration."

@router.post("/llm/query", response_model=LLMResponse, tags=["llm"])
async def llm_query(
    query_request: LLMQuery,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
) -> LLMResponse:
    """
    Query the LLM with database schema context and optional patient data.
    Uses intelligent agent dispatch to only call RAG when needed (reduces latency).
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"🔍 LLM Endpoint Called:")
    logger.info(f"  📝 Query: {query_request.query}")
    logger.info(f"  🆔 Patient ID: {query_request.patient_id}")
    logger.info(f"  👤 User: {current_user.id} ({current_user.email})")
    logger.info(f"  ⏰ Timestamp: {json.dumps({'timestamp': str(current_user.id)}, default=str)}")
    
    try:
        # Initialize LangGraph orchestrator with LLM semantic classification
        logger.info("🤖 Initializing LangGraph orchestrator...")
        orchestrator = get_orchestrator()
        
        # Prepare context for dispatch
        context = {
            'patient_id': query_request.patient_id,
            'user_id': current_user.id  # Add user context for multi-tenancy
        }
        logger.info(f"📋 Dispatch context: {context}")
        
        # Dispatch query to appropriate agent(s) with database access and user context
        logger.info("🚀 Dispatching to semantic routing system...")
        dispatch_result = orchestrator.dispatch(
            query_request.query, 
            context,
            db  # Pass database session for patient context agent
        )
        
        logger.info(f"✅ Dispatch completed:")
        logger.info(f"  📄 Response: {dispatch_result.get('natural_response', 'No response')[:100]}...")
        logger.info(f"  🤖 Agents used: {dispatch_result.get('agents_used', [])}")
        logger.info(f"  🏷️ Categories: {dispatch_result.get('categories', [])}")
        logger.info(f"  🎯 Route decision: {dispatch_result.get('route_decision', 'none')}")
        logger.info(f"  ❌ Error: {dispatch_result.get('error', 'None')}")
        
        # The orchestrator already returns a fully formatted natural response
        # No need to build prompts or call Groq again
        
        response = LLMResponse(
            response=dispatch_result.get('natural_response', 'No response generated'),
            patient_id=dispatch_result.get('patient_id') or query_request.patient_id,
            source="langgraph_orchestrated",
            agents_used=dispatch_result.get('agents_used', []),
            query_categories=dispatch_result.get('categories', []),
            has_research_context='pubmed_rag' in dispatch_result.get('agents_used', [])
        )
        
        logger.info(f"📤 Final API response: agents={response.agents_used}, categories={response.query_categories}")
        return response
        
    except Exception as e:
        logger.error(f"❌ LLM Endpoint Error: {str(e)}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        
        raise HTTPException(
            status_code=500,
            detail=f"LLM query failed: {str(e)}"
        )