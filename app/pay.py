# app/pay.py
import os
import math
import uuid

import yookassa
from yookassa import Configuration, Payment
from yookassa.domain.exceptions import (
    ApiError,
    BadRequestError,
    ForbiddenError,
    GoneError,
    InternalServerError,
    NotFoundError,
    ResponseProcessingError,
    TooManyRequestsError,
    UnauthorizedError,
)
from dotenv import load_dotenv

from app import keyboard, description
from app import referal as referal_module
from pgsql.database import user_info, del_information_about_server
from logs import log

load_dotenv()

Configuration.account_id = os.getenv("YOUKASSA_ACCOUNT_ID")
Configuration.secret_key = os.getenv("YOUKASSA_SECRET_KEY")


def _describe_api_error(e: ApiError) -> str:
    """Достаёт code/description/id из тела ошибки ЮKassa для логов."""
    err = e.error
    if err is None:
        return str(e.content)
    return f"code={err.code}, description={err.description}, id={err.id}"


def create_payment(amount: float, description_: str):
    """
    Создаёт ссылку на оплату через ЮKassa.
    Возвращает (pay_id, url) при успехе, либо ("error", "error") при любой ошибке
    (см. https://yookassa.ru/developers/using-api/response-handling/http-codes).
    """
    amount = int(math.floor(amount))
    idempotence_key = str(uuid.uuid4())
    try:
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

    except (UnauthorizedError, ForbiddenError) as e:
        # 401/403: неверные или недостаточные учётные данные магазина — требует ручного вмешательства.
        log.critical(f"ЮKassa: проблема с доступом при создании платежа ({_describe_api_error(e)})")
    except BadRequestError as e:
        log.error(f"ЮKassa: некорректный запрос на создание платежа ({_describe_api_error(e)})")
    except TooManyRequestsError as e:
        log.warning(f"ЮKassa: превышен лимит запросов при создании платежа ({_describe_api_error(e)})")
    except (NotFoundError, GoneError) as e:
        log.error(f"ЮKassa: ресурс недоступен при создании платежа ({_describe_api_error(e)})")
    except (InternalServerError, ResponseProcessingError) as e:
        # 500/202: результат неизвестен на стороне ЮKassa, но с новым idempotence_key
        # безопасный retry всё равно создаст новый платёж — просто просим пользователя повторить покупку.
        log.error(f"ЮKassa: техническая проблема на стороне ЮKassa при создании платежа ({_describe_api_error(e)})")
    except ApiError as e:
        log.error(f"ЮKassa: неожиданная ошибка API при создании платежа ({_describe_api_error(e)})")
    except Exception as e:
        log.error(f"ЮKassa: не удалось связаться с сервером при создании платежа: {e}")

    return "error", "error"


async def check_pay(telegram_id: int, first_name: str, username: str, pool):
    """
    Проверяет статус оплаты.
    Возвращает (text, reply_markup, is_pay, text_to_admin).
    """
    is_pay = False
    try:
        user = await user_info(telegram_id, pool)
        if not user:
            return description.error_check_pay, keyboard.back_to_my_profile.as_markup(), is_pay, "no"

        pay_id = user.get("pay_id", "0")

        try:
            answer = yookassa.Payment.find_one(pay_id).status
        except (UnauthorizedError, ForbiddenError) as e:
            # 401/403: неверные или недостаточные учётные данные магазина — критично, чинить руками.
            log.critical(
                f"ЮKassa: проблема с доступом при проверке оплаты telegram_id={telegram_id} ({_describe_api_error(e)})"
            )
            return description.error_check_pay, keyboard.back_to_my_profile.as_markup(), is_pay, "no"
        except (NotFoundError, GoneError) as e:
            # pay_id отсутствует/невалиден (например дефолтное "0") или платёж удалён у ЮKassa.
            log.warning(
                f"ЮKassa: платёж не найден при проверке для telegram_id={telegram_id} ({_describe_api_error(e)})"
            )
            return description.error_check_pay, keyboard.back_to_my_profile.as_markup(), is_pay, "no"
        except TooManyRequestsError as e:
            log.warning(
                f"ЮKassa: превышен лимит запросов при проверке оплаты telegram_id={telegram_id} ({_describe_api_error(e)})"
            )
            return (
                "⏳Слишком много запросов, попробуйте проверить оплату через несколько секунд⏳",
                keyboard.buy_from_p2pkassa(user.get("url_pay", "")),
                is_pay,
                "no",
            )
        except (InternalServerError, ResponseProcessingError) as e:
            log.error(
                f"ЮKassa: техническая проблема на стороне ЮKassa при проверке оплаты telegram_id={telegram_id} "
                f"({_describe_api_error(e)})"
            )
            return (
                "⏳Не удалось уточнить статус оплаты, попробуйте ещё раз чуть позже⏳",
                keyboard.buy_from_p2pkassa(user.get("url_pay", "")),
                is_pay,
                "no",
            )
        except BadRequestError as e:
            log.error(
                f"ЮKassa: некорректный запрос при проверке оплаты telegram_id={telegram_id} ({_describe_api_error(e)})"
            )
            return description.error_check_pay, keyboard.back_to_my_profile.as_markup(), is_pay, "no"
        except ApiError as e:
            log.error(
                f"ЮKassa: неожиданная ошибка API при проверке оплаты telegram_id={telegram_id} ({_describe_api_error(e)})"
            )
            return description.error_check_pay, keyboard.back_to_my_profile.as_markup(), is_pay, "no"

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
            return description.error_check_pay, keyboard.back_to_my_profile.as_markup(), is_pay, "no"

    except Exception as e:
        log.error(f"Ошибка проверки оплаты для telegram_id={telegram_id}: {e}")
        return description.error_check_pay, keyboard.back_to_my_profile.as_markup(), is_pay, "no"