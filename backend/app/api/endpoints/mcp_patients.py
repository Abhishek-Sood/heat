"""
MCP-based patient endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any

from app.mcp.deps import get_mcp_db, DatabaseMCPClient
from app.core.auth import get_current_user
from app.db.models import User

router = APIRouter()

@router.get("/mcp/patient/{patient_id}", tags=["mcp-patients"])
async def get_patient_mcp(
    patient_id: int, 
    current_user: User = Depends(get_current_user),
    mcp_client: DatabaseMCPClient = Depends(get_mcp_db)
) -> Dict[str, Any]:
    """Get patient information using MCP - with user authentication"""
    patient = await mcp_client.get_patient_by_user(patient_id, current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found or access denied")
    return patient

# @router.get("/mcp/patients", tags=["mcp-patients"])
# async def get_patients_mcp(skip: int = 0, limit: int = 100, mcp_client: DatabaseMCPClient = Depends(get_mcp_db)) -> List[Dict[str, Any]]:
#     """Get patients list using MCP"""
#     return await mcp_client.get_patients(skip=skip, limit=limit)

# @router.get("/mcp/patient/{patient_id}/vitals", tags=["mcp-patients"])
# async def get_patient_vitals_mcp(patient_id: int, mcp_client: DatabaseMCPClient = Depends(get_mcp_db)) -> List[Dict[str, Any]]:
#     """Get patient vitals using MCP"""
#     return await mcp_client.get_patient_vitals(patient_id)

# @router.get("/mcp/test", tags=["mcp-test"])
# async def test_mcp_connection(mcp_client: DatabaseMCPClient = Depends(get_mcp_db)) -> Dict[str, Any]:
#     """Simple test endpoint to verify MCP connection is working"""
#     try:
#         # Try to get first patient to test connection
#         patients = await mcp_client.get_patients(skip=0, limit=100)
#         return {
#             "status": "success",
#             "message": "MCP connection is working",
#             "patients_found": len(patients),
#             "mcp_connected": True
#         }
#     except Exception as e:
#         return {
#             "status": "error", 
#             "message": f"MCP connection failed: {str(e)}",
#             "mcp_connected": False
#         }