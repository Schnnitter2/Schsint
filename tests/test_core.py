from __future__ import annotations

import pytest
from pydantic import ValidationError

from schsint.core.engine import CoreEngine
from schsint.core.models import Finding, ModuleResult, ModuleStatus, ScanProgress, ScanRequest
from schsint.modules.base import BaseModule, ProgressCallback
from schsint.modules.offline_demo import OfflineDemoModule
from schsint.reports import ReportGenerator


class TestModule(BaseModule):
    def __init__(self, module_id: str, url: str, fail: bool = False) -> None:
        self.module_id, self.url, self.fail = module_id, url, fail

    async def run(self, request: ScanRequest, progress: ProgressCallback) -> ModuleResult:
        if self.fail:
            raise RuntimeError("expected failure")
        return ModuleResult(
            module=self.module_id,
            status=ModuleStatus.COMPLETED,
            checked_sources=1,
            findings=(Finding(source="Example", url=self.url, module=self.module_id, status="public_match"),),
        )


@pytest.fixture
def request() -> ScanRequest:
    return ScanRequest(username="sample_user", consent_confirmed=True)


@pytest.mark.asyncio
async def test_offline_demo_has_no_findings_or_network(request: ScanRequest) -> None:
    report = await CoreEngine([OfflineDemoModule()]).run(request)
    assert report.modules[0].status is ModuleStatus.SKIPPED
    assert report.findings == ()


@pytest.mark.asyncio
async def test_failure_is_isolated_and_urls_deduplicated(request: ScanRequest) -> None:
    engine = CoreEngine([
        TestModule("first", "https://EXAMPLE.test/profile#top"),
        TestModule("broken", "https://example.test/other", fail=True),
        TestModule("second", "https://example.test/profile"),
    ])
    report = await engine.run(request)
    assert [item.status for item in report.modules] == [ModuleStatus.COMPLETED, ModuleStatus.FAILED, ModuleStatus.COMPLETED]
    assert len(report.findings) == 1
    assert report.duplicate_count == 1


@pytest.mark.asyncio
async def test_progress_callback_and_scan_id(request: ScanRequest) -> None:
    events: list[ScanProgress] = []

    async def collect(event: ScanProgress) -> None:
        events.append(event)

    await CoreEngine([OfflineDemoModule()]).run(request, collect)
    assert {event.status for event in events} >= {"started", "skipped"}
    assert len({event.scan_id for event in events}) == 1


def test_consent_required_and_username_validated() -> None:
    with pytest.raises(ValidationError):
        ScanRequest(username="abc", consent_confirmed=False)
    with pytest.raises(ValidationError):
        ScanRequest(username="bad input", consent_confirmed=True)


def test_report_is_self_contained_and_escapes_username() -> None:
    report = CoreEngine([])
    import asyncio
    result = asyncio.run(report.run(ScanRequest(username="safe_name", consent_confirmed=True)))
    html = ReportGenerator().render_html(result)
    assert "Schsint" in html
    assert "cdn." not in html
    assert "does not establish identity" in html


def test_all_languages_have_help_text() -> None:
    from schsint.i18n import get_text
    for code in ("en", "es", "de", "ru"):
        assert get_text(code, "help")
