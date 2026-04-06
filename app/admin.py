# app/admin.py
from aiogram.utils.markdown import hbold
from app import keyboard, text as text_module
from pgsql.database import all_users, user_info


def admin_panel(name: str):
    txt = f"{name} добро пожаловать в админ панель!\nВыберите интересующие вас пункты:"
    return txt, keyboard.admin_panel.as_markup()


async def db_into_message(pool) -> str:
    """Выводит краткую таблицу пользователей для админа."""
    db = await all_users(pool)
    lines = ["<pre>id | telegram_id | username | money</pre>"]
    for user in db:
        lines.append(
            f"{user.get('id')} | {user.get('telegram_id')} | "
            f"{user.get('username')} | {user.get('money')}"
        )
    return "\n".join(lines)


async def pay_succsses(telegram_id: int, first_name: str, username: str | None, pool) -> str:
    user = await user_info(telegram_id, pool)
    if not user:
        return "Ошибка: пользователь не найден"

    if username is None:
        username = "Неизвестно"

    server = user.get("server", "no")
    price = user.get("price", 0)
    use_discount = user.get("use_discount", "no")

    txt = text_module.text(server, "Оплата прошла успешно:\n")

    if use_discount == "dis":
        txt += f"\n\nОплата в размере {hbold(str(price))} руб. прошла успешно (за счёт промокода OBLAKA -20%)"
    elif use_discount == "ref":
        txt += f"\n\nОплата в размере {hbold(str(price))} руб. прошла успешно (за счёт реферальной ссылки -10%)"
    elif use_discount == "no":
        txt += f"\n\nОплата в размере {hbold(str(price))} руб. прошла успешно"
    else:
        txt += "\n\nПРОИЗОШЛА КАКАЯ-ТО ОШИБКА"

    txt += (
        f"\n\nИмя пользователя: {hbold(first_name)}"
        f"\nusername пользователя: {hbold(username)}"
        f"\nid пользователя: {hbold(str(telegram_id))}"
        f'\n\nЧтобы ответить пользователю через бот: "sendto {telegram_id} [сообщение]"'
    )

    if username == "Неизвестно":
        txt += "\n\nПользователь скрыл свои данные. Обратная связь только через бота."

    return txt


def text_to_user(txt: str):
    parts = txt.split(" ", 2)
    user_id = int(parts[1])
    message_text = parts[2] if len(parts) > 2 else ""
    reply = f"Сообщение пользователю {user_id} успешно отправлено!"
    return reply, user_id, message_text