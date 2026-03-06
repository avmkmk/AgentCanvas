"""
AgentRunner — runs a single agent step via LLMService (BC-03).

Coding Standard 1: simple linear flow — no recursion.
Coding Standard 5: errors from llm_service propagate to the caller
(FlowExecutor) which is responsible for catch + recovery.
Coding Standard 9: sanitize_prompt is applied to all user-contributed
content (system_prompt, shared_memory JSON) before the LLM call.
"""
from __future__ import annotations

import json
import logging
from typing import Any

from app.models.agent import Agent
from app.services.llm_service import llm_service
from app.utils.prompt_sanitizer import sanitize_prompt

_log = logging.getLogger(__name__)

# Default model used when agent.model_name is empty / not set
_DEFAULT_MODEL = "claude-haiku-4-5-20251001"


class AgentRunner:
    """Executes a single agent step by calling the LLM.

    Stateless — safe to use as a module-level singleton.
    """

    async def run(
        self,
        agent: Agent,
        shared_memory: dict[str, Any],
        execution_id: str,
        step_number: int,
    ) -> dict[str, Any]:
        """Run *agent* and return an output dict.

        Builds the LLM prompt from shared_memory context plus the agent's
        system_prompt. Both are sanitized before submission (SECURITY.md).

        Args:
            agent: ORM Agent instance containing model_name and system_prompt.
            shared_memory: Current shared memory dict for context injection.
            execution_id: String ID of the parent FlowExecution.
            step_number: 1-based position of this agent in the flow sequence.

        Returns:
            dict with keys: ``output`` (str), ``agent_id`` (str), ``step`` (int).

        Raises:
            LLMTimeoutError: Forwarded from LLMService if all retries time out.
            LLMResponseError: Forwarded from LLMService if response is invalid.
        """
        # Sanitize user-contributed fields before building the LLM prompt
        context_json: str = sanitize_prompt(json.dumps(shared_memory))
        system_prompt: str = sanitize_prompt(agent.system_prompt or "")
        prompt: str = f"Context from previous steps:\n{context_json}"

        model: str = agent.model_name or _DEFAULT_MODEL

        _log.info(
            "AgentRunner.run: step=%d agent_id=%s execution_id=%s model=%s",
            step_number,
            str(agent.id),
            execution_id,
            model,
        )

        output_text: str = await llm_service.complete(
            model=model,
            prompt=prompt,
            system_prompt=system_prompt,
        )

        return {
            "output": output_text,
            "agent_id": str(agent.id),
            "step": step_number,
        }


# Module-level singleton (Coding Standard 4)
agent_runner = AgentRunner()
