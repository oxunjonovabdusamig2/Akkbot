# Account Sotuv Boti (aiogram 3.x)

Kanallar uchun akkaunt sotuvini boshqaruvchi professional Telegram bot.

## O'rnatish

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Sozlash

`.env` faylini yarating:

```bash
cp .env.example .env
```

So'ng `.env` faylini oching va quyidagilarni to'ldiring:

- `BOT_TOKEN` — @BotFather dan olingan token
- `CHANNEL_ID` — postlar joylanadigan kanal (`@kanal_username` yoki `-100xxxxxxxxxx`)
- `SUPER_ADMIN_ID` — sizning Telegram user ID raqamingiz (masalan @userinfobot orqali bilib oling)

**Muhim:** Botni kanalga **admin** qilib qo'shishni unutmang (post yuborish, tahrirlash, pin qilish va o'chirish huquqlari bilan).

`.env` fayli `.gitignore` orqali GitHub'ga yuklanmaydi — tokeningiz xavfsiz qoladi.

## Ishga tushirish

```bash
python main.py
```

## Asosiy imkoniyatlar

| Buyruq/Tugma | Vazifasi |
|---|---|
| `/start` | Botni ishga tushirish, admin panelni ochish |
| ➕ Yangi akkaunt | Rasm → Video → Narx → Privyazka → Tavsif → Tasdiqlash → kanalga post |
| ✏️ Tahrirlash | ID orqali topib, narx/privyazka/tavsif/rasm/video ni yangilash |
| ✅ Sotildi | Postni "SOTILDI" holatiga o'tkazadi (eski post tahrirlanadi) |
| ♻️ Qayta sotuvga | Postni qayta "Sotuvda" holatiga qaytaradi |
| 📌 Pin qilish | Kanaldagi postni pin qiladi |
| 🗑 O'chirish | Post va bazadagi yozuvni o'chiradi (tasdiqlash bilan) |
| 🔎 ID bo'yicha qidirish | Akkaunt ma'lumotlarini ko'rsatadi |
| 📊 Statistika | Jami/sotuvda/sotilgan sonini ko'rsatadi |
| `/last` | So'nggi 10 ta akkauntni ro'yxat qilib beradi |
| `/addadmin <id>` | Yangi admin qo'shish |
| `/removeadmin <id>` | Adminni o'chirish |

## Tuzilma

```
account_bot/
├── main.py            # Botni ishga tushirish, routerlar, global error handler
├── config.py           # Token, kanal ID, shablon
├── database.py         # SQLite (aiosqlite) - accounts va admins jadvallari
├── keyboards.py         # Reply/Inline klaviaturalar
├── states.py           # FSM holatlari
├── models.py            # Account dataclass
├── handlers/
│   ├── start.py         # /start
│   ├── admin.py          # Statistika, admin boshqaruvi
│   ├── accounts.py        # Yangi akkaunt qo'shish FSM
│   ├── edit.py             # Tahrirlash, pin, o'chirish, qidirish
│   ├── sold.py              # Sotildi / qayta sotuvga
│   └── statistics.py        # /last va qo'shimcha hisobotlar
├── utils/
│   ├── templates.py          # Post matni shabloni
│   └── functions.py           # Kanalga post joylash/tahrirlash/pin/delete
└── database.sqlite (avtomatik yaratiladi)
```

## GitHub'ga yuklash

Loyiha ichida allaqachon git repo boshlab qo'yilgan (`git init` qilingan va birinchi commit bor).
`.env` va `database.sqlite` fayllari `.gitignore` orqali chiqarib tashlangan, shuning uchun
tokenlaringiz va bazangiz tasodifan yuklanib ketmaydi.

1. GitHub'da yangi (bo'sh) repository yarating: https://github.com/new
   (README, .gitignore, LICENSE qo'shmang — ular allaqachon loyihada bor)
2. Terminalda loyiha papkasiga kiring va remote qo'shing:

```bash
cd account_bot
git remote add origin https://github.com/FOYDALANUVCHI_NOMI/REPO_NOMI.git
git branch -M main
git push -u origin main
```

Shu bilan loyiha GitHub'ga yuklanadi. Keyingi o'zgarishlar uchun:

```bash
git add .
git commit -m "O'zgarish tavsifi"
git push
```

## Eslatmalar

- Baza SQLite bo'lib, `database.py` ichidagi SQL so'rovlarni MySQL ga moslashtirish uchun
  `aiosqlite` o'rniga `aiomysql`/`asyncmy` ishlatib, so'rovlarni deyarli o'zgarishsiz ko'chirsa bo'ladi.
- Har bir handlerda try/except va global `@dp.errors()` handler orqali botning
  kutilmagan xatolik tufayli to'xtab qolishining oldi olingan.
- Bir nechta admin `admins` jadvalida saqlanadi, `/addadmin` va `/removeadmin` orqali boshqariladi.
