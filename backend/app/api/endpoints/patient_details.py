from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, validator
from typing import Dict, Any
from datetime import datetime, date
import re
from app.mcp.deps import get_mcp_db, DatabaseMCPClient
from app.core.auth import get_current_user
from app.db.models import User
from app.core.errors import MCPServerDownError

router = APIRouter()

# Helper function to serialize dates to strings
def serialize_dates(obj):
    """Convert date/datetime objects to strings for JSON serialization"""
    if isinstance(obj, dict):
        return {key: serialize_dates(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [serialize_dates(item) for item in obj]
    elif isinstance(obj, (date, datetime)):
        return obj.isoformat()
    else:
        return obj

# Define the schema for patient details
class PatientDetails(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Patient's full name")
    dob: str = Field(..., description="Date of birth in YYYY-MM-DD format")
    gender: str = Field(..., min_length=1, max_length=50, description="Patient's gender")
    contact: str = Field(..., max_length=50, description="Patient's contact information")
    address: str = Field(..., max_length=500, description="Patient's address")
    
    @validator('dob')
    def validate_dob(cls, v):
        """Validate date of birth format"""
        if not v or v.lower() == 'null':
            raise ValueError("Date of birth is required")
            
        # Check if it's just a year (like "2004")
        if re.match(r'^\d{4}$', v.strip()):
            raise ValueError("Date of birth must be in YYYY-MM-DD format, not just year. Example: 2004-01-15")
            
        # Check if it matches YYYY-MM-DD format
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', v.strip()):
            raise ValueError("Date of birth must be in YYYY-MM-DD format. Example: 1990-01-15")
            
        # Try to parse the date to ensure it's valid
        try:
            datetime.strptime(v.strip(), '%Y-%m-%d')
        except ValueError:
            raise ValueError("Invalid date format. Please use YYYY-MM-DD format with valid date values")
            
        return v.strip()
    
    @validator('name')
    def validate_name(cls, v):
        """Validate name is not null or empty"""
        if not v or v.lower() == 'null' or not v.strip():
            raise ValueError("Name is required and cannot be null or empty")
        return v.strip()
        
    @validator('contact')
    def validate_contact(cls, v):
        """Validate contact is not null"""
        if v and v.lower() == 'null':
            return ""  # Convert 'null' string to empty string
        return v or ""

class PatientResponse(BaseModel):
    message: str
    data: Dict[str, Any]

@router.post("/patients/add", status_code=201)
async def add_patient(
    patient: PatientDetails,
    current_user: User = Depends(get_current_user),
    mcp_client: DatabaseMCPClient = Depends(get_mcp_db)
):
    """
    Endpoint to add patient details to the database via MCP server.
    Each doctor can only see and manage their own patients.
    
    Expected date format for dob: YYYY-MM-DD (e.g., 2004-01-15)
    """
    try:
        # Add user_id to patient data to associate with the authenticated doctor
        patient_data = patient.dict()
        patient_data['user_id'] = current_user.id
        
        # Send patient details to MCP server (now async)
        response = await mcp_client.insert_patient(patient_data)

        if response.get("status") != "success":
            error_message = response.get("message", "Unknown database error")
            
            # Provide user-friendly error messages for common issues
            if "invalid input syntax for type date" in error_message:
                raise HTTPException(
                    status_code=400, 
                    detail="Invalid date format for date of birth. Please use YYYY-MM-DD format (e.g., 2004-01-15)"
                )
            elif "duplicate key value" in error_message:
                raise HTTPException(
                    status_code=409,
                    detail="A patient with this information already exists"
                )
            else:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Failed to add patient details: {error_message}"
                )

        return {
            "message": "Patient details added successfully via MCP server.", 
            "data": response.get("data", {})
        }

    except MCPServerDownError as e:
        # MCP Server is down - return 503 Service Unavailable
        raise HTTPException(
            status_code=503,
            detail={
                "error": "database_unavailable",
                "message": "Database connection lost. MCP Server is down.",
                "user_action": "Please log in again or contact support if the issue persists.",
                "technical_details": str(e)
            }
        )
    except HTTPException:
        # Re-raise HTTP exceptions (like validation errors)
        raise
    except Exception as e:
        # Handle any other unexpected errors
        error_msg = str(e)
        if "invalid input syntax for type date" in error_msg:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format for date of birth. Please use YYYY-MM-DD format (e.g., 2004-01-15)"
            )
        raise HTTPException(status_code=500, detail=f"Error adding patient: {error_msg}")

@router.get("/patients/{patient_id}")
async def get_patient(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    mcp_client: DatabaseMCPClient = Depends(get_mcp_db)
):
    """
    Endpoint to get patient details from the database via MCP server.
    Doctors can only access their own patients.
    """
    try:
        patient = await mcp_client.get_patient_by_user(patient_id, current_user.id)
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found or access denied")
        
        # Serialize dates to strings to avoid JSON serialization errors
        serialized_patient = serialize_dates(patient)
        
        return {"message": "Patient retrieved successfully.", "data": serialized_patient}
    
    except MCPServerDownError as e:
        # MCP Server is down - return 503 Service Unavailable
        raise HTTPException(
            status_code=503,
            detail={
                "error": "database_unavailable",
                "message": "Database connection lost. MCP Server is down.",
                "user_action": "Please log in again or contact support if the issue persists.",
                "technical_details": str(e)
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving patient: {str(e)}")

@router.get("/patients/")
async def get_patients(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    mcp_client: DatabaseMCPClient = Depends(get_mcp_db)
):
    """
    Endpoint to get patients from the database via MCP server.
    Each doctor sees only their own patients.
    """
    try:
        patients = await mcp_client.get_patients_by_user(current_user.id, skip=skip, limit=limit)
        
        # Serialize dates to strings to avoid JSON serialization errors
        serialized_patients = serialize_dates(patients)
        
        return {
            "message": f"Retrieved {len(patients)} patients successfully.", 
            "data": serialized_patients,
            "count": len(patients)
        }
    
    except MCPServerDownError as e:
        # MCP Server is down - return 503 Service Unavailable
        raise HTTPException(
            status_code=503,
            detail={
                "error": "database_unavailable",
                "message": "Database connection lost. MCP Server is down.",
                "user_action": "Please log in again or contact support if the issue persists.",
                "technical_details": str(e)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving patients: {str(e)}")