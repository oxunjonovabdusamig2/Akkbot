from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def admin_main_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="➕ Yangi akkaunt"), KeyboardButton(text="✏️ Tahrirlash"))
    builder.row(KeyboardButton(text="✅ Sotildi"), KeyboardButton(text="♻️ Qayta sotuvga"))
    builder.row(KeyboardButton(text="📌 Pin qilish"), KeyboardButton(text="🗑 O'chirish"))
    builder.row(KeyboardButton(text="🔎 ID bo'yicha qidirish"), KeyboardButton(text="📊 Statistika"))
    builder.row(KeyboardButton(text="👥 Adminlar"))
    return builder.as_markup(resize_keyboard=True)


def cancel_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="❌ Bekor qilish"))
    return builder.as_markup(resize_keyboard=True)


def skip_or_cancel_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="⏭ O'tkazib yuborish"))
    builder.row(KeyboardButton(text="❌ Bekor qilish"))
    return builder.as_markup(resize_keyboard=True)


def confirm_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Tasdiqlash va joylash", callback_data="confirm_post")
    builder.button(text="❌ Bekor qilish", callback_data="cancel_post")
    builder.adjust(1)
    return builder.as_markup()


def edit_field_keyboard(account_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💰 Narxi", callback_data=f"edit_field:{account_id}:price")
    builder.button(text="⚠️ Privyazka", callback_data=f"edit_field:{account_id}:privyazka")
    builder.button(text="📝 Tavsif", callback_data=f"edit_field:{account_id}:description")
    builder.button(text="🖼 Rasm", callback_data=f"edit_field:{account_id}:photo_id")
    builder.button(text="📹 Video/Isbot", callback_data=f"edit_field:{account_id}:video_id")
    builder.adjust(2)
    return builder.as_markup()


def delete_confirm_keyboard(account_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Ha, o'chirish", callback_data=f"delete_confirm:{account_id}")
    builder.button(text="❌ Yo'q", callback_data="delete_cancel")
    builder.adjust(1)
    return builder.as_markup()
