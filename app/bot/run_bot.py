import asyncio

from app.bot.create_bot import bot, dp
from app.bot.handlers.start import start_router


async def main():
    dp.include_router(start_router)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass