"""Centralized error handlers for FastAPI application.

Provides a function to register structured exception handlers for domain
exceptions and HTTPException to ensure NFR-004: meaningful error messages.
"""

import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_422_UNPROCESSABLE_ENTITY,
)

from .errors import ResumeUploadError, ResumeParsingError

LOG = logging.getLogger(__name__)


def register_error_handlers(app: FastAPI) -> None:
    """Attach exception handlers to the FastAPI app.

    Handlers produce structured JSON: {"error": <message>, "detail": <detail>}
    """

    @app.exception_handler(ResumeUploadError)
    async def upload_error_handler(request: Request, exc: ResumeUploadError):
        LOG.warning(
            "ResumeUploadError: %s - %s", exc.message, getattr(exc, "detail", None)
        )
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={"error": exc.message, "detail": exc.detail},
        )

    @app.exception_handler(ResumeParsingError)
    async def parsing_error_handler(request: Request, exc: ResumeParsingError):
        LOG.warning(
            "ResumeParsingError: %s - %s", exc.message, getattr(exc, "detail", None)
        )
        return JSONResponse(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": exc.message, "detail": exc.detail},
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        # Ensure HTTPException details are returned in a consistent structure
        detail = exc.detail if hasattr(exc, "detail") else str(exc)
        LOG.info("HTTPException: %s %s", exc.status_code, detail)
        # For backward compatibility include both 'error' and 'detail'
        return JSONResponse(
            status_code=exc.status_code or 500,
            content={"error": detail, "detail": detail},
        )
