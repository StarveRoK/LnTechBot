# app/referal.py
from app import description
from pgsql.database import (
    all_users,
    user_info,
    add_referal_discount,
    add_referal_discount_new_user,
    add_referal_to_user,
)


def _find_user(users: list[dict], referal_raw: str, current_id: int) -> bool:
    """Проверяет, существует ли пользователь с данным реферальным кодом."""
    referal_id = referal_raw.replace("rf", "")
    try:
        for user in users:
            if int(user["telegram_id"]) == int(referal_id) and int(user["telegram_id"]) != int(current_id):
                return True
    except Exception:
        return False
    return False


async def check_referal_discount(telegram_id: int, is_pay: bool, pool) -> None:
    """
    Проверяет наличие приглашённых пользователей, которые совершили покупку.
    При наличии — начисляет 10% скидки.
    При is_pay=True — фиксирует использованного реферала.
    """
    db = await all_users(pool)
    user = await user_info(telegram_id, pool)
    if not user:
        return

    for member in db:
        invited_by = str(member.get("inviting_user", ""))
        already_used = str(user.get("user_invited", ""))

        if (
            invited_by == str(telegram_id)
            and (member.get("purchases") or 0) > 0
            and str(member["telegram_id"]) not in already_used
        ):
            await add_referal_discount(telegram_id, pool)
            if is_pay:
                prev = member.get("user_invited", "no")
                user_invite = f"{str(member['telegram_id'])}_" if prev == "no" else f"{prev}{str(member['telegram_id'])}_"
                await add_referal_discount_new_user(telegram_id, user_invite, pool)


async def is_referal_code(txt: str, telegram_id: int, pool) -> str:
    """Обрабатывает ввод реферального кода пользователем."""
    all_users_list = await all_users(pool)
    if not _find_user(all_users_list, txt, telegram_id):
        return description.bad_referal_code
    return await add_referal_to_user(txt, telegram_id, pool)