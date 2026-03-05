"""
Prompt injection sanitizer — SECURITY.md §Prompt Injection Prevention.

Called by AgentService.create_agent and update_agent before persisting
system_prompt values. Must also be called by AgentRunner before any LLM call
(M3 — tracked in LLM-01).

Coding Standard 6: one function, one job.
Coding Standard 10: static patterns, version-controlled — not dynamically built.
"""
from __future__ import annotations

import re

# Known prompt injection patterns.
# Order matters for readability — more specific patterns first.
# Patterns are compiled once at module load (Coding Standard 2 — no re-creation).
_INJECTION_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(p, re.IGNORECASE)
    for p in [
        r"ignore (all |previous )?instructions",
        r"you are now",
        r"disregard (your|the) (previous|above)",
        # Negated lookahead: allow "act as a professional" / "act as a helpful…"
        r"act as (a |an )?(?!helpful|professional)",
        r"forget everything",
        r"system override",
    ]
)

_REPLACEMENT: str = "[REMOVED]"


def sanitize_prompt(text: str) -> str:
    """
    Remove known prompt-injection patterns from *text*.

    Returns the sanitized string. The original *text* is never mutated.
    Each matching substring is replaced with "[REMOVED]".

    Args:
        text: Raw user-provided text, e.g. a system prompt from the API.

    Returns:
        Sanitized text safe for storage and later LLM use.
    """
    sanitized: str = text
    for pattern in _INJECTION_PATTERNS:
        sanitized = pattern.sub(_REPLACEMENT, sanitized)
    return sanitized
