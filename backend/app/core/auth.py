from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.mcp.deps import get_mcp_db, DatabaseMCPClient
import jwt
from app.core.config import settings

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    mcp_client: DatabaseMCPClient = Depends(get_mcp_db)
):
    """
    Dependency to get the current authenticated user from JWT token via MCP
    """
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    # Get user via MCP instead of direct database access
    user = await mcp_client.get_user_by_id(int(user_id))
    if user is None or not user.get("is_active"):
        raise credentials_exception
    
    # Convert to a simple object for compatibility
    class User:
        def __init__(self, data):
            self.id = data["id"]
            self.username = data["username"] 
            self.email = data["email"]
            self.is_active = data["is_active"]
            self.medical_license_id = data.get("medical_license_id")
    
    return User(user)