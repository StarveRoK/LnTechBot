# app/my_profile.py
from aiogram.utils.markdown import hbold
from app import keyboard
from pgsql.database import add_new_user, user_info, del_information_about_server


def _text_my_profile(name: str, telegram_id: int, purchases: int, money: int) -> str:
    return (
        f"Профиль {hbold(name)} c айди {hbold(str(telegram_id))}\n"
        f"Всего покупок: {purchases}\n"
        f"Баланс: {money}₽"
    )


async def my_profile(telegram_id: int, name: str, pool):
    await add_new_user(telegram_id, name, pool)
    result = await user_info(telegram_id, pool)
    txt = _text_my_profile(name, telegram_id, result.get("purchases", 0), result.get("money", 0))
    return txt, keyboard.my_profile.as_markup()


async def back_to_my_profile(telegram_id: int, name: str, pool):
    await del_information_about_server(telegram_id, False, pool)
    result = await user_info(telegram_id, pool)
    txt = _text_my_profile(name, telegram_id, result.get("purchases", 0), result.get("money", 0))
    return txt, keyboard.my_profile.as_markup()