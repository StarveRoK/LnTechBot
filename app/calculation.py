from app import SQlite, text, description, keyboard, referal, pay
from aiogram.utils.markdown import hbold

"""------------------------------<<<ФУНКЦИИ ДЛЯ РАСЧЕТА>>>------------------------------"""


# Подробная информация о сервере
def information_about_server(choose, id_):
    if choose == "back_to_choose":
        tex = description.set_1
        reply_markup = keyboard.servers.as_markup()
        SQlite.del_information_about_server(id_, False)
        return tex, reply_markup
    buy_serv = text.buy_server(choose)
    tex = text.text(choose, buy_serv)
    reply_markup = keyboard.inline_keyboard_in_choose(choose, buy_serv)
    return tex, reply_markup


# Сбор информации о выбранном сервере
# Определение окончательной цены сервера (есть ли скидки или нет)
# Создание ссылки на оплату
# При нажатии "назад" все данные о выбранном сервере удаляются
def buy_or_back(data, id_):

    if data == "back_to_choosing_server":  # Если пользователь нажмет "назад"
        txt = description.set_1
        reply_markup = keyboard.servers.as_markup()
        SQlite.del_information_about_server(id_, False)
        return txt, reply_markup

    server_choose, discount = data.replace("buy_", ""), "no"  # Определение переменных
    user_info = SQlite.user_info(id_)  # Определение пользователя в бд
    price = int((description.servers.get(server_choose))[3])  # Получение цены выбранного сервера
    referal.check_referal_discount(id_, False)  # Проверка на наличие реферальной скидки

    if int(user_info[7]) > 0 or int(user_info[8]) > 0:  # Определение наличия скидки и какая из них больше
        discount = max(int(user_info[7]), int(user_info[8]))
        price = price - (price * (discount/100))
        if int(user_info[7]) > int(user_info[8]):
            discount = "dis"
        else:
            discount = "ref"

    txt = text.text(server_choose, "")  # Создание текста
    pay_id, url = pay.pay(price, text.text_to_p2pkassa(server_choose))  # Создание ссылки на оплату
    SQlite.server_choosing(discount, price, server_choose, id_, pay_id, url)  # Заполнение бд выбранным сервером

    if url == "error":
        return description.error, keyboard.back_to_my_profile.as_markup()  # Если оплата не создана
    txt = f"Вы выбрали: \n{txt}\n\nОкончательная цена: {hbold(str(price))}Р"  # Создание текста сообщения
    reply_markup = keyboard.buy_from_p2pkassa(url)  # Определение inline кнопок
    return txt, reply_markup
