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
technical_support.button(text="Тех.поддержка (Максим)", url="https://t.me/LnTechnologies")
technical_support.button(text="Разработчик (Алексей)", url="https://t.me/StarveR")
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
buy_ = ["back_to_choosing_server"]
key_server_description = ["back_to_choose"]
s_d = description.servers
for server in description.servers:
    key_server_description.append(server)
    buy_.append("buy_"+server)
    if server == "check_kassa":
        continue
    servers.button(text=f"{s_d.get(server)[0]} {s_d.get(server)[1]} Ядра | {s_d.get(server)[2]} "
                        f"озу | 128 ssd | {s_d.get(server)[3]}P", callback_data=server)
servers.adjust(1)

admin_panel = InlineKeyboardBuilder()
admin_panel.button(text="Вывести базу данных в чат", callback_data="db_to_chat")
admin_panel.button(text="Проверить оплату", callback_data="buy_check_kassa")
admin_panel.adjust(1)
