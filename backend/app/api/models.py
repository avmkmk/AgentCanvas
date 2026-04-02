"""
Models router — exposes the list of LLM deployment names available on the
EPAM AI Dial proxy.

This endpoint is public (no X-API-Key required) so the frontend can
populate the model picker without an extra auth step.

Coding Standard 6: one router, one job — model discovery only.
Coding Standard 8: delegates to llm_service.list_models(); no SDK calls here.
"""


import logging

from fastapi import APIRouter

from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["models"])


@router.get(
    "/api/v1/models",
    summary="List available LLM models",
    description=(
        "Returns the deployment names available on the configured LLM proxy. "
        "The list is fetched from the proxy once and cached for the lifetime "
        "of the process. If the proxy is unreachable, the configured default "
        "model is returned as a single-item fallback."
    ),
    response_model=list[str],
)
async def list_models() -> list[str]:
    """Return available model deployment names from the Dial proxy.

    No authentication required — this is a discovery endpoint used by
    the frontend model picker. The actual LLM calls are still auth-gated.
    """
    models: list[str] = await llm_service.list_models()
    logger.debug("Models endpoint returning %d model(s)", len(models))
    return models
