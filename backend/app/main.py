from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.logging import setup_logging
import os

from app.api.endpoints import (
    health, diagnose, recommend_treatment,
    query_sql, rag_search, alerts, chat, mcp_patients, llm, test, patient_details, file_upload, auth, lab_results, simple_test, test_orchestrator
)
from app.mcp.client import cleanup_mcp_client

setup_logging()
settings = get_settings()

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# CORS origins - include Render URLs and local development
cors_origins = [
    "http://localhost:3000", 
    "http://localhost:3001",
    "http://localhost:5173",  # Vite default
]

# Add Render frontend URL if available (for production)
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    if not frontend_url.startswith("http"):
        frontend_url = f"https://{frontend_url}"
    cors_origins.append(frontend_url)

# Add CORS middleware to allow frontend requests
# Using allow_origin_regex to match all Render subdomains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now (can restrict later)
    allow_origin_regex=r"https://.*\.onrender\.com",  # Regex for all Render subdomains
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Routers
app.include_router(health.router, prefix=settings.API_PREFIX)
# Register health router again at root for /openai.json
app.include_router(health.router)
app.include_router(diagnose.router, prefix=settings.API_PREFIX)
app.include_router(recommend_treatment.router, prefix=settings.API_PREFIX)
app.include_router(query_sql.router, prefix=settings.API_PREFIX)
app.include_router(rag_search.router, prefix=settings.API_PREFIX)
# app.include_router(alerts.router, prefix=settings.API_PREFIX)
app.include_router(chat.router, prefix=settings.API_PREFIX)

# New MCP-based endpoints
app.include_router(mcp_patients.router, prefix=settings.API_PREFIX)
app.include_router(llm.router, prefix=settings.API_PREFIX)
app.include_router(test.router, prefix=settings.API_PREFIX)
app.include_router(test_orchestrator.router, prefix=settings.API_PREFIX)

# Include the new router for patient details
app.include_router(patient_details.router, prefix="/api")

# Include the new router for file uploads
app.include_router(file_upload.router, prefix="/api")

# Include auth endpoints
app.include_router(auth.router)

# Include lab results endpoints
app.include_router(lab_results.router, prefix="/api")

# Include simple test endpoints
app.include_router(simple_test.router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    # DB connections, agents, pipelines can be initialized here
    # MCP client will be initialized on first use
    pass

@app.on_event("shutdown")
async def shutdown_event():
    # Cleanup MCP client connection
    await cleanup_mcp_client()