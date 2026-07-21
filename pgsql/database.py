# pgsql/database.py
import os
from aiogram.utils.markdown import hbold
from psycopg_pool import AsyncConnectionPool

from config import DATABASE_URL, ADMIN_IDS
from logs import log


# ─────────────────────────── helpers ────────────────────────────

async def fetchone_dict(cursor):
    row = await cursor.fetchone()
    if not row:
        return None
    keys = [desc.name for desc in cursor.description]
    return dict(zip(keys, row))


async def fetchall_list(cursor):
    rows = await cursor.fetchall()
    if not rows:
        return []
    keys = [desc.name for desc in cursor.description]
    return [dict(zip(keys, row)) for row in rows]


# ─────────────────────────── pool ────────────────────────────────

class AsyncDatabaseManager:
    def __init__(self, min_size: int = 2, max_size: int = 10, num_workers: int = 20):
        self.pool = AsyncConnectionPool(
            conninfo=DATABASE_URL,
            max_size=max_size,
            min_size=min_size,
            open=False,
            num_workers=num_workers,
            max_idle=300.0,
        )

    async def open_pool(self):
        try:
            await self.pool.open()
        except Exception as e:
            log.error(f"Ошибка при открытии пула соединений: {e}")

    async def close_pool(self):
        await self.pool.close()
        log.info("Пул соединений закрыт")


# ─────────────────────────── users ───────────────────────────────

async def add_new_user(telegram_id: int, username: str, pool) -> str:
    """Регистрирует пользователя если его нет. Возвращает приветствие."""
    async with pool.connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT id FROM users WHERE telegram_id = %s",
                (telegram_id,),
            )
            if await cursor.fetchone():
                return f"Привет {hbold(username)}! Давно не виделись!"

            admin = 1 if str(telegram_id) in ADMIN_IDS else 0

            await cursor.execute(
                """
                INSERT INTO users (
                    telegram_id, username, money, oblaka, purchases, admin,
                    discount, referal, server, price, use_discount,
                    inviting_user, user_invited, pay_id, url_pay
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (telegram_id) DO NOTHING
                """,
                (telegram_id, username, 0, 1, 0, admin,
                 0, 0, "no", 0, "no", "no", "no", "0", "no"),
            )
        await conn.commit()
    return f"Привет {hbold(username)}! Приятно познакомиться!"


async def user_info(telegram_id: int, pool) -> dict | None:
    """Возвращает строку пользователя как словарь."""
    async with pool.connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM users WHERE telegram_id = %s",
                (telegram_id,),
            )
            return await fetchone_dict(cursor)


async def all_users(pool) -> list[dict]:
    """Возвращает всех пользователей списком словарей."""
    async with pool.connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT * FROM users")
            return await fetchall_list(cursor)


# ─────────────────────────── обновления ──────────────────────────

async def add_discount_oblaka(telegram_id: int, percent: int, pool) -> None:
    """Списывает купон OBLAKA и выдаёт скидку (процент из app_settings, см. pgsql/catalog.py)."""
    async with pool.connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "UPDATE users SET oblaka = 0, discount = %s WHERE telegram_id = %s",
                (percent, telegram_id),
            )
        await conn.commit()


async def server_choosing(
    use_discount: str,
    price: float,
    server: str,
    telegram_id: int,
    pay_id: str,
    url_pay: str,
    pool,
) -> None:
    """Сохраняет выбранный сервер и ссылку на оплату."""
    async with pool.connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                """
                UPDATE users
                SET server = %s, price = %s, use_discount = %s,
                    pay_id = %s, url_pay = %s
                WHERE telegram_id = %s
                """,
                (server, price, use_discount, pay_id, url_pay, telegram_id),
            )
        await conn.commit()


async def add_referal_to_user(inviting_user_raw: str, telegram_id: int, pool) -> str:
    """Привязывает реферальный код к пользователю (только один раз)."""
    inviting_user = inviting_user_raw.replace("rf", "")
    async with pool.connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT inviting_user FROM users WHERE telegram_id = %s",
                (telegram_id,),
            )
            row = await cursor.fetchone()
            if row and row[0] != "no":
                return f"Вы уже активировали реферальный код! (rf{row[0]})"

            await cursor.execute(
                "UPDATE users SET inviting_user = %s WHERE telegram_id = %s",
                (inviting_user, telegram_id),
            )
        await conn.commit()
    return f"Вы успешно активировали реферальный код! (rf{inviting_user})"


async def add_referal_discount(telegram_id: int, percent: int, pool) -> None:
    """Устанавливает реферальную скидку (процент из app_settings, см. pgsql/catalog.py)."""
    async with pool.connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "UPDATE users SET referal = %s WHERE telegram_id = %s",
                (percent, telegram_id),
            )
        await conn.commit()


async def add_referal_discount_new_user(telegram_id: int, user_invite: str, pool) -> None:
    """Помечает приглашённого пользователя как «уже использованного»."""
    async with pool.connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "UPDATE users SET user_invited = %s WHERE telegram_id = %s",
                (user_invite, telegram_id),
            )
        await conn.commit()


async def del_information_about_server(telegram_id: int, is_pay: bool, pool) -> None:
    """
    Очищает данные о выбранном сервере.
    При is_pay=True — увеличивает счётчик покупок и сбрасывает скидку.
    """
    async with pool.connection() as conn:
        async with conn.cursor() as cursor:
            if is_pay:
                await cursor.execute(
                    "SELECT purchases, use_discount FROM users WHERE telegram_id = %s",
                    (telegram_id,),
                )
                row = await cursor.fetchone()
                purchases = (row[0] or 0) + 1
                use_discount = row[1] if row else "no"

                if use_discount == "ref":
                    await cursor.execute(
                        """
                        UPDATE users
                        SET purchases = %s, referal = 0,
                            server = 'no', price = 0, use_discount = 'no',
                            pay_id = '0', url_pay = 'no'
                        WHERE telegram_id = %s
                        """,
                        (purchases, telegram_id),
                    )
                elif use_discount == "dis":
                    await cursor.execute(
                        """
                        UPDATE users
                        SET purchases = %s, discount = 0,
                            server = 'no', price = 0, use_discount = 'no',
                            pay_id = '0', url_pay = 'no'
                        WHERE telegram_id = %s
                        """,
                        (purchases, telegram_id),
                    )
                else:
                    await cursor.execute(
                        """
                        UPDATE users
                        SET purchases = %s,
                            server = 'no', price = 0, use_discount = 'no',
                            pay_id = '0', url_pay = 'no'
                        WHERE telegram_id = %s
                        """,
                        (purchases, telegram_id),
                    )
            else:
                await cursor.execute(
                    """
                    UPDATE users
                    SET server = 'no', price = 0,
                        pay_id = '0', url_pay = 'no'
                    WHERE telegram_id = %s
                    """,
                    (telegram_id,),
                )
        await conn.commit()


# ─────────────────────────── exports ─────────────────────────────

__all__ = [
    "fetchone_dict",
    "fetchall_list",
    "AsyncDatabaseManager",
    "add_new_user",
    "user_info",
    "all_users",
    "add_discount_oblaka",
    "server_choosing",
    "add_referal_to_user",
    "add_referal_discount",
    "add_referal_discount_new_user",
    "del_information_about_server",
]