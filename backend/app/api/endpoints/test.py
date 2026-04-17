"""
Simple test endpoint to verify the system is working
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/test/simple", tags=["test"])
async def simple_test():
    """
    Simple test endpoint that doesn't depend on any external services
    Use this to verify FastAPI is working
    """
    return {
        "status": "success",
        "message": "FastAPI backend is running successfully",
        "endpoints_available": [
            "GET /api/test/simple - This simple test",
            "GET /api/llm/test - Test LLM endpoint with MCP",
            "GET /api/mcp/test - Test MCP connection",
            "GET /api/mcp/patients - List patients via MCP",
            "POST /api/llm/query - Interactive LLM queries"
        ]
    }

@router.get("/test/health", tags=["test"])
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "GenAI Clinical Assistant",
        "version": "1.0.0"
    }