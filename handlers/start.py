from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from database import db
from keyboards import admin_main_menu

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message):
    if await db.is_admin(message.from_user.id):
        await message.answer(
            "👋 Assalomu alaykum, Admin!",
            reply_markup=admin_main_menu(),
        )
    else:
        await message.answer(
            "👋 Salom! Bu bot faqat adminlar uchun mo'ljallangan.\n"
            "Sizga kirish huquqi berilmagan."
        )
