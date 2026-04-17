"""
MCP Server for Database Operations - STANDALONE SERVER
This server acts as the ONLY database connection point for the FastAPI backend
NO OTHER PART OF THE APPLICATION SHOULD CONNECT DIRECTLY TO THE DATABASE
"""

import asyncio
import json
import logging
import sys
import os
import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection settings from environment
from app.core.config import get_settings
settings = get_settings()
DATABASE_URL = settings.DATABASE_URL

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    ListToolsResult,  
    Tool,
    TextContent,
)
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, DateTime
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

class DatabaseMCPServer:
    """
    MCP Server that handles ALL database operations
    This is the ONLY component that should connect directly to the database
    """
    
    def __init__(self):
        self.server = Server("database-mcp-server")
        
        # Initialize database connection (ONLY place with direct DB access)
        self.engine = create_engine(DATABASE_URL)
        self.metadata = MetaData()
        
        # Define patients table schema
        self.patients_table = Table(
            "patients",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(255)),
            Column("dob", String(10)),  # Date of birth as string (YYYY-MM-DD format)
            Column("gender", String(50)),
            Column("contact", String(50)),
            Column("address", String(500)),
            Column("user_id", Integer),  # Doctor/user who owns this patient
            Column("created_at", DateTime),
            Column("updated_at", DateTime),
        )
        
        # Test database connection on startup
        self._test_connection()
        
        # Register MCP tools
        self._register_tools()
    
    def _test_connection(self):
        """Test database connection on server startup"""
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            logger.info("MCP Server: Database connection established successfully")
        except Exception as e:
            logger.error(f"MCP Server: Failed to connect to database: {str(e)}")
            raise e
    
    def _register_tools(self):
        """Register MCP tools for database operations"""
        
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            return ListToolsResult(
                tools=[
                    Tool(
                        name="insert_patient",
                        description="Insert a new patient into the database",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Patient name"},
                                "dob": {"type": "string", "description": "Date of birth (YYYY-MM-DD)"},
                                "gender": {"type": "string", "description": "Patient gender"},
                                "contact": {"type": "string", "description": "Contact information"},
                                "address": {"type": "string", "description": "Patient address"},
                                "user_id": {"type": "integer", "description": "ID of the doctor/user who owns this patient"}
                            },
                            "required": ["name", "dob", "gender", "contact", "address", "user_id"]
                        }
                    ),
                    Tool(
                        name="get_patient",
                        description="Get patient information by ID",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "patient_id": {"type": "integer", "description": "Patient ID"},
                                "user_id": {"type": "integer", "description": "User ID for access control (optional)"}
                            },
                            "required": ["patient_id"]
                        }
                    ),
                    Tool(
                        name="get_patients_by_user",
                        description="Get list of patients filtered by user ID with pagination",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "integer", "description": "User ID to filter patients"},
                                "skip": {"type": "integer", "description": "Records to skip", "default": 0},
                                "limit": {"type": "integer", "description": "Max records to return", "default": 100}
                            },
                            "required": ["user_id"]
                        }
                    ),
                    Tool(
                        name="get_patients",
                        description="Get list of patients with pagination",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "skip": {"type": "integer", "description": "Records to skip", "default": 0},
                                "limit": {"type": "integer", "description": "Max records to return", "default": 100}
                            }
                        }
                    ),
                    Tool(
                        name="get_patient_vitals", 
                        description="Get patient vitals by patient ID",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "patient_id": {"type": "integer", "description": "Patient ID"}
                            },
                            "required": ["patient_id"]
                        }
                    ),
                    Tool(
                        name="execute_query",
                        description="Execute a custom SQL query",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "SQL query to execute"},
                                "params": {"type": "object", "description": "Query parameters"}
                            },
                            "required": ["query"]
                        }
                    ),
                    Tool(
                        name="create_user",
                        description="Create a new user (signup)",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "username": {"type": "string", "description": "Username"},
                                "email": {"type": "string", "description": "Email address"},
                                "password_hash": {"type": "string", "description": "Hashed password"},
                                "medical_license_id": {"type": "string", "description": "Medical license ID (optional)"}
                            },
                            "required": ["username", "email", "password_hash"]
                        }
                    ),
                    Tool(
                        name="get_user_by_credentials",
                        description="Get user by username/email for authentication",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "username": {"type": "string", "description": "Username or email"}
                            },
                            "required": ["username"]
                        }
                    ),
                    Tool(
                        name="get_user_by_id",
                        description="Get user information by user ID",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "integer", "description": "User ID"}
                            },
                            "required": ["user_id"]
                        }
                    ),
                    Tool(
                        name="check_user_exists",
                        description="Check if username or email already exists",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "username": {"type": "string", "description": "Username"},
                                "email": {"type": "string", "description": "Email address"}
                            },
                            "required": ["username", "email"]
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle MCP tool calls"""
            try:
                if name == "insert_patient":
                    return await self._insert_patient(arguments)
                elif name == "get_patient":
                    patient_id = arguments["patient_id"]
                    user_id = arguments.get("user_id")  # Optional for backwards compatibility
                    return await self._get_patient(patient_id, user_id)
                elif name == "get_patients_by_user":
                    return await self._get_patients_by_user(
                        arguments["user_id"],
                        arguments.get("skip", 0),
                        arguments.get("limit", 100)
                    )
                elif name == "get_patients":
                    return await self._get_patients(
                        arguments.get("skip", 0),
                        arguments.get("limit", 100)
                    )
                elif name == "get_patient_vitals":
                    return await self._get_patient_vitals(arguments["patient_id"])
                elif name == "execute_query":
                    return await self._execute_query(
                        arguments["query"],
                        arguments.get("params", {})
                    )
                elif name == "create_user":
                    return await self._create_user(arguments)
                elif name == "get_user_by_credentials":
                    return await self._get_user_by_credentials(arguments["username"])
                elif name == "get_user_by_id":
                    return await self._get_user_by_id(arguments["user_id"])
                elif name == "check_user_exists":
                    return await self._check_user_exists(arguments["username"], arguments["email"])
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]
                    )
            except Exception as e:
                logger.error(f"MCP Server error in tool {name}: {str(e)}")
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps({"error": str(e)}))]
                )
    
    async def _insert_patient(self, patient_data: Dict[str, Any]) -> CallToolResult:
        """Insert patient data into the database"""
        try:
            # Add timestamps
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
                    
                    logger.info(f"MCP Server: Patient inserted with ID: {patient_id}")
                    
                    response_data = {
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
                    
                    return CallToolResult(
                        content=[TextContent(type="text", text=json.dumps(response_data))]
                    )
                except Exception as e:
                    trans.rollback()
                    raise e
                    
        except Exception as e:
            logger.error(f"MCP Server: Error inserting patient: {str(e)}")
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({"status": "error", "message": str(e)}))]
            )
    
    async def _get_patient(self, patient_id: int, user_id: Optional[int] = None) -> CallToolResult:
        """Get patient by ID from database, with optional user filtering for multi-tenancy"""
        try:
            with self.engine.connect() as connection:
                query = self.patients_table.select().where(self.patients_table.c.id == patient_id)
                
                # Add user filter if user_id is provided (for multi-tenancy)
                if user_id is not None:
                    query = query.where(self.patients_table.c.user_id == user_id)
                
                result = connection.execute(query)
                row = result.fetchone()
                
                if row:
                    patient_data = dict(row._mapping)
                    # Convert datetime and date objects to strings for JSON serialization
                    for key, value in patient_data.items():
                        if isinstance(value, datetime.datetime):
                            patient_data[key] = value.isoformat()
                        elif isinstance(value, datetime.date):
                            patient_data[key] = value.isoformat()
                        
                    return CallToolResult(
                        content=[TextContent(type="text", text=json.dumps(patient_data))]
                    )
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=json.dumps(None))]
                    )
                    
        except Exception as e:
            logger.error(f"MCP Server: Error getting patient {patient_id}: {str(e)}")
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({"error": str(e)}))]
            )
    
    async def _get_patients(self, skip: int, limit: int) -> CallToolResult:
        """Get list of patients from database"""
        try:
            with self.engine.connect() as connection:
                query = self.patients_table.select().offset(skip).limit(limit)
                result = connection.execute(query)
                rows = result.fetchall()
                
                patients = []
                for row in rows:
                    patient_data = dict(row._mapping)
                    # Convert datetime and date objects to strings for JSON serialization
                    for key, value in patient_data.items():
                        if isinstance(value, datetime.datetime):
                            patient_data[key] = value.isoformat()
                        elif isinstance(value, datetime.date):
                            patient_data[key] = value.isoformat()
                    patients.append(patient_data)
                
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps(patients))]
                )
                
        except Exception as e:
            logger.error(f"MCP Server: Error getting patients: {str(e)}")
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({"error": str(e)}))]
            )

    async def _get_patients_by_user(self, user_id: int, skip: int, limit: int) -> CallToolResult:
        """Get list of patients filtered by user ID (multi-tenancy)"""
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
                    # Convert datetime and date objects to strings for JSON serialization
                    for key, value in patient_data.items():
                        if isinstance(value, datetime.datetime):
                            patient_data[key] = value.isoformat()
                        elif isinstance(value, datetime.date):
                            patient_data[key] = value.isoformat()
                    patients.append(patient_data)
                
                logger.info(f"MCP Server: Retrieved {len(patients)} patients for user {user_id}")
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps(patients))]
                )
                
        except Exception as e:
            logger.error(f"MCP Server: Error getting patients for user {user_id}: {str(e)}")
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({"error": str(e)}))]
            )
    
    async def _get_patient_vitals(self, patient_id: int) -> CallToolResult:
        """Get patient vitals from database (placeholder - implement based on your vitals table)"""
        try:
            # Placeholder implementation - you can extend this based on your vitals table structure
            logger.info(f"MCP Server: Getting vitals for patient {patient_id} (placeholder)")
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps([]))]
            )
            
        except Exception as e:
            logger.error(f"MCP Server: Error getting vitals for patient {patient_id}: {str(e)}")
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({"error": str(e)}))]
            )
    
    async def _execute_query(self, query: str, params: Dict[str, Any]) -> CallToolResult:
        """Execute custom SQL query on database"""
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query), params)
                
                if result.returns_rows:
                    rows = []
                    for row in result:
                        row_dict = dict(row._mapping)
                        # Convert datetime and date objects to strings for JSON serialization
                        for key, value in row_dict.items():
                            if isinstance(value, datetime.datetime):
                                row_dict[key] = value.isoformat()
                            elif isinstance(value, datetime.date):
                                row_dict[key] = value.isoformat()
                        rows.append(row_dict)
                    
                    response = {
                        "query": query,
                        "params": params,
                        "results": rows
                    }
                else:
                    response = {
                        "query": query,
                        "params": params,
                        "message": "Query executed successfully",
                        "rows_affected": result.rowcount
                    }
                
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps(response))]
                )
                
        except Exception as e:
            logger.error(f"MCP Server: Error executing query: {str(e)}")
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({"error": str(e)}))]
            )
    
    async def _create_user(self, user_data: Dict[str, Any]) -> CallToolResult:
        """Create a new user (signup)"""
        try:
            with self.engine.begin() as conn:
                # Insert new user
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
                
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps({
                        "status": "success",
                        "user_id": user_id,
                        "message": "User created successfully"
                    }))]
                )
                
        except Exception as e:
            logger.error(f"MCP Server: Error creating user: {str(e)}")
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({
                    "status": "error", 
                    "message": str(e)
                }))]
            )
    
    async def _get_user_by_credentials(self, username: str) -> CallToolResult:
        """Get user by username or email for authentication"""
        try:
            with self.engine.begin() as conn:
                # Get user by username or email
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
                    
                    return CallToolResult(
                        content=[TextContent(type="text", text=json.dumps({
                            "status": "success",
                            "user": user_data
                        }))]
                    )
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=json.dumps({
                            "status": "not_found",
                            "message": "User not found"
                        }))]
                    )
                
        except Exception as e:
            logger.error(f"MCP Server: Error getting user by credentials: {str(e)}")
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({
                    "status": "error",
                    "message": str(e)
                }))]
            )
    
    async def _get_user_by_id(self, user_id: int) -> CallToolResult:
        """Get user information by user ID"""
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
                    
                    return CallToolResult(
                        content=[TextContent(type="text", text=json.dumps({
                            "status": "success",
                            "user": user_data
                        }))]
                    )
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=json.dumps({
                            "status": "not_found",
                            "message": "User not found"
                        }))]
                    )
                
        except Exception as e:
            logger.error(f"MCP Server: Error getting user by ID: {str(e)}")
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({
                    "status": "error",
                    "message": str(e)
                }))]
            )
    
    async def _check_user_exists(self, username: str, email: str) -> CallToolResult:
        """Check if username or email already exists"""
        try:
            with self.engine.begin() as conn:
                query = text("""
                    SELECT id FROM users 
                    WHERE username = :username OR email = :email
                    LIMIT 1
                """)
                
                result = conn.execute(query, {"username": username, "email": email})
                existing_user = result.fetchone()
                
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps({
                        "exists": existing_user is not None
                    }))]
                )
                
        except Exception as e:
            logger.error(f"MCP Server: Error checking user exists: {str(e)}")
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({
                    "status": "error",
                    "message": str(e)
                }))]
            )
    
    async def run(self):
        """Run the MCP server using stdio"""
        logger.info("Starting MCP Database Server...")
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream, 
                write_stream, 
                initialization_options={}
            )

# Entry point for running the MCP server
async def main():
    """Main entry point for the MCP server"""
    try:
        db_server = DatabaseMCPServer()
        await db_server.run()
    except Exception as e:
        import traceback
        logger.error(f"Failed to start MCP server: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())