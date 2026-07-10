import aiosqlite
from datetime import datetime
from typing import Optional, List

from config import config
from models import Account


CREATE_ACCOUNTS_TABLE = """
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    price TEXT NOT NULL,
    privyazka TEXT NOT NULL,
    description TEXT NOT NULL,
    photo_id TEXT,
    video_id TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    message_id INTEGER,
    created_at TEXT NOT NULL,
    created_by INTEGER NOT NULL
)
"""

CREATE_ADMINS_TABLE = """
CREATE TABLE IF NOT EXISTS admins (
    user_id INTEGER PRIMARY KEY,
    added_by INTEGER,
    added_at TEXT
)
"""


class Database:
    def __init__(self, path: str = config.DB_PATH):
        self.path = path

    async def init(self):
        async with aiosqlite.connect(self.path) as db:
            await db.execute(CREATE_ACCOUNTS_TABLE)
            await db.execute(CREATE_ADMINS_TABLE)
            await db.commit()
            # Super adminni bazaga qo'shib qo'yamiz
            if config.SUPER_ADMIN_ID:
                await db.execute(
                    "INSERT OR IGNORE INTO admins (user_id, added_by, added_at) VALUES (?, ?, ?)",
                    (config.SUPER_ADMIN_ID, config.SUPER_ADMIN_ID, datetime.now().isoformat()),
                )
                await db.commit()

    # ---------------- ACCOUNTS ----------------

    async def add_account(
        self,
        price: str,
        privyazka: str,
        description: str,
        photo_id: Optional[str],
        video_id: Optional[str],
        created_by: int,
    ) -> int:
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute(
                """INSERT INTO accounts
                   (price, privyazka, description, photo_id, video_id, status, created_at, created_by)
                   VALUES (?, ?, ?, ?, ?, 'active', ?, ?)""",
                (price, privyazka, description, photo_id, video_id, datetime.now().isoformat(), created_by),
            )
            await db.commit()
            return cursor.lastrowid

    async def set_message_id(self, account_id: int, message_id: int):
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "UPDATE accounts SET message_id = ? WHERE id = ?", (message_id, account_id)
            )
            await db.commit()

    async def get_account(self, account_id: int) -> Optional[Account]:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
            row = await cursor.fetchone()
            if row is None:
                return None
            return Account(**dict(row))

    async def update_field(self, account_id: int, field: str, value: str):
        allowed = {"price", "privyazka", "description", "photo_id", "video_id", "status"}
        if field not in allowed:
            raise ValueError(f"Ruxsat etilmagan maydon: {field}")
        async with aiosqlite.connect(self.path) as db:
            await db.execute(f"UPDATE accounts SET {field} = ? WHERE id = ?", (value, account_id))
            await db.commit()

    async def delete_account(self, account_id: int):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
            await db.commit()

    async def list_accounts(self, status: Optional[str] = None) -> List[Account]:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            if status:
                cursor = await db.execute(
                    "SELECT * FROM accounts WHERE status = ? ORDER BY id DESC", (status,)
                )
            else:
                cursor = await db.execute("SELECT * FROM accounts ORDER BY id DESC")
            rows = await cursor.fetchall()
            return [Account(**dict(row)) for row in rows]

    async def stats(self) -> dict:
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM accounts")
            total = (await cursor.fetchone())[0]
            cursor = await db.execute("SELECT COUNT(*) FROM accounts WHERE status = 'sold'")
            sold = (await cursor.fetchone())[0]
            cursor = await db.execute("SELECT COUNT(*) FROM accounts WHERE status = 'active'")
            active = (await cursor.fetchone())[0]
            return {"total": total, "sold": sold, "active": active}

    # ---------------- ADMINS ----------------

    async def add_admin(self, user_id: int, added_by: int):
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO admins (user_id, added_by, added_at) VALUES (?, ?, ?)",
                (user_id, added_by, datetime.now().isoformat()),
            )
            await db.commit()

    async def remove_admin(self, user_id: int):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
            await db.commit()

    async def is_admin(self, user_id: int) -> bool:
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute("SELECT 1 FROM admins WHERE user_id = ?", (user_id,))
            row = await cursor.fetchone()
            return row is not None

    async def list_admins(self) -> List[int]:
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute("SELECT user_id FROM admins")
            rows = await cursor.fetchall()
            return [row[0] for row in rows]


db = Database()
