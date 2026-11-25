"""SQLite persistence with minimal scan history and explicit deletion."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ScanRecord(Base):
    __tablename__ = "scans"

    scan_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    telegram_user_id: Mapped[int] = mapped_column(Integer, index=True)
    username: Mapped[str] = mapped_column(String(64))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(24))
    findings_count: Mapped[int] = mapped_column(Integer, default=0)
    modules: Mapped[list["ModuleRecord"]] = relationship(
        back_populates="scan", cascade="all, delete-orphan", lazy="selectin"
    )


class ModuleRecord(Base):
    __tablename__ = "module_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    scan_id: Mapped[str] = mapped_column(ForeignKey("scans.scan_id", ondelete="CASCADE"), index=True)
    module: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(24))
    checked_sources: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    scan: Mapped[ScanRecord] = relationship(back_populates="modules")


class UserSetting(Base):
    __tablename__ = "user_settings"

    telegram_user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    language: Mapped[str] = mapped_column(String(2), default="en")


class ScanRepository:
    def __init__(self, sessions: async_sessionmaker[AsyncSession]) -> None:
        self.sessions = sessions

    async def save(self, report, telegram_user_id: int) -> None:
        status = "completed" if all(item.status.value != "failed" for item in report.modules) else "partial"
        async with self.sessions() as session:
            record = ScanRecord(
                scan_id=report.scan_id,
                telegram_user_id=telegram_user_id,
                username=report.username,
                started_at=report.started_at,
                completed_at=report.completed_at,
                status=status,
                findings_count=len(report.findings),
                modules=[ModuleRecord(
                    module=item.module,
                    status=item.status.value,
                    checked_sources=item.checked_sources,
                    error=item.error,
                ) for item in report.modules],
            )
            session.add(record)
            await session.commit()

    async def history(self, telegram_user_id: int, limit: int = 10) -> list[ScanRecord]:
        async with self.sessions() as session:
            result = await session.scalars(
                select(ScanRecord)
                .where(ScanRecord.telegram_user_id == telegram_user_id)
                .order_by(ScanRecord.completed_at.desc())
                .limit(max(1, min(limit, 50)))
            )
            return list(result.all())

    async def delete_history(self, telegram_user_id: int) -> int:
        async with self.sessions() as session:
            result = await session.execute(delete(ScanRecord).where(ScanRecord.telegram_user_id == telegram_user_id))
            await session.commit()
            return int(result.rowcount or 0)


class UserSettingsRepository:
    def __init__(self, sessions: async_sessionmaker[AsyncSession]) -> None:
        self.sessions = sessions

    async def get_language(self, telegram_user_id: int) -> str:
        async with self.sessions() as session:
            setting = await session.get(UserSetting, telegram_user_id)
            return setting.language if setting else "en"

    async def set_language(self, telegram_user_id: int, language: str) -> None:
        if language not in {"en", "es", "de", "ru"}:
            raise ValueError("unsupported language")
        async with self.sessions() as session:
            setting = await session.get(UserSetting, telegram_user_id)
            if setting is None:
                session.add(UserSetting(telegram_user_id=telegram_user_id, language=language))
            else:
                setting.language = language
            await session.commit()


class Database:
    def __init__(self, url: str) -> None:
        self.engine = create_async_engine(url)
        self.sessions = async_sessionmaker(self.engine, expire_on_commit=False)
        self.scans = ScanRepository(self.sessions)
        self.settings = UserSettingsRepository(self.sessions)

    async def initialize(self) -> None:
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def close(self) -> None:
        await self.engine.dispose()
