import logging
from pathlib import Path

from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores.fluent_runtime_core import FluentRuntimeCore
from aiogram_i18n.managers.fsm import FSMManager
from decouple import config

raw_admins = config("ADMINS", default="")
admins = [
    int(admin_id.strip()) for admin_id in raw_admins.split(",") if admin_id.strip()
]

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

bot = Bot(
    token=config("TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=RedisStorage.from_url(config("REDIS_URL")))

locales_path = Path(__file__).resolve().parent / "locales" / "{locale}" / "LC_MESSAGES"
i18n_middleware = I18nMiddleware(
    core=FluentRuntimeCore(path=locales_path, default_locale="ru"),
    manager=FSMManager(default_locale="ru"),
    default_locale="ru",
)
i18n_middleware.setup(dispatcher=dp)
