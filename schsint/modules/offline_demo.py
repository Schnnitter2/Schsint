"""Offline-only safe demonstration module; performs no network requests."""

from schsint.core.models import ModuleResult, ModuleStatus, ScanProgress, ScanRequest
from schsint.modules.base import BaseModule, ProgressCallback


class OfflineDemoModule(BaseModule):
    module_id = "offline-demo"

    async def run(self, request: ScanRequest, progress: ProgressCallback) -> ModuleResult:
        del request  # No target data is transmitted or used by the demo module.
        await progress(
            ScanProgress(
                scan_id="pending",
                active_module=self.module_id,
                status="running",
                message="Offline demo: no public sources are queried.",
            )
        )
        return ModuleResult(module=self.module_id, status=ModuleStatus.SKIPPED)
