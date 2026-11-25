"""Plugin contract for independently executable scan modules."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable

from schsint.core.models import ModuleResult, ScanProgress, ScanRequest

ProgressCallback = Callable[[ScanProgress], Awaitable[None]]


class BaseModule(ABC):
    module_id: str

    @abstractmethod
    async def run(self, request: ScanRequest, progress: ProgressCallback) -> ModuleResult:
        """Run one bounded module and report progress asynchronously."""
