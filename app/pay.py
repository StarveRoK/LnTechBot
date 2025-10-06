import os

import yookassa

from app import referal, SQlite, keyboard, description, admin
from dotenv import load_dotenv
import math
import uuid
from yookassa import Configuration, Payment

load_dotenv()

Configuration.account_id = os.getenv('YOUKASSA_ACCOUNT_ID')
Configuration.secret_key = os.getenv("YOUKASSA_SECRET_KEY")


# Создание ссылки на оплату
def pay(amount, description_):
    amount = int(math.floor(amount))  # Сумма денег

    idempotence_key = str(uuid.uuid4())

    payment = Payment.create({
        "amount": {
            "value": str(amount),
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://oblaka.tech/"
        },
        "capture": True,
        "description": description_
    }, idempotence_key)

    return payment.id, payment.confirmation.confirmation_url


# Проверка оплаты (ожидание, отмена, подтверждение)
def check_pay(id_, first_name, username):
    is_pay = False
    try:
        user_info_db = SQlite.user_info(id_)
        id_pay = user_info_db[14]
        answer = yookassa.Payment.find_one(id_pay).status
        if answer == "succeeded":
            is_pay = True
            txt = description.pay_sucsses
            txt_to_admin = admin.pay_succsses(id_, first_name, username)
            referal.check_referal_discount(id_, True)
            SQlite.del_information_about_server(id_, True)
            return txt, keyboard.back_to_my_profile.as_markup(), is_pay, txt_to_admin
            # '''ТУТ ДОЛЖЕН БЫТЬ КОД С ОТПРАВКОЙ ЛОГИНА И ПАРОЛЯ'''

        elif answer == "pending" or answer == "waiting_for_capture":
            return "⏳Ожидается оплата...⏳", keyboard.buy_from_p2pkassa(user_info_db[15]), is_pay, "no"
        elif answer == "canceled":
            SQlite.del_information_about_server(id_, False)
            return "❌Оплата устарела и/или была отменена!❌", keyboard.back_to_my_profile.as_markup(), is_pay, "no"
        else:
            return description.error, keyboard.back_to_my_profile.as_markup(), is_pay, "no"
    except Exception:
        return description.error, keyboard.back_to_my_profile.as_markup(), is_pay, "no"
