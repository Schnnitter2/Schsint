"""Application settings parsed from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    bot_token: str
    admin_ids: frozenset[int]
    database_url: str
    data_dir: Path
    rate_limit_per_hour: int
    max_username_length: int

    @classmethod
    def from_env(cls) -> "Settings":
        raw_admins = os.getenv("ADMIN_IDS", "")
        try:
            admins = frozenset(int(value.strip()) for value in raw_admins.split(",") if value.strip())
        except ValueError as exc:
            raise ValueError("ADMIN_IDS must be comma-separated Telegram numeric IDs") from exc
        data_dir = Path(os.getenv("DATA_DIR", "data"))
        return cls(
            bot_token=os.getenv("BOT_TOKEN", ""),
            admin_ids=admins,
            database_url=os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{data_dir / 'schsint.db'}"),
            data_dir=data_dir,
            rate_limit_per_hour=max(1, int(os.getenv("RATE_LIMIT_PER_HOUR", "5"))),
            max_username_length=64,
        )
