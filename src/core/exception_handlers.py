from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from src.exceptions.base import AppError


def add_exception_handlers(app):
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "message": exc.message,
                    "code": exc.status_code,
                    "method": request.method,
                    "path": str(request.url),
                }
            }
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "message": exc.detail,
                    "code": exc.status_code,
                    "method": request.method,
                    "path": str(request.url),
                }
            }
        )
