# app/calculation.py
from aiogram.utils.markdown import hbold
from app import text as text_module, description, keyboard
from app import referal as referal_module
from app import pay as pay_module
from pgsql.database import user_info, del_information_about_server, server_choosing


def information_about_server(choose: str, telegram_id: int, pool=None):
    """
    Возвращает (text, reply_markup) для выбранного сервера.
    При choose == 'back_to_choose' — сбрасывает выбор (синхронная версия не нужна, см. ниже).
    """
    if choose == "back_to_choose":
        return description.set_1, keyboard.servers.as_markup()

    buy_serv = text_module.buy_server(choose)
    tex = text_module.text(choose, buy_serv)
    reply_markup = keyboard.inline_keyboard_in_choose(choose, buy_serv)
    return tex, reply_markup


async def buy_or_back(data: str, telegram_id: int, pool):
    """Обрабатывает нажатие «Купить» или «Назад»."""
    if data == "back_to_choosing_server":
        await del_information_about_server(telegram_id, False, pool)
        return description.set_1, keyboard.servers.as_markup()

    server_choose = data.replace("buy_", "")
    user_data = await user_info(telegram_id, pool)
    price = int((description.servers.get(server_choose))[3])
    use_discount = "no"

    await referal_module.check_referal_discount(telegram_id, False, pool)

    # Пересчитываем user_data после проверки реферала
    user_data = await user_info(telegram_id, pool)
    discount_val = int(user_data.get("discount") or 0)
    referal_val = int(user_data.get("referal") or 0)

    if discount_val > 0 or referal_val > 0:
        best = max(discount_val, referal_val)
        price = price - (price * (best / 100))
        use_discount = "dis" if discount_val >= referal_val else "ref"

    pay_id, url = pay_module.create_payment(price, text_module.text_to_p2pkassa(server_choose))

    if url == "error":
        return description.error, keyboard.back_to_my_profile.as_markup()

    await server_choosing(use_discount, price, server_choose, telegram_id, pay_id, url, pool)

    txt = text_module.text(server_choose, "")
    txt = f"Вы выбрали:\n{txt}\n\nОкончательная цена: {hbold(str(int(price)))}Р"
    reply_markup = keyboard.buy_from_p2pkassa(url)
    return txt, reply_markup