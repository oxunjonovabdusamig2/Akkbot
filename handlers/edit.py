import logging

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from database import db
from keyboards import admin_main_menu, cancel_keyboard, edit_field_keyboard, delete_confirm_keyboard
from states import EditAccount, PinAccount, DeleteAccount, SearchAccount
from utils.functions import update_channel_post, replace_media, pin_post, delete_post
from utils.templates import build_caption

logger = logging.getLogger(__name__)
router = Router(name="edit")


async def admin_only(message: Message) -> bool:
    if not await db.is_admin(message.from_user.id):
        await message.answer("⛔️ Sizda ushbu amal uchun ruxsat yo'q.")
        return False
    return True


def _parse_id(text: str):
    text = text.strip()
    if text.isdigit():
        return int(text)
    return None


# ---------------- TAHRIRLASH ----------------

@router.message(F.text == "✏️ Tahrirlash")
async def start_edit(message: Message, state: FSMContext):
    if not await admin_only(message):
        return
    await state.set_state(EditAccount.waiting_id)
    await message.answer("🔎 Tahrirlamoqchi bo'lgan akkauntning <b>ID</b> raqamini kiriting:", reply_markup=cancel_keyboard())


@router.message(EditAccount.waiting_id)
async def edit_got_id(message: Message, state: FSMContext):
    account_id = _parse_id(message.text)
    if account_id is None:
        await message.answer("❗️ Faqat raqam kiriting.")
        return
    account = await db.get_account(account_id)
    if not account:
        await message.answer("❌ Bunday ID topilmadi. Qaytadan kiriting yoki bekor qiling.")
        return
    await state.update_data(account_id=account_id)
    await state.set_state(EditAccount.choosing_field)
    await message.answer(
        f"✏️ ID {account_id} uchun qaysi maydonni tahrirlaysiz?",
        reply_markup=edit_field_keyboard(account_id),
    )


@router.callback_query(F.data.startswith("edit_field:"))
async def choose_field(callback: CallbackQuery, state: FSMContext):
    _, account_id, field = callback.data.split(":")
    await state.update_data(account_id=int(account_id), field=field)
    await state.set_state(EditAccount.waiting_value)

    field_names = {
        "price": ("💰 Yangi narxni kiriting:", "text"),
        "privyazka": ("⚠️ Yangi privyazka ma'lumotini kiriting:", "text"),
        "description": ("📝 Yangi tavsifni kiriting:", "text"),
        "photo_id": ("🖼 Yangi rasmni yuboring:", "photo"),
        "video_id": ("📹 Yangi video/isbotni yuboring:", "video"),
    }
    prompt, _ = field_names[field]
    await callback.message.answer(prompt, reply_markup=cancel_keyboard())
    await callback.answer()


@router.message(EditAccount.waiting_value, F.photo)
async def edit_value_photo(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    if data.get("field") != "photo_id":
        await message.answer("❗️ Siz matn maydonini tahrirlayapsiz, rasm emas.")
        return
    await _apply_edit(message, state, bot, message.photo[-1].file_id)


@router.message(EditAccount.waiting_value, F.video)
async def edit_value_video(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    if data.get("field") != "video_id":
        await message.answer("❗️ Siz matn maydonini tahrirlayapsiz, video emas.")
        return
    await _apply_edit(message, state, bot, message.video.file_id)


@router.message(EditAccount.waiting_value)
async def edit_value_text(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    if data.get("field") in ("photo_id", "video_id"):
        await message.answer("❗️ Iltimos, mos fayl (rasm/video) yuboring.")
        return
    await _apply_edit(message, state, bot, message.text)


async def _apply_edit(message: Message, state: FSMContext, bot: Bot, new_value: str):
    data = await state.get_data()
    account_id = data["account_id"]
    field = data["field"]

    await db.update_field(account_id, field, new_value)
    account = await db.get_account(account_id)

    if field in ("photo_id", "video_id"):
        ok = await replace_media(
            bot, account,
            new_photo_id=new_value if field == "photo_id" else None,
            new_video_id=new_value if field == "video_id" else None,
        )
    else:
        ok = await update_channel_post(bot, account)

    if ok:
        await message.answer(f"✅ ID {account_id} yangilandi va kanalda post yangilandi.", reply_markup=admin_main_menu())
    else:
        await message.answer(
            f"⚠️ Ma'lumot bazada yangilandi, lekin kanaldagi postni yangilashda xatolik yuz berdi.",
            reply_markup=admin_main_menu(),
        )
    await state.clear()


# ---------------- PIN ----------------

@router.message(F.text == "📌 Pin qilish")
async def start_pin(message: Message, state: FSMContext):
    if not await admin_only(message):
        return
    await state.set_state(PinAccount.waiting_id)
    await message.answer("🔎 Pin qilinadigan akkauntning ID raqamini kiriting:", reply_markup=cancel_keyboard())


@router.message(PinAccount.waiting_id)
async def pin_got_id(message: Message, state: FSMContext, bot: Bot):
    account_id = _parse_id(message.text)
    if account_id is None:
        await message.answer("❗️ Faqat raqam kiriting.")
        return
    account = await db.get_account(account_id)
    if not account:
        await message.answer("❌ Bunday ID topilmadi.")
        return
    ok = await pin_post(bot, account)
    if ok:
        await message.answer(f"📌 ID {account_id} posti pin qilindi.", reply_markup=admin_main_menu())
    else:
        await message.answer("⚠️ Pin qilishda xatolik yuz berdi.", reply_markup=admin_main_menu())
    await state.clear()


# ---------------- O'CHIRISH ----------------

@router.message(F.text == "🗑 O'chirish")
async def start_delete(message: Message, state: FSMContext):
    if not await admin_only(message):
        return
    await state.set_state(DeleteAccount.waiting_id)
    await message.answer("🔎 O'chiriladigan akkauntning ID raqamini kiriting:", reply_markup=cancel_keyboard())


@router.message(DeleteAccount.waiting_id)
async def delete_got_id(message: Message, state: FSMContext):
    account_id = _parse_id(message.text)
    if account_id is None:
        await message.answer("❗️ Faqat raqam kiriting.")
        return
    account = await db.get_account(account_id)
    if not account:
        await message.answer("❌ Bunday ID topilmadi.")
        return
    await state.update_data(account_id=account_id)
    await message.answer(
        f"⚠️ ID {account_id} rostdan ham o'chirilsinmi? Bu amalni qaytarib bo'lmaydi.",
        reply_markup=delete_confirm_keyboard(account_id),
    )


@router.callback_query(F.data.startswith("delete_confirm:"))
async def delete_confirm(callback: CallbackQuery, state: FSMContext, bot: Bot):
    account_id = int(callback.data.split(":")[1])
    account = await db.get_account(account_id)
    if account:
        await delete_post(bot, account)
        await db.delete_account(account_id)
        await callback.message.answer(f"🗑 ID {account_id} o'chirildi.", reply_markup=admin_main_menu())
    else:
        await callback.message.answer("❌ Topilmadi.", reply_markup=admin_main_menu())
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "delete_cancel")
async def delete_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("❌ Bekor qilindi.", reply_markup=admin_main_menu())
    await callback.answer()


# ---------------- QIDIRISH ----------------

@router.message(F.text == "🔎 ID bo'yicha qidirish")
async def start_search(message: Message, state: FSMContext):
    if not await admin_only(message):
        return
    await state.set_state(SearchAccount.waiting_id)
    await message.answer("🔎 Qidirilayotgan akkauntning ID raqamini kiriting:", reply_markup=cancel_keyboard())


@router.message(SearchAccount.waiting_id)
async def search_got_id(message: Message, state: FSMContext):
    account_id = _parse_id(message.text)
    if account_id is None:
        await message.answer("❗️ Faqat raqam kiriting.")
        return
    account = await db.get_account(account_id)
    await state.clear()
    if not account:
        await message.answer("❌ Bunday ID topilmadi.", reply_markup=admin_main_menu())
        return
    caption = build_caption(account)
    if account.video_id:
        await message.answer_video(account.video_id, caption=caption, reply_markup=admin_main_menu())
    elif account.photo_id:
        await message.answer_photo(account.photo_id, caption=caption, reply_markup=admin_main_menu())
    else:
        await message.answer(caption, reply_markup=admin_main_menu())
