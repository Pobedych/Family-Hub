from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from decouple import config

from app.bot.fsm.login_fsm import LoginFSM

start_router = Router()

@start_router.message(CommandStart())
async def start(message: Message):
    await message.answer("Чтобы начать пользоваться ботом введите /login")

@start_router.message(Command["login"])
async def login(message: Message, state: FSMContext):
    await state.set_state(LoginFSM.login)
    await message.answer("Введите свой пароль")

@start_router.message(F.text, LoginFSM.login)
async def login(message: Message, state: FSMContext):
    if message.text == config("LOGIN_PASSWORD"):
        await message.answer("Доступ разрешен, нажмите /start")
        await state.clear()
    else:
        await message.answer("Access denied")



