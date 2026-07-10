import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()  # loyiha papkasidagi .env faylini o'qiydi (agar mavjud bo'lsa)


@dataclass
class Config:
    # Bot tokenini @BotFather dan oling
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "PUT_YOUR_BOT_TOKEN_HERE")

    # Postlar joylanadigan kanal (username yoki -100... ID)
    CHANNEL_ID: str = os.getenv("CHANNEL_ID", "@your_channel_username")

    # Botni ishga tushirgan super-admin (u boshqa adminlarni qo'sha oladi)
    SUPER_ADMIN_ID: int = int(os.getenv("SUPER_ADMIN_ID", "0"))

    # Ma'lumotlar bazasi fayli
    DB_PATH: str = os.getenv("DB_PATH", "database.sqlite")


config = Config()

# Post shabloni uchun emoji va sarlavhalar
POST_TEMPLATE = (
    "🆔 <b>ID:</b> {id}\n"
    "💰 <b>Narxi:</b> {price}\n"
    "⚠️ <b>Privyazka:</b> {privyazka}\n"
    "📝 <b>Tavsif:</b>\n{description}\n\n"
    "{status_line}"
)

SOLD_LINE = "✅ <b>SOTILDI</b>"
ACTIVE_LINE = "📌 <i>Sotuvda</i>"
