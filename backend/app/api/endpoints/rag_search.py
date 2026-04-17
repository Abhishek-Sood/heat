from fastapi import APIRouter, Depends
from app.core.auth import get_current_user
from app.db.models import User
from ...rag.retriever import retrieve_medical_knowledge

router = APIRouter()

@router.post("/rag-search", tags=["rag"])
def rag_search(
    query: str, 
    current_user: User = Depends(get_current_user)
):
    """RAG search endpoint - requires authentication"""
    return retrieve_medical_knowledge(query)
