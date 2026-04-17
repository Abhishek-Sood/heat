
from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter()

@router.get("/alerts/{patient_id}", tags=["alerts"])
def get_alerts(patient_id: int) -> List[Dict[str, Any]]:
    """Placeholder endpoint - use MCP-based endpoints for alerts"""
    return [
        {
            "message": "Alerts feature moved to MCP-based endpoints",
            "use_instead": "/api/mcp/patients or /api/llm/query",
            "patient_id": patient_id
        }
    ]
