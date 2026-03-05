"""
Global exception handler middleware.

Converts unhandled exceptions to structured JSON responses.
Pydantic ValidationError → 422 with field-level detail.
All other unhandled exceptions → 500 with sanitized message (no stack trace to client).

Coding Standard 5: no silent errors — all exceptions are logged.
Coding Standard 6: one handler, one job — do not mix concerns here.
"""
from __future__ import annotations

import logging
import traceback

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

logger = logging.getLogger(__name__)


def register_error_handlers(app: FastAPI) -> None:
    """Attach all error handlers to the FastAPI app instance."""

    @app.exception_handler(ValidationError)
    async def pydantic_validation_error_handler(
        request: Request, exc: ValidationError
    ) -> JSONResponse:
        # Return structured field errors — useful for API consumers
        logger.warning(
            "Validation error on %s %s: %s",
            request.method,
            request.url.path,
            exc.errors(),
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        # Log full traceback server-side; return generic message to client
        # to avoid information leakage (Security — OWASP A05)
        logger.error(
            "Unhandled exception on %s %s:\n%s",
            request.method,
            request.url.path,
            traceback.format_exc(),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An internal server error occurred."},
        )
