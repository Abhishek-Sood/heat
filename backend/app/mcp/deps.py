"""
MCP-based dependency injection for FastAPI endpoints
"""

from fastapi import Depends
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from app.mcp.client import DatabaseMCPClient
from app.db.database import SessionLocal

def get_db_session():
    """Dependency to get database session for direct DB access (used for auth)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_mcp_db() -> DatabaseMCPClient:
    """Dependency to get MCP database client"""
    client = DatabaseMCPClient()
    await client.connect()
    return client

# MCP-based data access functions
async def get_mcp_patient(patient_id: int, mcp_client: DatabaseMCPClient = Depends(get_mcp_db)) -> Optional[Dict[str, Any]]:
    """Get patient using MCP client"""
    return await mcp_client.get_patient(patient_id)

async def get_mcp_patients(skip: int = 0, limit: int = 100, mcp_client: DatabaseMCPClient = Depends(get_mcp_db)) -> List[Dict[str, Any]]:
    """Get patients using MCP client"""
    return await mcp_client.get_patients(skip=skip, limit=limit)

async def get_mcp_patient_vitals(patient_id: int, mcp_client: DatabaseMCPClient = Depends(get_mcp_db)) -> List[Dict[str, Any]]:
    """Get patient vitals using MCP client"""
    return await mcp_client.get_patient_vitals(patient_id)