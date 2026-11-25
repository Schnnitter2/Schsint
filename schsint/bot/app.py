"""Telegram bot entry point; all scans are offline-only in this release."""

from __future__ import annotations

import asyncio
import logging
import time
from collections import defaultdict, deque
from datetime import datetime

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from pydantic import ValidationError

from schsint.bot.keyboards import LANGUAGES, consent_keyboard, language_keyboard
from schsint.bot.states import ScanFlow
from schsint.config import Settings
from schsint.core.engine import CoreEngine
from schsint.core.models import ScanRequest
from schsint.database import Database
from schsint.i18n import get_text
from schsint.modules.offline_demo import OfflineDemoModule
from schsint.reports import ReportGenerator

logger = logging.getLogger("schsint")
router = Router()
settings: Settings
 database: Database
engine: CoreEngine
reporter = ReportGenerator()
rate_events: dict[int, deque[float]] = defaultdict(deque)


def language_for(user_id: int) -> str:
    return "en"


async def get_language(user_id: int) -> str:
    return await database.settings.get_language(user_id)


def is_admin(user_id: int) -> bool:
    return bool(settings.admin_ids) and user_id in settings.admin_ids


def rate_allowed(user_id: int) -> bool:
    now = time.monotonic()
    events = rate_events[user_id]
    while events and now - events[0] > 3600:
        events.popleft()
    if len(events) >= settings.rate_limit_per_hour:
        return False
    events.append(now)
    return True


@router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id
    language = await get_language(user_id)
    await message.answer(get_text(language, "welcome"), reply_markup=language_keyboard())


@router.callback_query(F.data.startswith("lang:"))
async def choose_language(callback: CallbackQuery) -> None:
    code = callback.data.split(":", 1)[1]
    if code not in LANGUAGES:
        await callback.answer("Unsupported language", show_alert=True)
        return
    await database.settings.set_language(callback.from_user.id, code)
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(get_text(code, "ready"))


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    language = await get_language(message.from_user.id)
    await message.answer(get_text(language, "help"))


@router.message(Command("settings"))
async def settings_command(message: Message) -> None:
    language = await get_language(message.from_user.id)
    await message.answer(get_text(language, "settings"), reply_markup=language_keyboard())


@router.message(Command("scan"))
async def scan_command(message: Message, state: FSMContext) -> None:
    language = await get_language(message.from_user.id)
    if not is_admin(message.from_user.id):
        await message.answer(get_text(language, "restricted"))
        return
    if not rate_allowed(message.from_user.id):
        await message.answer("Rate limit reached. Try again later.")
        return
    await state.set_state(ScanFlow.username)
    await message.answer(get_text(language, "consent_prompt"))


@router.message(ScanFlow.username)
async def receive_username(message: Message, state: FSMContext) -> None:
    language = await get_language(message.from_user.id)
    username = (message.text or "").strip()
    try:
        ScanRequest(username=username, consent_confirmed=True)
    except ValidationError:
        await message.answer(get_text(language, "invalid"))
        return
    await state.update_data(username=username)
    await state.set_state(ScanFlow.consent)
    await message.answer(get_text(language, "consent"), reply_markup=consent_keyboard(language))


@router.callback_query(F.data == "scan:cancel")
async def cancel_scan(callback: CallbackQuery, state: FSMContext) -> None:
    language = await get_language(callback.from_user.id)
    await state.clear()
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(get_text(language, "cancel"))


@router.callback_query(F.data == "scan:consent", ScanFlow.consent)
async def confirm_scan(callback: CallbackQuery, state: FSMContext) -> None:
    language = await get_language(callback.from_user.id)
    if not is_admin(callback.from_user.id):
        await state.clear()
        await callback.answer(get_text(language, "restricted"), show_alert=True)
        return
    data = await state.get_data()
    await state.clear()
    try:
        request = ScanRequest(username=data["username"], consent_confirmed=True)
        report = await engine.run(request)
        await database.scans.save(report, callback.from_user.id)
        html = reporter.render_html(report, language)
        document = BufferedInputFile(html.encode("utf-8"), filename=f"schsint-{report.scan_id}.html")
        await callback.answer()
        if callback.message:
            await callback.message.answer_document(document, caption=get_text(language, "done"))
    except Exception:
        logger.exception("Scan/report operation failed")
        await callback.answer(get_text(language, "error"), show_alert=True)


@router.message(Command("history"))
async def history_command(message: Message) -> None:
    language = await get_language(message.from_user.id)
    if not is_admin(message.from_user.id):
        await message.answer(get_text(language, "restricted"))
        return
    records = await database.scans.history(message.from_user.id)
    if not records:
        await message.answer(get_text(language, "history_empty"))
        return
    lines = [get_text(language, "history")]
    lines.extend(
        f"• {record.completed_at:%Y-%m-%d %H:%M} UTC · @{record.username} · {record.status} · {record.findings_count} result(s)"
        for record in records
    )
    await message.answer("\n".join(lines))


@router.message(Command("delete_history"))
async def delete_history_command(message: Message) -> None:
    language = await get_language(message.from_user.id)
    if not is_admin(message.from_user.id):
        await message.answer(get_text(language, "restricted"))
        return
    count = await database.scans.delete_history(message.from_user.id)
    await message.answer(get_text(language, "deleted", count=count))


async def main() -> None:
    global settings, database, engine
    settings = Settings.from_env()
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN is required")
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    database = Database(settings.database_url)
    await database.initialize()
    engine = CoreEngine([OfflineDemoModule()], max_concurrent_scans=2, max_parallel_modules=2)
    bot = Bot(settings.bot_token)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)
    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()
        await database.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
