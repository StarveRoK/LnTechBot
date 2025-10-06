from app import SQlite, description

# Проверка на наличие пользователя в БД, который поделился реферальным кодом
def is_user(users, referal, id):
    referal = referal.replace("rf", "")
    try:
        for user in users:
            user = list(user)
            if int(user[1]) == int(referal) and int(user[1]) != int(id): return True
    except: return False
    return False

# Проверка на наличие реферальных ссылок (есть ли приглашённые пользователи, которые приобрели сервер)
# При наличии - начисляется 10% скидки.
# При покупке - айди приглашенного пользователя заносится в бд, как "использованный"
def check_referal_discount(id, is_pay):
    db = SQlite.all_telegram_id()
    user = SQlite.user_info(id)
    for name in db:
        if str(name[12]) == str(id) and name[5] > 0 and str(name[1]) not in str(user[13]):
            SQlite.add_referal_discount(id)
            if is_pay:
                '''СТРОКИ НИЖЕ ДОЛЖНЫ ВЫПОЛНЯТЬСЯ ТОЛЬКО ПОСЛЕ ОПЛАТЫ!!!!!!!'''
                if name[13] == "no": user_invite = f"{str(name[1])}_"
                else: user_invite = f"{name[13]}{str(name[1])}_"
                SQlite.add_referal_discount_new_user(id, user_invite)

# Проверка на наличие пользователя с введеным реферальным кодом
def is_referal_code(txt, id):
    all_users = SQlite.all_telegram_id()
    is_user_ = is_user(all_users, txt, id)
    if is_user_ == False: return description.bad_referal_code
    else: return SQlite.add_referal_to_user(txt, id)
