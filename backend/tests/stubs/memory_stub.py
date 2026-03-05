"""
Stub for MemoryService (BC-04).

Provides an in-memory dict-backed implementation of the expected
MemoryService interface.  Used by unit tests that need read/write
isolation semantics without a real Redis or MongoDB connection.

Coding Standard 2: state is always initialised in __init__; no lazy init.
Coding Standard 3: explicit type annotations throughout.
"""
from __future__ import annotations


class MemoryServiceStub:
    """
    In-memory stub for MemoryService.

    Stores flow memory keyed by flow_id.  Each flow has an independent
    namespace — writes to one flow_id must not affect another.
    """

    def __init__(self) -> None:
        # Initialised at construction so there is never an uninitialised-read
        self._store: dict[str, dict[str, object]] = {}

    async def read(self, flow_id: str) -> dict[str, object]:
        """
        Return the stored memory for flow_id.

        Returns an empty dict (not None) when flow_id has no stored memory,
        which matches the expected real-service contract — callers must not
        have to guard against None.
        """
        return self._store.get(flow_id, {})

    async def write(self, flow_id: str, data: dict[str, object]) -> None:
        """
        Write data for flow_id, overwriting any previously stored value.

        The overwrite semantics match the real MemoryService: a full
        snapshot is stored, not a merge.
        """
        self._store[flow_id] = data
