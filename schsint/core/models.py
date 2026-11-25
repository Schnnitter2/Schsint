"""Validated contracts shared by the engine, adapters, and reports."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ScanRequest(BaseModel):
    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    username: str = Field(min_length=1, max_length=64)
    consent_confirmed: bool

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        if value.startswith((".", "-", "_")) or value.endswith((".", "-", "_")):
            raise ValueError("username must start and end with a letter or number")
        if not all(char.isalnum() or char in "._-" for char in value):
            raise ValueError("only letters, numbers, '.', '_' and '-' are allowed")
        return value

    @field_validator("consent_confirmed")
    @classmethod
    def require_consent(cls, value: bool) -> bool:
        if value is not True:
            raise ValueError("authorization confirmation is required")
        return value


class Finding(BaseModel):
    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    source: str = Field(min_length=1, max_length=120)
    url: str = Field(min_length=1, max_length=2048)
    module: str = Field(min_length=1, max_length=80)
    status: str = Field(min_length=1, max_length=40)
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    confidence_note: str = Field(
        default="A username match alone does not establish that accounts belong to the same person.",
        max_length=500,
    )


class ModuleStatus(StrEnum):
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ModuleResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    module: str = Field(min_length=1, max_length=80)
    status: ModuleStatus
    checked_sources: int = Field(default=0, ge=0)
    findings: tuple[Finding, ...] = ()
    error: str | None = Field(default=None, max_length=500)


class ScanProgress(BaseModel):
    model_config = ConfigDict(frozen=True)

    scan_id: str
    active_module: str
    processed_sources: int = Field(default=0, ge=0)
    total_sources: int = Field(default=0, ge=0)
    status: str
    message: str = Field(default="", max_length=300)


class ScanReport(BaseModel):
    model_config = ConfigDict(frozen=True)

    scan_id: str = Field(default_factory=lambda: str(uuid4()))
    username: str = Field(min_length=1, max_length=64)
    started_at: datetime
    completed_at: datetime
    modules: tuple[ModuleResult, ...]
    findings: tuple[Finding, ...]
    duplicate_count: int = Field(default=0, ge=0)
