import logging

from aiogram import Bot
from aiogram.types import InputMediaPhoto, InputMediaVideo
from aiogram.exceptions import TelegramBadRequest

from config import config
from models import Account
from utils.templates import build_caption

logger = logging.getLogger(__name__)


async def publish_account(bot: Bot, account: Account) -> int:
    """Akkauntni kanalga joylaydi va message_id ni qaytaradi."""
    caption = build_caption(account)
    try:
        if account.video_id:
            msg = await bot.send_video(
                chat_id=config.CHANNEL_ID,
                video=account.video_id,
                caption=caption,
                parse_mode="HTML",
            )
        elif account.photo_id:
            msg = await bot.send_photo(
                chat_id=config.CHANNEL_ID,
                photo=account.photo_id,
                caption=caption,
                parse_mode="HTML",
            )
        else:
            msg = await bot.send_message(
                chat_id=config.CHANNEL_ID, text=caption, parse_mode="HTML"
            )
        return msg.message_id
    except Exception as e:
        logger.exception("Postni kanalga joylashda xatolik: %s", e)
        raise


async def update_channel_post(bot: Bot, account: Account) -> bool:
    """Kanaldagi mavjud postni yangilaydi. Xatolikdan himoyalangan."""
    if not account.message_id:
        return False
    caption = build_caption(account)
    try:
        if account.video_id or account.photo_id:
            await bot.edit_message_caption(
                chat_id=config.CHANNEL_ID,
                message_id=account.message_id,
                caption=caption,
                parse_mode="HTML",
            )
        else:
            await bot.edit_message_text(
                chat_id=config.CHANNEL_ID,
                message_id=account.message_id,
                text=caption,
                parse_mode="HTML",
            )
        return True
    except TelegramBadRequest as e:
        # Masalan "message is not modified" yoki topilmasa
        logger.warning("Postni tahrirlab bo'lmadi: %s", e)
        return False
    except Exception as e:
        logger.exception("Postni yangilashda kutilmagan xatolik: %s", e)
        return False


async def replace_media(bot: Bot, account: Account, new_photo_id: str = None, new_video_id: str = None) -> bool:
    """Postdagi rasm yoki videoni almashtiradi (media butunlay o'zgargani uchun edit_media ishlatiladi)."""
    if not account.message_id:
        return False
    caption = build_caption(account)
    try:
        if new_video_id:
            media = InputMediaVideo(media=new_video_id, caption=caption, parse_mode="HTML")
        elif new_photo_id:
            media = InputMediaPhoto(media=new_photo_id, caption=caption, parse_mode="HTML")
        else:
            return False
        await bot.edit_message_media(
            chat_id=config.CHANNEL_ID, message_id=account.message_id, media=media
        )
        return True
    except Exception as e:
        logger.exception("Mediani almashtirishda xatolik: %s", e)
        return False


async def pin_post(bot: Bot, account: Account) -> bool:
    if not account.message_id:
        return False
    try:
        await bot.pin_chat_message(chat_id=config.CHANNEL_ID, message_id=account.message_id)
        return True
    except Exception as e:
        logger.exception("Pin qilishda xatolik: %s", e)
        return False


async def delete_post(bot: Bot, account: Account) -> bool:
    if not account.message_id:
        return False
    try:
        await bot.delete_message(chat_id=config.CHANNEL_ID, message_id=account.message_id)
        return True
    except Exception as e:
        logger.exception("Postni o'chirishda xatolik: %s", e)
        return False
