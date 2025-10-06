from app import SQlite, description

#Выполняется при ввода слова OBLAKA пользователем
#Проверка зарегистрирован ли пользователь
# Проверка на наличие купона OBLAKA в БД. При наличии - начисление скидки (20%) и удаление купона
def oblaka(id, name):
    SQlite.add_new_user(id, name)
    user_info = SQlite.user_info(id)
    if int(user_info[4]) == 1: #Проверка в БД на наличие купона
        SQlite.add_discount_oblaka(id)
        txt = description.activate_coupon_string
    elif int(user_info[4]) == 0: txt = description.user_have_no_coupon
    else: txt = description.error
    return txt