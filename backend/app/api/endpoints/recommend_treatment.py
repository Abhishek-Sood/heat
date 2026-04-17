
from fastapi import APIRouter

router = APIRouter()

@router.post("/recommend-treatment", tags=["treatment"])
def recommend_treatment(patient_id: int):
    """Placeholder endpoint - use MCP-based LLM endpoint for treatment recommendations"""
    return {
        "message": "Treatment recommendation feature moved to MCP-based LLM endpoint",
        "use_instead": "/api/llm/query",
        "example_query": f"recommend treatment for patient {patient_id}"
    }
