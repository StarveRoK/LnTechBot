# main.py
import asyncio
import logging
import platform
import sys

from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from config import ADMIN_IDS, MAX_ADMIN, TOKEN, PROXY
from middleware import DatabaseMiddleware
from pgsql.database import AsyncDatabaseManager, add_new_user
from pgsql import catalog
from logs import log
from app import keyboard, description, pay, my_profile, admin, referal, oblaka, calculation

dp = Dispatcher()

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

database_manager = AsyncDatabaseManager()

# ──────────────────────── команды ────────────────────────────────

@dp.message(CommandStart())
async def command_start_handler(message: Message, pool=None):
    text = await add_new_user(message.from_user.id, message.from_user.full_name, pool)
    await message.answer(text, reply_markup=keyboard.builder.as_markup(resize_keyboard=True))


@dp.message(Command("admin"))
async def admin_panel(message: Message, pool=None):
    if str(message.from_user.id) in ADMIN_IDS.split(' '):
        text, reply_markup = admin.admin_panel(message.from_user.first_name)
        await message.answer(text, reply_markup=reply_markup)
    else:
        await message.reply("Я не понимаю тебя")

# ──────────────────────── reply-кнопки ───────────────────────────

@dp.message(F.text == "🖥VDS/VPS Сервера в наличии")
async def open_all_servers(message: types.Message, pool=None):
    await add_new_user(message.from_user.id, message.from_user.first_name, pool)
    await message.answer(description.set_1, reply_markup=keyboard.servers.as_markup())


@dp.message(F.text == "🎁Промокод")
async def info_promocode(message: types.Message, pool=None):
    await message.answer(description.set_2)


@dp.message(F.text == "🙍‍♂️Мой профиль")
async def my_profile_(message: types.Message, pool=None):
    text, reply_markup = await my_profile.my_profile(message.from_user.id, message.from_user.first_name, pool)
    await message.answer(text, reply_markup=reply_markup)


@dp.message(F.text == "ℹ️Информация")
async def information(message: types.Message, pool=None):
    await message.answer(description.set_4)


@dp.message(F.text == "📞Контакты")
async def contacts(message: types.Message, pool=None):
    await message.answer(description.set_5, reply_markup=keyboard.technical_support.as_markup())


@dp.message(F.text == "OBLAKA")
async def oblaka_(message: types.Message, pool=None):
    text = await oblaka.oblaka(message.from_user.id, message.from_user.first_name, pool)
    await message.answer(text)


@dp.message()
async def unexpected_message(message: types.Message, pool=None):
    if "rf" in message.text:
        await message.answer(text=await referal.is_referal_code(message.text, message.from_user.id, pool))
    elif "sendto" in message.text:
        if str(message.from_user.id) in ADMIN_IDS.split(' '):
            text, user_id, text_to_user = admin.text_to_user(message.text)
            try:
                await bot.send_message(chat_id=user_id, text=text_to_user)
                await message.answer(text=text)
            except Exception:
                await message.answer(text=description.error_send_message_to_user)
        else:
            await message.reply("Я не понимаю тебя")
    else:
        await message.reply("Я не понимаю тебя")

# ──────────────────────── inline-кнопки ──────────────────────────

@dp.callback_query(F.data.in_(keyboard.key_server_description))
async def callback_one_server(callback_query: types.CallbackQuery, pool=None):
    text, reply_markup = calculation.information_about_server(callback_query.data, callback_query.from_user.id)
    await callback_query.message.edit_text(text=text, reply_markup=reply_markup)


@dp.callback_query(F.data.in_(keyboard.buy_))
async def callback_buy_or_back(callback_query: types.CallbackQuery, pool=None):
    text, reply_markup = await calculation.buy_or_back(callback_query.data, callback_query.from_user.id, pool)
    await callback_query.message.edit_text(text=text, reply_markup=reply_markup)


@dp.callback_query(F.data == "input_referal")
async def callback_referal_code(callback_query: types.CallbackQuery, pool=None):
    await callback_query.message.edit_text(
        text=description.input_referal,
        reply_markup=keyboard.back_to_my_profile.as_markup(),
    )


@dp.callback_query(F.data == "buy")
async def callback_check_pay_(callback_query: types.CallbackQuery, pool=None):
    text, reply_markup, is_pay, text_to_admin = await pay.check_pay(
        callback_query.from_user.id,
        callback_query.from_user.first_name,
        callback_query.from_user.username,
        pool,
    )
    if is_pay:
        await bot.send_message(int(MAX_ADMIN), text=text_to_admin)
        await callback_query.message.edit_text(text=text, reply_markup=reply_markup)
    else:
        try:
            await callback_query.message.edit_text(text=text, reply_markup=reply_markup)
        except Exception:
            pass


@dp.callback_query(F.data == "back_to_my_profile")
async def callback_back_to_my_profile(callback_query: types.CallbackQuery, pool=None):
    text, reply_markup = await my_profile.back_to_my_profile(
        callback_query.from_user.id, callback_query.from_user.first_name, pool
    )
    await callback_query.message.edit_text(text=text, reply_markup=reply_markup)


@dp.callback_query(F.data == "referal_system")
async def callback_referal_system(callback_query: types.CallbackQuery, pool=None):
    text = description.referal + f"\n\nВаш реферальный код: rf{hbold(str(callback_query.from_user.id))}"
    await callback_query.message.edit_text(text=text, reply_markup=keyboard.input_referal.as_markup())


@dp.callback_query(F.data == "coupon")
async def callback_activate_coupon(callback_query: types.CallbackQuery, pool=None):
    await callback_query.message.edit_text(
        text=description.set_3,
        reply_markup=keyboard.back_to_my_profile.as_markup(),
    )


@dp.callback_query(F.data == "db_to_chat")
async def callback_admin_button(callback_query: types.CallbackQuery, pool=None):
    text = await admin.db_into_message(pool)
    await callback_query.message.edit_text(text=text)


@dp.callback_query()
async def callback_unexpected(callback_query: types.CallbackQuery, pool=None):
    await callback_query.message.edit_text(
        text=description.error,
        reply_markup=keyboard.back_to_my_profile.as_markup(),
    )

# ──────────────────────── запуск ─────────────────────────────────

async def main():

    try:
        global bot
        bot = Bot(
            TOKEN,
            default=DefaultBotProperties(parse_mode="HTML"),
            session=AiohttpSession(proxy=PROXY)
        )
        log.info("🚀 Starting up...")

        try:
            await database_manager.open_pool()
            if not database_manager.pool:
                raise Exception("Failed to create connection pool")
            dp.message.middleware(DatabaseMiddleware(database_manager.pool))
            dp.callback_query.middleware(DatabaseMiddleware(database_manager.pool))
            log.info("✅ Database pool initialized")
        except Exception as e:
            log.error(f"❌ Failed to initialize database: {e}")
            return

        # Тарифы, локации и проценты скидок теперь живут в Postgres (см. pgsql/catalog.py)
        # вместо хардкода в app/description.py. Загружаются один раз при старте.
        description.servers = await catalog.load_tariffs(database_manager.pool)
        description.location = await catalog.load_locations(database_manager.pool)
        catalog.APP_SETTINGS.update(await catalog.load_app_settings(database_manager.pool))
        keyboard.build_server_buttons()
        log.info(f"✅ Catalog loaded: {len(description.servers)} tariffs")

        await dp.start_polling(bot)

    finally:
        await database_manager.close_pool()
        log.info("✅ Database pool closed")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())