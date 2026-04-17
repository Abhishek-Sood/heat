"""
Test endpoint without authentication to verify orchestrator fixes
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from app.agents.langgraph_orchestrator import get_orchestrator

router = APIRouter()

class TestQuery(BaseModel):
    query: str
    patient_id: Optional[int] = None
    user_id: int = 1

class TestResponse(BaseModel):
    response: str
    agents_used: List[str]
    categories: List[str]
    has_sql_context: bool
    error: Optional[str] = None

@router.post("/test/orchestrator", response_model=TestResponse, tags=["test"])
async def test_orchestrator_no_auth(request: TestQuery) -> TestResponse:
    """
    Test orchestrator endpoint without authentication for debugging
    """
    try:
        orchestrator = get_orchestrator()
        
        context = {
            'patient_id': request.patient_id,
            'user_id': request.user_id
        }
        
        result = orchestrator.dispatch(request.query, context, db=None)
        
        return TestResponse(
            response=result.get('natural_response', 'No response generated'),
            agents_used=result.get('agents_used', []),
            categories=result.get('categories', []),
            has_sql_context=result.get('has_sql_context', False),
            error=result.get('error')
        )
        
    except Exception as e:
        return TestResponse(
            response=f"Error: {str(e)}",
            agents_used=[],
            categories=[],
            has_sql_context=False,
            error=str(e)
        )