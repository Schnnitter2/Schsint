"""Telegram language selection keyboard."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

LANGUAGES = {"en": "🇬🇧 English", "es": "🇪🇸 Español", "de": "🇩🇪 Deutsch", "ru": "🇷🇺 Русский"}


def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=label, callback_data=f"lang:{code}")
        for code, label in LANGUAGES.items()
    ]])


def consent_keyboard(language: str) -> InlineKeyboardMarkup:
    labels = {"en": "I confirm permission", "es": "Confirmo el permiso", "de": "Berechtigung bestätigen", "ru": "Подтверждаю разрешение"}
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=labels.get(language, labels["en"]), callback_data="scan:consent")
    ], [InlineKeyboardButton(text="Cancel", callback_data="scan:cancel")]])
