from fastapi import APIRouter
from fastapi.responses import JSONResponse
import psutil
import os

router = APIRouter()

def check_mcp_server_status():
    """Check if MCP DB server process is running"""
    # If SKIP_MCP_CHECK is set, assume it's running
    if os.environ.get('SKIP_MCP_CHECK', '').lower() in ('true', '1', 'yes'):
        return "enabled (check skipped)"
    
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if isinstance(cmdline, list):
                    cmdline_str = ' '.join(cmdline)
                    if 'app.mcp.db_server' in cmdline_str or 'db_server' in cmdline_str:
                        return "running"
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return "not running"
    except Exception as e:
        return f"check failed: {str(e)}"

@router.get("/health", tags=["health"])
def health_check():
    mcp_status = check_mcp_server_status()
    return {
        "status": "ok",
        "mcp_server": mcp_status
    }

@router.get("/openai.json", include_in_schema=False)
async def openai_manifest():
    manifest = {
        "schema_version": "v1",
        "name_for_human": "GenAI Clinical Assistant",
        "name_for_model": "genai_clinical_assistant",
        "description_for_human": "Access clinical assistant features.",
        "description_for_model": "Provides clinical assistant endpoints for patient data, diagnosis, and recommendations.",
        "auth": {"type": "none"},
        "api": {"type": "openapi", "url": "/openapi.json"},
        "logo_url": "/static/logo.png",
        "contact_email": "support@example.com",
        "legal_info_url": "https://example.com/legal"
    }
    return JSONResponse(content=manifest)
