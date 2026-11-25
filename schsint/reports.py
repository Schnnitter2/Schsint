"""Self-contained, escaped HTML and JSON report exports."""

from __future__ import annotations

import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from schsint.core.models import ScanReport


class ReportGenerator:
    def __init__(self, template_dir: Path | None = None) -> None:
        root = template_dir or Path(__file__).parent / "templates"
        self.environment = Environment(
            loader=FileSystemLoader(root),
            autoescape=select_autoescape(("html", "xml")),
        )

    def render_html(self, report: ScanReport, language: str = "en") -> str:
        template = self.environment.get_template("report.html")
        return template.render(report=report, language=language)

    @staticmethod
    def render_json(report: ScanReport) -> str:
        return json.dumps(report.model_dump(mode="json"), ensure_ascii=False, indent=2)

    def write_html(self, report: ScanReport, destination: Path, language: str = "en") -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(self.render_html(report, language), encoding="utf-8")
        return destination
