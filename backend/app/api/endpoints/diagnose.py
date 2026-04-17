
from fastapi import APIRouter

router = APIRouter()

@router.post("/diagnose", tags=["diagnosis"])
def diagnose_patient(patient_id: int):
    """Placeholder endpoint - use MCP-based LLM endpoint for diagnosis"""
    return {
        "message": "Diagnosis feature moved to MCP-based LLM endpoint",
        "use_instead": "/api/llm/query",
        "example_query": f"diagnose patient {patient_id}"
    }
