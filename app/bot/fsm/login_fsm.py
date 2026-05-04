from aiogram.fsm.state import StatesGroup, State


class LoginFSM(StatesGroup):
    login = State()
