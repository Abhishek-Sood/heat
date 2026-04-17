from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Optional
import jwt
import hashlib
from pydantic import BaseModel, EmailStr

from app.mcp.deps import get_mcp_db
from app.mcp.client import DatabaseMCPClient
from app.core.config import get_settings
from app.core.errors import MCPServerDownError

router = APIRouter(tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
settings = get_settings()

# JWT Configuration from settings
JWT_SECRET = settings.SECRET_KEY
JWT_ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS

# Pydantic models
class UserSignup(BaseModel):
    username: str
    email: EmailStr
    password: str
    medical_license_id: Optional[str] = None

class UserLogin(BaseModel):
    identifier: str  # Can be username or email
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    refresh_token: str

def hash_password(password: str) -> str:
    """Simple password hashing - in production use bcrypt"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

@router.post("/auth/signup", response_model=dict)
async def signup(user_data: UserSignup, mcp_client: DatabaseMCPClient = Depends(get_mcp_db)):
    """User registration endpoint"""
    try:
        # Check if username or email already exists using MCP
        user_exists = await mcp_client.check_user_exists(user_data.username, user_data.email)
        
        if user_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )
        
        # Hash password
        password_hash = hash_password(user_data.password)
        
        # Create user via MCP
        user_creation_data = {
            "username": user_data.username,
            "email": user_data.email,
            "password_hash": password_hash,
            "medical_license_id": user_data.medical_license_id
        }
        
        result = await mcp_client.create_user(user_creation_data)
        
        if result["status"] == "success":
            return {"message": "User created successfully", "user_id": result["user_id"]}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Registration failed: {result.get('message', 'Unknown error')}"
            )
        
    except MCPServerDownError as e:
        # MCP Server is down - return 503 Service Unavailable
        raise HTTPException(
            status_code=503,
            detail={
                "error": "database_unavailable",
                "message": "Registration service temporarily unavailable. Database server is down.",
                "user_action": "Please try again later or contact support if the issue persists.",
                "technical_details": str(e)
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin, mcp_client: DatabaseMCPClient = Depends(get_mcp_db)):
    """User login endpoint"""
    try:
        # Find user by username or email using MCP
        user = await mcp_client.get_user_by_credentials(user_data.identifier)
        
        if not user or not user.get("is_active") or not verify_password(user_data.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Create tokens
        token_data = {"sub": str(user["id"]), "username": user["username"], "email": user["email"]}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        
    except MCPServerDownError as e:
        # MCP Server is down - return 503 Service Unavailable
        raise HTTPException(
            status_code=503,
            detail={
                "error": "database_unavailable",
                "message": "Login service temporarily unavailable. Database server is down.",
                "user_action": "Please try again in a few moments or contact support if the issue persists.",
                "technical_details": str(e)
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/auth/refresh", response_model=Token)
async def refresh_token(token_data: TokenRefresh, mcp_client: DatabaseMCPClient = Depends(get_mcp_db)):
    """Refresh access token"""
    try:
        # Decode refresh token
        payload = jwt.decode(token_data.refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        # Get user data from token
        user_id = payload.get("sub")
        username = payload.get("username")
        email = payload.get("email")
        
        # Verify user still exists and is active using MCP
        user = await mcp_client.get_user_by_id(int(user_id))
        
        if not user or not user.get("is_active"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new tokens
        token_data = {"sub": user_id, "username": username, "email": email}
        new_access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )