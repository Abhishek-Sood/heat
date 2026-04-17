
from fastapi import APIRouter

router = APIRouter()

@router.post("/query-sql", tags=["sql"])
def query_sql(nl_query: str):
    """Placeholder endpoint - use MCP-based LLM endpoint for SQL queries"""
    return {
        "message": "SQL query feature moved to MCP-based LLM endpoint",
        "use_instead": "/api/llm/query",
        "your_query": nl_query,
        "example": "POST /api/llm/query with JSON: {\"query\": \"your natural language query\"}"
    }
