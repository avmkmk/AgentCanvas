"""
Unit tests for app/middleware/error_handler.py — global exception handlers.

Two security/correctness properties are verified:
  1. Pydantic ValidationError → HTTP 422 with structured field-level errors
     (not a generic 500 — API consumers need actionable feedback)
  2. Any other Exception → HTTP 500 with a generic message — the full
     traceback must NOT appear in the response body (prevents information
     disclosure per OWASP A05)

We register the handlers on a minimal FastAPI instance with two routes that
deliberately trigger each error type.
"""
from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, field_validator


# ─── Minimal test app ─────────────────────────────────────────────────────────

def _build_error_test_app() -> FastAPI:
    from app.middleware.error_handler import register_error_handlers

    app = FastAPI()
    register_error_handlers(app)

    class _StrictModel(BaseModel):
        value: int

        @field_validator("value")
        @classmethod
        def must_be_positive(cls, v: int) -> int:
            if v <= 0:
                raise ValueError("value must be positive")
            return v

    @app.get("/trigger-validation-error")
    async def _trigger_validation() -> dict:
        # Raise a Pydantic ValidationError directly to test the handler
        _StrictModel(value=-1)  # This will raise ValidationError
        return {}  # unreachable

    @app.get("/trigger-runtime-error")
    async def _trigger_runtime() -> dict:
        # Simulate an unhandled exception with sensitive detail in its message
        raise RuntimeError(
            "DB password is hunter2 — should never appear in response"
        )

    return app


@pytest.fixture(scope="module")
def error_client() -> TestClient:
    return TestClient(_build_error_test_app(), raise_server_exceptions=False)


# ─── Tests ────────────────────────────────────────────────────────────────────

class TestPydanticValidationErrorHandler:

    def test_validation_error_returns_422(self, error_client: TestClient) -> None:
        response = error_client.get("/trigger-validation-error")
        assert response.status_code == 422

    def test_validation_error_body_contains_detail_key(
        self, error_client: TestClient
    ) -> None:
        response = error_client.get("/trigger-validation-error")
        body = response.json()
        assert "detail" in body

    def test_validation_error_detail_is_list_of_field_errors(
        self, error_client: TestClient
    ) -> None:
        response = error_client.get("/trigger-validation-error")
        detail = response.json()["detail"]
        # Pydantic v2 errors() returns a list of dicts with 'loc', 'msg', 'type'
        assert isinstance(detail, list)
        assert len(detail) > 0
        first_error = detail[0]
        assert "msg" in first_error


class TestUnhandledExceptionHandler:

    def test_runtime_error_returns_500(self, error_client: TestClient) -> None:
        response = error_client.get("/trigger-runtime-error")
        assert response.status_code == 500

    def test_runtime_error_body_contains_generic_message(
        self, error_client: TestClient
    ) -> None:
        response = error_client.get("/trigger-runtime-error")
        body = response.json()
        assert body["detail"] == "An internal server error occurred."

    def test_runtime_error_does_not_expose_exception_message(
        self, error_client: TestClient
    ) -> None:
        """
        Security property: the raw exception message must not reach the caller.
        The route raises RuntimeError with 'hunter2' in the message — that
        string must not appear in the HTTP response.
        """
        response = error_client.get("/trigger-runtime-error")
        body_text = response.text
        assert "hunter2" not in body_text
        assert "RuntimeError" not in body_text

    def test_runtime_error_does_not_expose_traceback(
        self, error_client: TestClient
    ) -> None:
        response = error_client.get("/trigger-runtime-error")
        body_text = response.text
        # Traceback markers that must never reach the client
        assert "Traceback" not in body_text
        assert "File " not in body_text
        assert "line " not in body_text
