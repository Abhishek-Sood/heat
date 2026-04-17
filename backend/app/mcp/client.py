"""
MCP Client for FastAPI Backend - Simple approach that requires MCP Server to be running
Handles database operations by checking MCP server availability first, then using shared DB functions
"""

import asyncio
import json
import logging
import subprocess
import psutil
import os
import sys
import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, DateTime
from app.core.errors import MCPServerDownError

logger = logging.getLogger(__name__)

from app.core.config import get_settings
settings = get_settings()

class DatabaseMCPClient:
    """
    MCP Client that ensures MCP DB Server is running before allowing database operations
    Simple approach: Check MCP server is running, then use shared database functions
    """
    
    def __init__(self):
        self.engine = create_engine(settings.DATABASE_URL)
        self.metadata = MetaData()
        self._setup_tables()
        self._is_connected = False
        
    def _setup_tables(self):
        """Setup table schemas"""
        self.patients_table = Table(
            "patients",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(255)),
            Column("dob", String(10)),
            Column("gender", String(50)),
            Column("contact", String(50)),
            Column("address", String(500)),
            Column("user_id", Integer),
            Column("created_at", DateTime),
            Column("updated_at", DateTime),
        )
        
    def _is_mcp_server_running(self) -> bool:
        """Check if MCP DB server process is running"""
        # In production/container environments, check for SKIP_MCP_CHECK env var
        if os.environ.get('SKIP_MCP_CHECK', '').lower() in ('true', '1', 'yes'):
            return True
            
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info.get('cmdline', [])
                    if isinstance(cmdline, list):
                        cmdline_str = ' '.join(cmdline)
                        # Check for various ways MCP server might be running
                        if 'app.mcp.db_server' in cmdline_str or 'db_server' in cmdline_str:
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # If server process not found, reset connection state
            if self._is_connected:
                logger.warning("🔥 MCP server process not found - resetting connection state")
                self._is_connected = False
            return False
        except Exception as e:
            logger.error(f"Error checking MCP server: {e}")
            # On error, assume server is down and reset connection
            if self._is_connected:
                logger.warning("🔥 MCP server check failed - resetting connection state")
                self._is_connected = False
            return False
    
    async def connect(self):
        """Check MCP Server is running before allowing database operations"""
        if not self._is_mcp_server_running():
            raise Exception("❌ MCP DB Server not running. Please start it with: python -m app.mcp.db_server")
        
        try:
            # Test database connection
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            self._is_connected = True
            logger.info("✅ MCP Client ready - MCP DB Server is running")
        except Exception as e:
            raise Exception(f"❌ Database connection failed: {str(e)}")
    
    async def disconnect(self):
        """Disconnect"""
        self._is_connected = False
        logger.info("MCP Client disconnected")

    def _ensure_mcp_server_running(self):
        """Ensure MCP server is running before database operations with health check"""
        # First check if process is running (this also resets connection state if needed)
        if not self._is_mcp_server_running():
            raise MCPServerDownError("MCP Database Server is not running. All database operations are blocked. Please restart the MCP server or contact support.")
        
        # If we think we're connected but server check passed, verify database connectivity
        if self._is_connected:
            try:
                with self.engine.connect() as connection:
                    connection.execute(text("SELECT 1"))
                # Connection is healthy
                return
            except Exception as e:
                logger.warning(f"🔥 Database connection test failed: {e} - resetting connection state")
                self._is_connected = False
                raise MCPServerDownError(f"MCP Database connection is unhealthy: {e}. Please check the MCP server.")
        else:
            # Not connected, try to reconnect
            try:
                with self.engine.connect() as connection:
                    connection.execute(text("SELECT 1"))
                self._is_connected = True
                logger.info("✅ MCP connection restored")
            except Exception as e:
                raise MCPServerDownError(f"Cannot establish MCP Database connection: {e}. Please restart the MCP server.")

    # Database operation methods - require MCP server to be running
    async def get_patient(self, patient_id: int, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Get patient by ID - requires MCP server running"""
        self._ensure_mcp_server_running()
        
        try:
            with self.engine.connect() as connection:
                query = self.patients_table.select().where(self.patients_table.c.id == patient_id)
                
                if user_id is not None:
                    query = query.where(self.patients_table.c.user_id == user_id)
                
                result = connection.execute(query)
                row = result.fetchone()
                
                if row:
                    patient_data = dict(row._mapping)
                    # Convert datetime objects to strings
                    for key, value in patient_data.items():
                        if isinstance(value, datetime.datetime):
                            patient_data[key] = value.isoformat()
                        elif isinstance(value, datetime.date):
                            patient_data[key] = value.isoformat()
                    return patient_data
                return None
        except Exception as e:
            logger.error(f"Error getting patient: {e}")
            raise e

    async def get_patients(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get list of patients - requires MCP server running"""
        self._ensure_mcp_server_running()
        
        try:
            with self.engine.connect() as connection:
                query = self.patients_table.select().offset(skip).limit(limit)
                result = connection.execute(query)
                rows = result.fetchall()
                
                patients = []
                for row in rows:
                    patient_data = dict(row._mapping)
                    # Convert datetime objects to strings
                    for key, value in patient_data.items():
                        if isinstance(value, datetime.datetime):
                            patient_data[key] = value.isoformat()
                        elif isinstance(value, datetime.date):
                            patient_data[key] = value.isoformat()
                    patients.append(patient_data)
                
                return patients
        except Exception as e:
            logger.error(f"Error getting patients: {e}")
            raise e

    async def get_patients_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get patients by user ID - requires MCP server running"""
        self._ensure_mcp_server_running()
        
        try:
            with self.engine.connect() as connection:
                query = (self.patients_table.select()
                        .where(self.patients_table.c.user_id == user_id)
                        .offset(skip)
                        .limit(limit))
                result = connection.execute(query)
                rows = result.fetchall()
                
                patients = []
                for row in rows:
                    patient_data = dict(row._mapping)
                    # Convert datetime objects to strings
                    for key, value in patient_data.items():
                        if isinstance(value, datetime.datetime):
                            patient_data[key] = value.isoformat()
                        elif isinstance(value, datetime.date):
                            patient_data[key] = value.isoformat()
                    patients.append(patient_data)
                
                return patients
        except Exception as e:
            logger.error(f"Error getting patients by user: {e}")
            raise e

    async def get_patient_by_user(self, patient_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Get single patient by ID filtered by user ID - requires MCP server running"""
        self._ensure_mcp_server_running()
        
        try:
            with self.engine.connect() as connection:
                query = (self.patients_table.select()
                        .where(self.patients_table.c.id == patient_id)
                        .where(self.patients_table.c.user_id == user_id))
                result = connection.execute(query)
                row = result.fetchone()
                
                if row:
                    patient_data = dict(row._mapping)
                    # Convert datetime objects to strings
                    for key, value in patient_data.items():
                        if isinstance(value, datetime.datetime):
                            patient_data[key] = value.isoformat()
                        elif isinstance(value, datetime.date):
                            patient_data[key] = value.isoformat()
                    return patient_data
                return None
        except Exception as e:
            logger.error(f"Error getting patient by user: {e}")
            raise e

    async def insert_patient(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert patient - requires MCP server running"""
        self._ensure_mcp_server_running()
        
        try:
            now = datetime.datetime.utcnow()
            patient_data['created_at'] = now
            patient_data['updated_at'] = now
            
            with self.engine.connect() as connection:
                trans = connection.begin()
                try:
                    insert_query = self.patients_table.insert().values(**patient_data)
                    result = connection.execute(insert_query)
                    patient_id = result.inserted_primary_key[0]
                    trans.commit()
                    
                    return {
                        "status": "success",
                        "data": {
                            "id": patient_id,
                            "name": patient_data.get("name"),
                            "dob": patient_data.get("dob"),
                            "gender": patient_data.get("gender"),
                            "contact": patient_data.get("contact"),
                            "address": patient_data.get("address"),
                            "created_at": patient_data.get("created_at").isoformat(),
                            "updated_at": patient_data.get("updated_at").isoformat()
                        }
                    }
                except Exception as e:
                    trans.rollback()
                    raise e
        except Exception as e:
            logger.error(f"Error inserting patient: {e}")
            raise e

    async def get_patient_vitals(self, patient_id: int) -> List[Dict[str, Any]]:
        """Get patient vitals - requires MCP server running"""
        self._ensure_mcp_server_running()
        
        # Placeholder implementation
        return []

    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute SQL query - requires MCP server running"""
        self._ensure_mcp_server_running()
        
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query), params or {})
                
                if result.returns_rows:
                    rows = []
                    for row in result:
                        row_dict = dict(row._mapping)
                        # Convert datetime objects to strings
                        for key, value in row_dict.items():
                            if isinstance(value, datetime.datetime):
                                row_dict[key] = value.isoformat()
                            elif isinstance(value, datetime.date):
                                row_dict[key] = value.isoformat()
                        rows.append(row_dict)
                    
                    return {
                        "query": query,
                        "params": params,
                        "results": rows
                    }
                else:
                    return {
                        "query": query,
                        "params": params,
                        "message": "Query executed successfully",
                        "rows_affected": result.rowcount
                    }
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise e

    # User management methods for authentication
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create user - requires MCP server running"""
        self._ensure_mcp_server_running()
        
        try:
            with self.engine.begin() as conn:
                query = text("""
                    INSERT INTO users (username, email, password_hash, medical_license_id, is_active, created_at, updated_at)
                    VALUES (:username, :email, :password_hash, :medical_license_id, :is_active, :created_at, :updated_at)
                    RETURNING id
                """)
                
                now = datetime.datetime.now()
                result = conn.execute(query, {
                    "username": user_data["username"],
                    "email": user_data["email"],
                    "password_hash": user_data["password_hash"],
                    "medical_license_id": user_data.get("medical_license_id"),
                    "is_active": True,
                    "created_at": now,
                    "updated_at": now
                })
                
                user_id = result.fetchone()[0]
                
                return {
                    "status": "success",
                    "user_id": user_id,
                    "message": "User created successfully"
                }
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return {
                "status": "error", 
                "message": str(e)
            }

    async def get_user_by_credentials(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by credentials - requires MCP server running"""
        self._ensure_mcp_server_running()
        
        try:
            with self.engine.begin() as conn:
                query = text("""
                    SELECT id, username, email, password_hash, medical_license_id, is_active, created_at, updated_at
                    FROM users 
                    WHERE username = :username OR email = :username
                    LIMIT 1
                """)
                
                result = conn.execute(query, {"username": username})
                user = result.fetchone()
                
                if user:
                    user_data = dict(user._mapping)
                    # Convert datetime objects to strings
                    for key, value in user_data.items():
                        if isinstance(value, datetime.datetime):
                            user_data[key] = value.isoformat()
                    return user_data
                return None
        except Exception as e:
            logger.error(f"Error getting user by credentials: {e}")
            raise e

    async def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID - requires MCP server running"""
        self._ensure_mcp_server_running()
        
        try:
            with self.engine.begin() as conn:
                query = text("""
                    SELECT id, username, email, medical_license_id, is_active, created_at, updated_at
                    FROM users 
                    WHERE id = :user_id
                """)
                
                result = conn.execute(query, {"user_id": user_id})
                user = result.fetchone()
                
                if user:
                    user_data = dict(user._mapping)
                    # Convert datetime objects to strings
                    for key, value in user_data.items():
                        if isinstance(value, datetime.datetime):
                            user_data[key] = value.isoformat()
                    return user_data
                return None
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            raise e

    async def check_user_exists(self, username: str, email: str) -> bool:
        """Check if user exists - requires MCP server running"""
        self._ensure_mcp_server_running()
        
        try:
            with self.engine.begin() as conn:
                query = text("""
                    SELECT id FROM users 
                    WHERE username = :username OR email = :email
                    LIMIT 1
                """)
                
                result = conn.execute(query, {"username": username, "email": email})
                existing_user = result.fetchone()
                
                return existing_user is not None
        except Exception as e:
            logger.error(f"Error checking user exists: {e}")
            raise e

# Global MCP client instance (singleton)
_mcp_client = None

async def get_mcp_client() -> DatabaseMCPClient:
    """Get or create the global MCP client instance with health checking"""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = DatabaseMCPClient()
    
    # Always check server health first (this will reset _is_connected if server is down)
    if not _mcp_client._is_mcp_server_running():
        raise Exception("❌ MCP DB Server not running. Please start it with: python -m app.mcp.db_server")
    
    # Now check if we need to connect/reconnect
    if not _mcp_client._is_connected:
        await _mcp_client.connect()
    
    return _mcp_client

async def cleanup_mcp_client():
    """Cleanup the global MCP client"""
    global _mcp_client
    if _mcp_client is not None:
        await _mcp_client.disconnect()
        _mcp_client = None

async def force_mcp_client_refresh():
    """Force refresh the MCP client connection state"""
    global _mcp_client
    if _mcp_client is not None:
        # Reset connection state to force fresh health check
        _mcp_client._is_connected = False
        logger.info("🔄 Forced MCP client refresh - connection state reset")
    return await get_mcp_client()

