from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import RequestValidationError
from fastapi.exceptions import HTTPException
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

class MCPServerDownError(Exception):
    """Raised when MCP DB Server is not running"""
    def __init__(self, message: str = "MCP Database Server is not running. Please contact support."):
        self.message = message
        super().__init__(self.message)

async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )
