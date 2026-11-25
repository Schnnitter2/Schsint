from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from schsint.database import Base, Database, ScanRepository, UserSettingsRepository


@pytest.mark.asyncio
async def test_history_and_language_can_be_managed(tmp_path) -> None:
    database = Database(f"sqlite+aiosqlite:///{tmp_path / 'test.db'}")
    await database.initialize()
    await database.settings.set_language(101, "ru")
    assert await database.settings.get_language(101) == "ru"
    assert await database.scans.history(101) == []
    assert await database.scans.delete_history(101) == 0
    await database.close()
