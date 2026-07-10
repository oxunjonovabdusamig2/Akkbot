from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from database import db
from keyboards import admin_main_menu

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "👋 Assalomu alaykum!\n\nXush kelibsiz.",
        reply_markup=admin_main_menu(),
    )
