from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram_i18n import I18nContext
from decouple import config

from app.bot.fsm.login_fsm import LoginFSM

start_router = Router()
SUPPORTED_LOCALES = {"ru", "en"}


def language_buttons(screen: str, i18n: I18nContext) -> list[InlineKeyboardButton]:
    return [
        InlineKeyboardButton(
            text=i18n.get("button-lang-ru"),
            callback_data=f"locale:ru:{screen}",
        ),
        InlineKeyboardButton(
            text=i18n.get("button-lang-en"),
            callback_data=f"locale:en:{screen}",
        ),
    ]


def start_keyboard(i18n: I18nContext) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.get("button-login"), callback_data="auth:login"
                )
            ],
            [
                InlineKeyboardButton(
                    text=i18n.get("button-about"), callback_data="public:about"
                ),
                InlineKeyboardButton(
                    text=i18n.get("button-help"), callback_data="public:help"
                ),
            ],
            language_buttons("start", i18n),
        ]
    )


def login_keyboard(i18n: I18nContext) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.get("button-back"), callback_data="nav:start"
                )
            ],
            language_buttons("login", i18n),
        ]
    )


def hub_keyboard(i18n: I18nContext) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.get("button-about"), callback_data="hub:about"
                ),
                InlineKeyboardButton(
                    text=i18n.get("button-security"),
                    callback_data="hub:security",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=i18n.get("button-help"), callback_data="hub:help"
                )
            ],
            language_buttons("hub", i18n),
        ]
    )


def back_to_hub_keyboard(i18n: I18nContext, screen: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.get("button-panel"), callback_data="hub:menu"
                )
            ],
            language_buttons(screen, i18n),
        ]
    )


def back_to_start_keyboard(i18n: I18nContext, screen: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.get("button-start"), callback_data="nav:start"
                )
            ],
            language_buttons(screen, i18n),
        ]
    )


async def clear_state_keep_locale(state: FSMContext, i18n: I18nContext) -> None:
    locale = i18n.locale
    await state.clear()
    await i18n.set_locale(locale)


async def edit_screen(message: Message, screen: str, i18n: I18nContext) -> None:
    if screen == "login":
        await message.edit_text(
            i18n.get("login-text"), reply_markup=login_keyboard(i18n)
        )
    elif screen == "hub":
        await message.edit_text(
            i18n.get("main-menu-text"), reply_markup=hub_keyboard(i18n)
        )
    elif screen == "about-hub":
        await message.edit_text(
            i18n.get("about-text"),
            reply_markup=back_to_hub_keyboard(i18n, "about-hub"),
        )
    elif screen == "security":
        await message.edit_text(
            i18n.get("security-text"),
            reply_markup=back_to_hub_keyboard(i18n, "security"),
        )
    elif screen == "help-hub":
        await message.edit_text(
            i18n.get("help-text"),
            reply_markup=back_to_hub_keyboard(i18n, "help-hub"),
        )
    elif screen == "about-public":
        await message.edit_text(
            i18n.get("about-text"),
            reply_markup=back_to_start_keyboard(i18n, "about-public"),
        )
    elif screen == "help-public":
        await message.edit_text(
            i18n.get("help-text"),
            reply_markup=back_to_start_keyboard(i18n, "help-public"),
        )
    else:
        await message.edit_text(
            i18n.get("start-text"), reply_markup=start_keyboard(i18n)
        )


@start_router.message(CommandStart())
async def start(message: Message, i18n: I18nContext):
    await message.answer(i18n.get("start-text"), reply_markup=start_keyboard(i18n))


@start_router.message(Command("login"))
async def request_login(message: Message, state: FSMContext, i18n: I18nContext):
    await state.set_state(LoginFSM.login)
    await message.answer(i18n.get("login-text"), reply_markup=login_keyboard(i18n))


@start_router.message(F.text, LoginFSM.login)
async def check_login_password(message: Message, state: FSMContext, i18n: I18nContext):
    if message.text == config("LOGIN_PASSWORD"):
        await clear_state_keep_locale(state, i18n)
        await message.answer(
            i18n.get("main-menu-text"), reply_markup=hub_keyboard(i18n)
        )
    else:
        await message.answer(i18n.get("denied-text"), reply_markup=login_keyboard(i18n))


@start_router.callback_query(F.data == "auth:login")
async def login_from_button(
    callback: CallbackQuery, state: FSMContext, i18n: I18nContext
):
    await state.set_state(LoginFSM.login)
    if callback.message:
        await callback.message.edit_text(
            i18n.get("login-text"), reply_markup=login_keyboard(i18n)
        )
    await callback.answer()


@start_router.callback_query(F.data == "nav:start")
async def back_to_start(callback: CallbackQuery, state: FSMContext, i18n: I18nContext):
    await clear_state_keep_locale(state, i18n)
    if callback.message:
        await callback.message.edit_text(
            i18n.get("start-text"), reply_markup=start_keyboard(i18n)
        )
    await callback.answer()


@start_router.callback_query(F.data == "hub:menu")
async def show_hub_menu(callback: CallbackQuery, i18n: I18nContext):
    if callback.message:
        await callback.message.edit_text(
            i18n.get("main-menu-text"), reply_markup=hub_keyboard(i18n)
        )
    await callback.answer()


@start_router.callback_query(F.data == "hub:about")
async def show_about(callback: CallbackQuery, i18n: I18nContext):
    if callback.message:
        await callback.message.edit_text(
            i18n.get("about-text"),
            reply_markup=back_to_hub_keyboard(i18n, "about-hub"),
        )
    await callback.answer()


@start_router.callback_query(F.data == "hub:security")
async def show_security(callback: CallbackQuery, i18n: I18nContext):
    if callback.message:
        await callback.message.edit_text(
            i18n.get("security-text"),
            reply_markup=back_to_hub_keyboard(i18n, "security"),
        )
    await callback.answer()


@start_router.callback_query(F.data == "hub:help")
async def show_help(callback: CallbackQuery, i18n: I18nContext):
    if callback.message:
        await callback.message.edit_text(
            i18n.get("help-text"),
            reply_markup=back_to_hub_keyboard(i18n, "help-hub"),
        )
    await callback.answer()


@start_router.callback_query(F.data == "public:about")
async def show_public_about(callback: CallbackQuery, i18n: I18nContext):
    if callback.message:
        await callback.message.edit_text(
            i18n.get("about-text"),
            reply_markup=back_to_start_keyboard(i18n, "about-public"),
        )
    await callback.answer()


@start_router.callback_query(F.data == "public:help")
async def show_public_help(callback: CallbackQuery, i18n: I18nContext):
    if callback.message:
        await callback.message.edit_text(
            i18n.get("help-text"),
            reply_markup=back_to_start_keyboard(i18n, "help-public"),
        )
    await callback.answer()


@start_router.callback_query(F.data.startswith("locale:"))
async def change_locale(callback: CallbackQuery, i18n: I18nContext):
    _, locale, screen = callback.data.split(":", maxsplit=2)
    if locale not in SUPPORTED_LOCALES:
        await callback.answer()
        return

    await i18n.set_locale(locale)
    if callback.message:
        await edit_screen(callback.message, screen, i18n)
    await callback.answer(i18n.get("language-updated"))
