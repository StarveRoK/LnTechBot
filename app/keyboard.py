# keyboard.py
from app import description

from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


# Функция для создания inline кнопок с определенным callback_data
def inline_keyboard_in_choose(choose, name):
    buy_server_or_back = InlineKeyboardBuilder()
    buy_server_or_back.button(text="Купить " + name, callback_data="buy_" + choose)
    buy_server_or_back.button(text="Назад", callback_data="back_to_choose")
    buy_server_or_back.adjust(1)
    choose = buy_server_or_back.as_markup()
    return choose


def buy_from_p2pkassa(url):
    buy_from = InlineKeyboardBuilder()
    buy_from.button(text="Оплатить через: Юkassa", callback_data="p2pkassa", url=url)
    buy_from.button(text="Проверить оплату", callback_data="buy")
    buy_from.button(text="Назад", callback_data="back_to_choose")
    buy_from.adjust(1)
    return buy_from.as_markup()


builder = ReplyKeyboardBuilder()
builder.button(text="🖥VDS/VPS Сервера в наличии", callback_data="set1")
builder.button(text="🎁Промокод", callback_data="set2")
builder.button(text="🙍‍♂️Мой профиль", callback_data="my_profiles")
builder.button(text="ℹ️Информация", callback_data="set4")
builder.button(text="📞Контакты", callback_data="set5")
builder.adjust(1, 3, 1)
builder.as_markup()

technical_support = InlineKeyboardBuilder()
technical_support.button(text="Тех.поддержка Ульяна", url="https://t.me/ingcod")
technical_support.button(text="Тех.поддержка Саид", url="https://t.me/ln_tech_support")
# technical_support.button(text="Тех.поддержка (Максим)", url="https://t.me/LnTechnologies")
# technical_support.button(text="Разработчик (Алексей)", url="https://t.me/StarveR")
technical_support.adjust(1)

my_profile = InlineKeyboardBuilder()
my_profile.button(text="Реферальная система", callback_data="referal_system")
my_profile.button(text="Активировать купон", callback_data="coupon")
my_profile.adjust(2)

back_to_my_profile = InlineKeyboardBuilder()
back_to_my_profile.button(text="Вернуться", callback_data="back_to_my_profile")

input_referal = InlineKeyboardBuilder()
input_referal.button(text="Ввести реферальный код", callback_data="input_referal")
input_referal.button(text="Вернуться", callback_data="back_to_my_profile")
input_referal.adjust(1)

servers = InlineKeyboardBuilder()
# "back_to_choosing_server"/"back_to_choose" — служебные callback_data, не привязаны к тарифам.
buy_ = ["back_to_choosing_server"]
key_server_description = ["back_to_choose"]


def build_server_buttons() -> None:
    """
    Строит клавиатуру серверов и списки допустимых callback_data по тарифам,
    загруженным из Postgres (description.servers, см. main.py при старте).

    ВАЖНО: main.py регистрирует `@dp.callback_query(F.data.in_(keyboard.buy_))` и
    `F.data.in_(keyboard.key_server_description))` на этапе импорта — то есть ДО того,
    как эта функция вызывается при старте бота. aiogram/magic_filter захватывает сам
    объект списка по ссылке в момент декорирования, а не его содержимое. Поэтому здесь
    списки дополняются на месте (.clear()/.append()), а НЕ пересоздаются — иначе уже
    зарегистрированные фильтры будут смотреть на старый пустой список и не сработают.
    """
    global servers

    servers = InlineKeyboardBuilder()

    del buy_[1:]
    del key_server_description[1:]

    for code, s in description.servers.items():
        key_server_description.append(code)
        buy_.append("buy_" + code)
        if not s["is_visible"]:
            continue
        servers.button(
            text=f"{s['flag']} {s['cores']} Ядра | {s['ram_gb']} "
                 f"озу | {s['ssd_gb']} ssd | {int(s['price'])}P",
            callback_data=code,
        )
    servers.adjust(1)

admin_panel = InlineKeyboardBuilder()
admin_panel.button(text="Вывести базу данных в чат", callback_data="db_to_chat")
admin_panel.button(text="Проверить оплату", callback_data="buy_check_kassa")
admin_panel.adjust(1)
