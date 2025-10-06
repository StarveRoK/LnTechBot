from app import keyboard, SQlite, text
from aiogram.utils.markdown import hbold

# Отклик на команду /admin
def admin_panel(name):
    txt = f"{name} добро пожаловать в админ панель!\nВыберите интересующие вас пункты:"
    reply_markup = keyboard.admin_panel.as_markup()
    return txt, reply_markup

# БД для админа
def db_into_message():
    db = SQlite.all_telegram_id()
    message = "id | telegram_id | username | money \n"
    for user in db:
        x=0
        while x!=4:
            message += f" {str(user[x])} |"
            x+=1
        message += "\n"
    return message

def pay_succsses(id, first_name, username):
    user_info_db = SQlite.user_info(id)
    if username == None: username = "Неизвестно"
    txt = text.text(user_info_db[9], "Оплата прошла успешно:\n")
    if user_info_db[11] == "dis": txt += f"\n\nОплата в размере {hbold(str(user_info_db[10]))} руб. прошла успешна (за счет промокода OBLAKA -20%)"
    elif user_info_db[11] == "ref": txt += f"\n\nОплата в размере {hbold(str(user_info_db[10]))} руб. прошла успешна (за счет реферальной ссылки -10%)"
    elif user_info_db[11] == "no": txt += f"\n\nОплата в размере {hbold(str(user_info_db[10]))} руб. прошла успешна"
    else: txt += f"\n\nПРОИЗОШЛА КАКАЯ-ТО ОШИБКА"
    txt += f"\n\nИмя пользователя: {hbold(first_name)}\nusername пользователя: {hbold(username)}\nid пользователя: {hbold(str(id))}"
    txt += f"\n\nЧто-бы ответить пользователю через бот, напишите в чат \"sendto [id] [message]\" (sendto 123456789 Hello user) или напишите лично @{username}"
    if username == "Неизвестно": txt += "\n\nПользователь скрыл свои данные. Обратная связь возможна только через бота \"sendto [id] [message]\""
    return txt

def text_to_user(txt):
    txt = txt.split(' ')
    text = f"Сообщение пользователю {str(txt[1])} успешно отправлено!"
    user_id = int(txt[1])
    text_to_user_ = ""
    for word in txt:
        if word == txt[0] or word == txt[1]: text_to_user_ = ""
        else: text_to_user_ += word + " "
    return text, user_id, text_to_user_




