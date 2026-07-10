from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from database import db

router = Router(name="statistics")


@router.message(Command("last"))
async def last_accounts(message: Message):
    """So'nggi 10 ta akkauntni ko'rsatadi: /last"""
    if not await db.is_admin(message.from_user.id):
        await message.answer("⛔️ Sizda ushbu amal uchun ruxsat yo'q.")
        return

    accounts = await db.list_accounts()
    if not accounts:
        await message.answer("📦 Hozircha akkauntlar mavjud emas.")
        return

    lines = ["📋 <b>So'nggi akkauntlar:</b>\n"]
    for acc in accounts[:10]:
        status_emoji = "✅" if acc.status == "sold" else "📌"
        lines.append(f"{status_emoji} ID <b>{acc.id}</b> — {acc.price}")
    await message.answer("\n".join(lines))
