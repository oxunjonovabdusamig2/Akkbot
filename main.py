import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import config
from database import db

from handlers import start, admin, accounts, edit, sold, statistics
from aiogram.types import ErrorEvent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    if config.BOT_TOKEN == "PUT_YOUR_BOT_TOKEN_HERE":
        logger.error("config.py da BOT_TOKEN kiritilmagan! Iltimos BOT_TOKEN ni to'g'rilang.")
        return

    await db.init()

    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    # Routerlarni ro'yxatdan o'tkazish
    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(accounts.router)
    dp.include_router(edit.router)
    dp.include_router(sold.router)
    dp.include_router(statistics.router)

    @dp.errors()
    async def global_error_handler(event: ErrorEvent):
        """Botni xatoliklardan himoya qiladi - hech qanday xatolik bot ishini to'xtatmaydi."""
        logger.exception(
            "Xatolik yuz berdi: %s | Update: %s", event.exception, event.update
        )
        return True

    logger.info("Bot ishga tushmoqda...")
    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
