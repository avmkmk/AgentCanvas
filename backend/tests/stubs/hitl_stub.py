"""
Stub for HITLManager (BC-06).

Models the expected state-machine behaviour of HITLReview:
  pending → approved
  pending → rejected
  approved → (no further transitions allowed)
  rejected → (no further transitions allowed)

Coding Standard 3: explicit Literal type for status — no magic strings.
Coding Standard 5: invalid transitions raise ValueError with a clear message.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

# Valid status values mirror the DB CHECK constraint
HITLStatus = Literal["pending", "approved", "rejected"]


@dataclass
class HITLReview:
    """Represents a single HITL review gate in a flow execution."""

    id: str
    status: HITLStatus = "pending"

    def approve(self) -> None:
        """
        Transition status from pending → approved.

        Raises ValueError if the review is not in the 'pending' state.
        A non-pending review cannot be approved — this prevents double-action
        bugs where an operator clicks Approve twice.
        """
        if self.status != "pending":
            raise ValueError(
                f"Cannot approve review with status '{self.status}'. "
                "Only 'pending' reviews can be approved."
            )
        self.status = "approved"

    def reject(self) -> None:
        """
        Transition status from pending → rejected.

        Raises ValueError if the review is not in the 'pending' state.
        """
        if self.status != "pending":
            raise ValueError(
                f"Cannot reject review with status '{self.status}'. "
                "Only 'pending' reviews can be rejected."
            )
        self.status = "rejected"


class HITLManagerStub:
    """Minimal stub matching the expected HITLManager interface."""

    async def create_review(self, execution_id: str) -> HITLReview:
        """Create a new HITL review in 'pending' status."""
        return HITLReview(id=f"review-{execution_id}")
