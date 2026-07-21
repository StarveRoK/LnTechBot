"""
Одноразовый перенос пользователей из старой my_database.db (SQLite) в Postgres.

Данные образовались до перехода бота на pgsql/database.py и с тех пор нигде не
использовались, но так и не были перенесены. Скрипт идемпотентен — при повторном
запуске существующие telegram_id пропускаются (ON CONFLICT DO NOTHING), поэтому
его безопасно перезапускать.

Использование:
    alembic upgrade head            # сначала должна существовать схема
    python scripts/migrate_sqlite_users.py [путь_к_sqlite]
"""
import asyncio
import platform
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pgsql.database import AsyncDatabaseManager

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

SQLITE_COLUMNS = (
    "telegram_id", "username", "money", "oblaka", "purchases", "admin",
    "discount", "referal", "server", "price", "use_discount",
    "inviting_user", "user_invited", "pay_id", "url_pay",
)

INSERT_SQL = f"""
    INSERT INTO users ({", ".join(SQLITE_COLUMNS)})
    VALUES ({", ".join(["%s"] * len(SQLITE_COLUMNS))})
    ON CONFLICT (telegram_id) DO NOTHING
"""


def read_sqlite_users(db_path: str) -> list[tuple]:
    conn = sqlite3.connect(db_path)
    conn.text_factory = lambda b: b.decode("utf-8", errors="replace")
    try:
        cursor = conn.execute(f"SELECT {', '.join(SQLITE_COLUMNS)} FROM users")
        return cursor.fetchall()
    finally:
        conn.close()


async def main() -> None:
    sqlite_path = sys.argv[1] if len(sys.argv) > 1 else str(
        Path(__file__).resolve().parent.parent / "my_database.db"
    )
    rows = read_sqlite_users(sqlite_path)
    print(f"Прочитано из {sqlite_path}: {len(rows)} строк")

    db = AsyncDatabaseManager()
    await db.open_pool()
    try:
        inserted = 0
        async with db.pool.connection() as conn:
            async with conn.cursor() as cursor:
                for row in rows:
                    await cursor.execute(INSERT_SQL, row)
                    inserted += cursor.rowcount
            await conn.commit()
        print(f"Перенесено новых пользователей: {inserted} / {len(rows)}")
        print(f"Уже существовало (пропущено): {len(rows) - inserted}")
    finally:
        await db.close_pool()


if __name__ == "__main__":
    asyncio.run(main())
