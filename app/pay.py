# app/pay.py
import os
import math
import uuid

import yookassa
from yookassa import Configuration, Payment
from dotenv import load_dotenv

from app import keyboard, description
from app import referal as referal_module
from pgsql.database import user_info, del_information_about_server

load_dotenv()

Configuration.account_id = os.getenv("YOUKASSA_ACCOUNT_ID")
Configuration.secret_key = os.getenv("YOUKASSA_SECRET_KEY")


def create_payment(amount: float, description_: str):
    """Создаёт ссылку на оплату через ЮKassa. Возвращает (pay_id, url)."""
    amount = int(math.floor(amount))
    idempotence_key = str(uuid.uuid4())
    payment = Payment.create(
        {
            "amount": {"value": str(amount), "currency": "RUB"},
            "confirmation": {"type": "redirect", "return_url": "https://oblaka.tech/"},
            "capture": True,
            "description": description_,
        },
        idempotence_key,
    )
    return payment.id, payment.confirmation.confirmation_url


async def check_pay(telegram_id: int, first_name: str, username: str, pool):
    """
    Проверяет статус оплаты.
    Возвращает (text, reply_markup, is_pay, text_to_admin).
    """
    is_pay = False
    try:
        user = await user_info(telegram_id, pool)
        if not user:
            return description.error, keyboard.back_to_my_profile.as_markup(), is_pay, "no"

        pay_id = user.get("pay_id", "0")
        answer = yookassa.Payment.find_one(pay_id).status

        if answer == "succeeded":
            is_pay = True
            await referal_module.check_referal_discount(telegram_id, True, pool)
            await del_information_about_server(telegram_id, True, pool)

            # Импорт здесь чтобы избежать цикличности
            from app.admin import pay_succsses
            text_to_admin = await pay_succsses(telegram_id, first_name, username, pool)
            return description.pay_sucsses, keyboard.back_to_my_profile.as_markup(), is_pay, text_to_admin

        elif answer in ("pending", "waiting_for_capture"):
            return "⏳Ожидается оплата...⏳", keyboard.buy_from_p2pkassa(user.get("url_pay", "")), is_pay, "no"

        elif answer == "canceled":
            await del_information_about_server(telegram_id, False, pool)
            return "❌Оплата устарела и/или была отменена!❌", keyboard.back_to_my_profile.as_markup(), is_pay, "no"

        else:
            return description.error, keyboard.back_to_my_profile.as_markup(), is_pay, "no"

    except Exception:
        return description.error, keyboard.back_to_my_profile.as_markup(), is_pay, "no"