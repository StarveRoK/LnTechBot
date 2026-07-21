# pgsql/catalog.py
"""
Тарифы, локации и настройки скидок раньше были захардкожены в app/description.py
и pgsql/database.py. Теперь они хранятся в Postgres (см. alembic/versions/0002_*,
0003_*) и загружаются один раз при старте бота в main.py.
"""

# Проценты скидок по умолчанию — используются, если строка отсутствует в app_settings.
DEFAULT_APP_SETTINGS = {
    "oblaka_discount_percent": 20,
    "referal_discount_percent": 10,
}

# Заполняется в main.py при старте из load_app_settings(). Модули-потребители должны
# делать `from pgsql import catalog` и обращаться как `catalog.APP_SETTINGS[...]`,
# а не `from pgsql.catalog import APP_SETTINGS` — иначе они получат копию ссылки на
# старый (пустой) словарь и не увидят обновление, сделанное при старте.
APP_SETTINGS: dict = dict(DEFAULT_APP_SETTINGS)


async def load_tariffs(pool) -> dict:
    """
    Возвращает тарифы в виде {code: {"flag", "cores", "ram_gb", "ssd_gb", "price", "is_visible"}},
    упорядоченные как в таблице (sort_order).
    """
    async with pool.connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                """
                SELECT code, flag, cores, ram_gb, ssd_gb, price, is_visible
                FROM tariffs
                ORDER BY sort_order
                """
            )
            rows = await cursor.fetchall()

    return {
        code: {
            "flag": flag,
            "cores": cores,
            "ram_gb": ram_gb,
            "ssd_gb": ssd_gb,
            "price": price,
            "is_visible": is_visible,
        }
        for code, flag, cores, ram_gb, ssd_gb, price, is_visible in rows
    }


async def load_locations(pool) -> dict:
    """Возвращает {flag: country}."""
    async with pool.connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT flag, country FROM locations")
            rows = await cursor.fetchall()

    return {flag: country for flag, country in rows}


async def load_app_settings(pool) -> dict:
    """Возвращает настройки как {key: int(value)}, с дефолтами на случай отсутствия строки."""
    async with pool.connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT key, value FROM app_settings")
            rows = await cursor.fetchall()

    settings = dict(DEFAULT_APP_SETTINGS)
    settings.update({key: int(value) for key, value in rows})
    return settings
