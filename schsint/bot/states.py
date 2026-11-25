"""FSM states for the guided scan flow."""

from aiogram.fsm.state import State, StatesGroup


class ScanFlow(StatesGroup):
    username = State()
    consent = State()
