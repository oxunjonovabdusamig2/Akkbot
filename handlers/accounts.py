import logging

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from database import db
from keyboards import admin_main_menu, cancel_keyboard, skip_or_cancel_keyboard, confirm_keyboard
from models import Account
from states import AddAccount
from utils.functions import publish_account
from utils.templates import build_caption

logger = logging.getLogger(__name__)
router = Router(name="accounts")


async def admin_only(message: Message) -> bool:
    if not await db.is_admin(message.from_user.id):
        await message.answer("⛔️ Sizda ushbu amal uchun ruxsat yo'q.")
        return False
    return True


@router.message(F.text == "➕ Yangi akkaunt")
async def start_add_account(message: Message, state: FSMContext):
    if not await admin_only(message):
        return
    await state.set_state(AddAccount.photo)
    await message.answer(
        "🖼 Akkaunt uchun <b>rasm</b> yuboring.\n"
        "Agar rasm yo'q bo'lsa, o'tkazib yuborishingiz mumkin.",
        reply_markup=skip_or_cancel_keyboard(),
    )


@router.message(AddAccount.photo, F.photo)
async def add_photo(message: Message, state: FSMContext):
    await state.update_data(photo_id=message.photo[-1].file_id)
    await state.set_state(AddAccount.video)
    await message.answer(
        "📹 Endi <b>video yoki isbot</b> yuboring (ixtiyoriy).",
        reply_markup=skip_or_cancel_keyboard(),
    )


@router.message(AddAccount.photo, F.text == "⏭ O'tkazib yuborish")
async def skip_photo(message: Message, state: FSMContext):
    await state.update_data(photo_id=None)
    await state.set_state(AddAccount.video)
    await message.answer(
        "📹 Endi <b>video yoki isbot</b> yuboring (ixtiyoriy).",
        reply_markup=skip_or_cancel_keyboard(),
    )


@router.message(AddAccount.photo)
async def add_photo_invalid(message: Message):
    await message.answer("❗️ Iltimos, rasm yuboring yoki o'tkazib yuboring.")


@router.message(AddAccount.video, F.video)
async def add_video(message: Message, state: FSMContext):
    await state.update_data(video_id=message.video.file_id)
    await state.set_state(AddAccount.price)
    await message.answer("💰 Akkaunt <b>narxini</b> kiriting (masalan: 150 000 so'm):", reply_markup=cancel_keyboard())


@router.message(AddAccount.video, F.text == "⏭ O'tkazib yuborish")
async def skip_video(message: Message, state: FSMContext):
    await state.update_data(video_id=None)
    await state.set_state(AddAccount.price)
    await message.answer("💰 Akkaunt <b>narxini</b> kiriting (masalan: 150 000 so'm):", reply_markup=cancel_keyboard())


@router.message(AddAccount.video)
async def add_video_invalid(message: Message):
    await message.answer("❗️ Iltimos, video yuboring yoki o'tkazib yuboring.")


@router.message(AddAccount.price)
async def add_price(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await state.set_state(AddAccount.privyazka)
    await message.answer(
        "⚠️ <b>Privyazka</b> ma'lumotini kiriting (raqam, pochta va h.k.):",
        reply_markup=cancel_keyboard(),
    )


@router.message(AddAccount.privyazka)
async def add_privyazka(message: Message, state: FSMContext):
    await state.update_data(privyazka=message.text)
    await state.set_state(AddAccount.description)
    await message.answer("📝 Akkaunt haqida <b>tavsif</b> kiriting:", reply_markup=cancel_keyboard())


@router.message(AddAccount.description)
async def add_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    data = await state.get_data()

    preview = Account(
        id=0,
        price=data["price"],
        privyazka=data["privyazka"],
        description=data["description"],
        photo_id=data.get("photo_id"),
        video_id=data.get("video_id"),
        status="active",
        message_id=None,
        created_at="",
        created_by=message.from_user.id,
    )
    caption = build_caption(preview).replace("🆔 <b>ID:</b> 0\n", "")

    await state.set_state(AddAccount.confirm)

    if data.get("video_id"):
        await message.answer_video(data["video_id"], caption=caption, reply_markup=confirm_keyboard())
    elif data.get("photo_id"):
        await message.answer_photo(data["photo_id"], caption=caption, reply_markup=confirm_keyboard())
    else:
        await message.answer(caption, reply_markup=confirm_keyboard())


@router.callback_query(AddAccount.confirm, F.data == "confirm_post")
async def confirm_post(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    account_id = await db.add_account(
        price=data["price"],
        privyazka=data["privyazka"],
        description=data["description"],
        photo_id=data.get("photo_id"),
        video_id=data.get("video_id"),
        created_by=callback.from_user.id,
    )
    account = await db.get_account(account_id)
    try:
        message_id = await publish_account(bot, account)
        await db.set_message_id(account_id, message_id)
        await callback.message.answer(
            f"✅ Akkaunt (ID: {account_id}) muvaffaqiyatli kanalga joylandi!",
            reply_markup=admin_main_menu(),
        )
    except Exception:
        logger.exception("Kanalga joylashda xatolik")
        await callback.message.answer(
            "⚠️ Akkaunt bazaga saqlandi, lekin kanalga joylashda xatolik yuz berdi. "
            "Iltimos, kanal ID/username to'g'riligini va bot admin ekanini tekshiring.",
            reply_markup=admin_main_menu(),
        )
    await state.clear()
    await callback.answer()


@router.callback_query(AddAccount.confirm, F.data == "cancel_post")
async def cancel_post(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("❌ Bekor qilindi.", reply_markup=admin_main_menu())
    await callback.answer()
