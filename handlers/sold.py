from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database import db
from keyboards import admin_main_menu, cancel_keyboard
from states import SoldAccount, RelistAccount
from utils.functions import update_channel_post

router = Router(name="sold")


async def admin_only(message: Message) -> bool:
    if not await db.is_admin(message.from_user.id):
        await message.answer("⛔️ Sizda ushbu amal uchun ruxsat yo'q.")
        return False
    return True


def _parse_id(text: str):
    text = text.strip()
    return int(text) if text.isdigit() else None


# ---------------- SOTILDI ----------------

@router.message(F.text == "✅ Sotildi")
async def start_sold(message: Message, state: FSMContext):
    if not await admin_only(message):
        return
    await state.set_state(SoldAccount.waiting_id)
    await message.answer("🔎 Sotilgan akkauntning ID raqamini kiriting:", reply_markup=cancel_keyboard())


@router.message(SoldAccount.waiting_id)
async def sold_got_id(message: Message, state: FSMContext, bot: Bot):
    account_id = _parse_id(message.text)
    if account_id is None:
        await message.answer("❗️ Faqat raqam kiriting.")
        return
    account = await db.get_account(account_id)
    if not account:
        await message.answer("❌ Bunday ID topilmadi.")
        return
    if account.status == "sold":
        await message.answer("ℹ️ Bu akkaunt allaqachon 'sotilgan' deb belgilangan.")
        await state.clear()
        return

    await db.update_field(account_id, "status", "sold")
    account = await db.get_account(account_id)
    ok = await update_channel_post(bot, account)

    if ok:
        await message.answer(f"✅ ID {account_id} 'SOTILDI' deb belgilandi va post yangilandi.", reply_markup=admin_main_menu())
    else:
        await message.answer("⚠️ Baza yangilandi, lekin kanal postini yangilashda xatolik yuz berdi.", reply_markup=admin_main_menu())
    await state.clear()


# ---------------- QAYTA SOTUVGA CHIQARISH ----------------

@router.message(F.text == "♻️ Qayta sotuvga")
async def start_relist(message: Message, state: FSMContext):
    if not await admin_only(message):
        return
    await state.set_state(RelistAccount.waiting_id)
    await message.answer("🔎 Qayta sotuvga chiqariladigan akkauntning ID raqamini kiriting:", reply_markup=cancel_keyboard())


@router.message(RelistAccount.waiting_id)
async def relist_got_id(message: Message, state: FSMContext, bot: Bot):
    account_id = _parse_id(message.text)
    if account_id is None:
        await message.answer("❗️ Faqat raqam kiriting.")
        return
    account = await db.get_account(account_id)
    if not account:
        await message.answer("❌ Bunday ID topilmadi.")
        return
    if account.status == "active":
        await message.answer("ℹ️ Bu akkaunt allaqachon sotuvda.")
        await state.clear()
        return

    await db.update_field(account_id, "status", "active")
    account = await db.get_account(account_id)
    ok = await update_channel_post(bot, account)

    if ok:
        await message.answer(f"♻️ ID {account_id} qayta sotuvga chiqarildi va post yangilandi.", reply_markup=admin_main_menu())
    else:
        await message.answer("⚠️ Baza yangilandi, lekin kanal postini yangilashda xatolik yuz berdi.", reply_markup=admin_main_menu())
    await state.clear()
