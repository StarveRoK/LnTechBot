# app/oblaka.py
from app import description
from pgsql.database import add_new_user, user_info, add_discount_oblaka


async def oblaka(telegram_id: int, name: str, pool) -> str:
    """
    Обрабатывает ввод слова OBLAKA.
    Регистрирует пользователя если нужно, проверяет наличие купона и начисляет скидку.
    """
    await add_new_user(telegram_id, name, pool)
    user = await user_info(telegram_id, pool)

    if not user:
        return description.error

    if int(user["oblaka"]) == 1:
        await add_discount_oblaka(telegram_id, pool)
        return description.activate_coupon_string
    elif int(user["oblaka"]) == 0:
        return description.user_have_no_coupon
    else:
        return description.error