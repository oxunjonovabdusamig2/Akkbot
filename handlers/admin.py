from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import config
from database import db
from keyboards import admin_main_menu, cancel_keyboard
from states import AddAdmin, RemoveAdmin

router = Router(name="admin")


async def admin_only(message: Message) -> bool:
    if not await db.is_admin(message.from_user.id):
        await message.answer("⛔️ Sizda ushbu amal uchun ruxsat yo'q.")
        return False
    return True


@router.message(F.text == "📊 Statistika")
async def show_statistics(message: Message):
    if not await admin_only(message):
        return
    stats = await db.stats()
    text = (
        "📊 <b>Statistika</b>\n\n"
        f"📦 Jami akkauntlar: <b>{stats['total']}</b>\n"
        f"📌 Sotuvda: <b>{stats['active']}</b>\n"
        f"✅ Sotilgan: <b>{stats['sold']}</b>"
    )
    await message.answer(text)


@router.message(F.text == "👥 Adminlar")
async def admins_menu(message: Message):
    if not await admin_only(message):
        return
    admins = await db.list_admins()
    text = "👥 <b>Adminlar ro'yxati:</b>\n\n" + "\n".join(f"• <code>{a}</code>" for a in admins)
    text += (
        "\n\nYangi admin qo'shish uchun: /addadmin <user_id>\n"
        "Adminni o'chirish uchun: /removeadmin <user_id>"
    )
    await message.answer(text)


@router.message(Command("addadmin"))
async def add_admin_cmd(message: Message):
    if not await admin_only(message):
        return
    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("❗️ Foydalanish: /addadmin <user_id>")
        return
    new_admin_id = int(parts[1])
    await db.add_admin(new_admin_id, added_by=message.from_user.id)
    await message.answer(f"✅ <code>{new_admin_id}</code> admin sifatida qo'shildi.")


@router.message(Command("removeadmin"))
async def remove_admin_cmd(message: Message):
    if not await admin_only(message):
        return
    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("❗️ Foydalanish: /removeadmin <user_id>")
        return
    target_id = int(parts[1])
    if target_id == config.SUPER_ADMIN_ID:
        await message.answer("⛔️ Bosh adminni o'chirib bo'lmaydi.")
        return
    await db.remove_admin(target_id)
    await message.answer(f"🗑 <code>{target_id}</code> adminlikdan chiqarildi.")


@router.message(F.text == "❌ Bekor qilish", StateFilter("*"))
async def cancel_any_state(message: Message, state: FSMContext):
    current = await state.get_state()
    if current is None:
        return
    await state.clear()
    await message.answer("❌ Amal bekor qilindi.", reply_markup=admin_main_menu())
