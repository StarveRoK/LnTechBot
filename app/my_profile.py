from aiogram.utils.markdown import hbold
from app import SQlite, keyboard

# Текст для вкладки "Мой профиль"
def text_my_profile(name, id, purchases, money):
    answer = f"Профиль {hbold(name)} c айди {hbold(id)}\nВсего покупок: {purchases}\nБаланс: {money}₽"
    return answer


# Текст для вкладки "Мой профиль"
def my_profile(id, name):
    SQlite.add_new_user(id, name)
    user_info = SQlite.user_info(id)
    txt = text_my_profile(name, id, str(user_info[5]), str(user_info[3]))
    reply_markup = keyboard.my_profile.as_markup()
    return txt, reply_markup


#Возвращение в профиль со всеми данными
def back_to_my_profile(id, name):
    SQlite.del_information_about_server(id, False)
    user_info = SQlite.user_info(id)
    txt = text_my_profile(name, id, str(user_info[5]), str(user_info[3]))
    reply_markup = keyboard.my_profile.as_markup()
    return txt, reply_markup