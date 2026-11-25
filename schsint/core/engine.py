"""Bounded asynchronous orchestration, progress, failure isolation and deduplication."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from urllib.parse import urlsplit, urlunsplit
from uuid import uuid4

from schsint.core.models import (
    Finding,
    ModuleResult,
    ModuleStatus,
    ScanProgress,
    ScanReport,
    ScanRequest,
)
from schsint.modules.base import BaseModule, ProgressCallback

logger = logging.getLogger(__name__)


class CoreEngine:
    def __init__(
        self,
        modules: tuple[BaseModule, ...] | list[BaseModule],
        *,
        max_concurrent_scans: int = 2,
        max_parallel_modules: int = 4,
    ) -> None:
        if max_concurrent_scans < 1 or max_parallel_modules < 1:
            raise ValueError("concurrency limits must be positive")
        ids = [module.module_id for module in modules]
        if len(set(ids)) != len(ids):
            raise ValueError("module_id values must be unique")
        self._modules = tuple(modules)
        self._scan_slots = asyncio.Semaphore(max_concurrent_scans)
        self._module_slots = asyncio.Semaphore(max_parallel_modules)

    async def run(
        self,
        request: ScanRequest,
        progress_callback: ProgressCallback | None = None,
    ) -> ScanReport:
        async with self._scan_slots:
            scan_id = str(uuid4())
            started_at = datetime.now(timezone.utc)
            processed_sources = 0

            async def emit(event: ScanProgress) -> None:
                if progress_callback is not None:
                    try:
                        await progress_callback(event)
                    except Exception:
                        logger.exception("Progress callback failed")

            async def run_one(module: BaseModule) -> ModuleResult:
                nonlocal processed_sources

                async def module_progress(event: ScanProgress) -> None:
                    await emit(event.model_copy(update={"scan_id": scan_id}))

                await emit(ScanProgress(
                    scan_id=scan_id,
                    active_module=module.module_id,
                    total_sources=len(self._modules),
                    status="started",
                    message="Module started.",
                ))
                try:
                    async with self._module_slots:
                        result = await module.run(request, module_progress)
                    if result.module != module.module_id:
                        raise ValueError("module result ID does not match registered module")
                except asyncio.CancelledError:
                    raise
                except Exception as exc:
                    logger.exception("Module %s failed", module.module_id)
                    result = ModuleResult(
                        module=module.module_id,
                        status=ModuleStatus.FAILED,
                        error=f"{type(exc).__name__}: {exc}"[:500],
                    )
                processed_sources += result.checked_sources
                await emit(ScanProgress(
                    scan_id=scan_id,
                    active_module=module.module_id,
                    processed_sources=processed_sources,
                    total_sources=len(self._modules),
                    status=result.status.value,
                    message=result.error or "Module finished.",
                ))
                return result

            results = await asyncio.gather(*(run_one(module) for module in self._modules))
            findings, duplicates = self._deduplicate(
                finding for result in results for finding in result.findings
            )
            return ScanReport(
                scan_id=scan_id,
                username=request.username,
                started_at=started_at,
                completed_at=datetime.now(timezone.utc),
                modules=tuple(results),
                findings=tuple(findings),
                duplicate_count=duplicates,
            )

    @staticmethod
    def _deduplicate(findings: object) -> tuple[list[Finding], int]:
        unique: list[Finding] = []
        seen: set[tuple[str, str]] = set()
        duplicates = 0
        for finding in findings:  # type: ignore[union-attr]
            parts = urlsplit(finding.url)
            canonical = urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path, parts.query, ""))
            key = canonical, finding.status.casefold()
            if key in seen:
                duplicates += 1
            else:
                seen.add(key)
                unique.append(finding)
        return unique, duplicates
