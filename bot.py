
# bot.py
import logging
import csv
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import CommandStart, Command
import os

# ENV переменные
TOKEN = "8075247657:AAEOFQGogUIITMVpndzRR_jH-ZM84NRqa4Q"
print(f"TOKEN: {repr(TOKEN)}")
MERCHANT_LOGIN = "Neyroph_bot"
PASSWORD1 = "dR07mRr4HoY8sGQb5Any"
NOTIFY_CHAT_ID = os.getenv("NOTIFY_CHAT_ID")  # ID группы для уведомлений
CHANNEL_USERNAME = "@your_channel_username"  # заменишь на свой канал

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

# CSV-файл для подписок
SUBS_FILE = "subscriptions.csv"

# --- КНОПКИ ---
def start_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Вступить в клуб", callback_data="join_club"))
    kb.add(InlineKeyboardButton("Подробнее о клубе", callback_data="club_details"))
    kb.add(InlineKeyboardButton("Правовая информация", callback_data="legal_info"))
    kb.add(InlineKeyboardButton("Управление подпиской", callback_data="manage_sub"))
    kb.add(InlineKeyboardButton("FAQ", callback_data="faq"))
    return kb

def tariff_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("1 мес — 990₽", url=generate_pay_link(990, "1 мес")))
    kb.add(InlineKeyboardButton("3 мес — 2690₽", url=generate_pay_link(2690, "3 мес")))
    kb.add(InlineKeyboardButton("6 мес — 4790₽", url=generate_pay_link(4790, "6 мес")))
    kb.add(InlineKeyboardButton("Правовая информация", callback_data="legal_info"))
    kb.add(InlineKeyboardButton("Главное меню", callback_data="main_menu"))
    return kb

# --- Генерация ссылки оплаты ---
def generate_pay_link(amount, period):
    description = f"Подписка NEYROPH на {period}"
    invoice_id = int(datetime.now().timestamp())
    import hashlib
    signature_raw = f"{MERCHANT_LOGIN}:{amount}:{invoice_id}:{PASSWORD1}"
    signature = hashlib.md5(signature_raw.encode()).hexdigest()
    link = f"https://auth.robokassa.ru/Merchant/Index.aspx?MerchantLogin={MERCHANT_LOGIN}&OutSum={amount}&InvoiceID={invoice_id}&Description={description}&SignatureValue={signature}"
    return link

# --- Хэндлеры ---
@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    await msg.answer("Ехууу, привет! 👋\n\nТы на верном пути — вступаешь в закрытый клуб NEYROPH...", reply_markup=start_keyboard())

@dp.callback_query_handler(lambda c: c.data == "join_club")
async def join_club(callback: types.CallbackQuery):
    await callback.message.answer("Выбирай срок подписки и вступай в клуб!", reply_markup=tariff_keyboard())

# --- Обработка уведомлений Робокассы (webhook) ---
from aiohttp import web

async def robokassa_callback(request):
    data = await request.post()
    user_id = data.get("InvId")  # Используем invoice id как user_id (можно заменить)
    username = data.get("shp_username", "неизвестно")
    amount = data.get("OutSum")
    period = data.get("shp_period", "-")

    end_date = (datetime.now() + timedelta(days=30 if period == "1 мес" else 90 if period == "3 мес" else 180)).date()

    # Сохраняем подписку
    with open(SUBS_FILE, "a", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([user_id, username, datetime.now().date(), end_date, period])

    # Уведомление в группу
    await bot.send_message(chat_id=NOTIFY_CHAT_ID, text=f"💳 Новая оплата от @{username}\nТариф: {period}\nСумма: {amount}₽")

    return web.Response(text="OK")

# --- Проверка подписок ---
async def check_subscriptions():
    today = datetime.now().date()
    updated_rows = []
    with open(SUBS_FILE, "r", encoding='utf-8') as f:
        for row in csv.reader(f):
            user_id, username, _, end_date_str, _ = row
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            if today > end_date:
                try:
                    await bot.ban_chat_member(CHANNEL_USERNAME, int(user_id))
                    await bot.unban_chat_member(CHANNEL_USERNAME, int(user_id))
                except Exception as e:
                    print(f"Ошибка удаления {user_id}: {e}")
            else:
                updated_rows.append(row)
    with open(SUBS_FILE, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(updated_rows)

# --- Запуск веб-сервера ---
app = web.Application()
app.router.add_post("/payment_callback", robokassa_callback)

if __name__ == "__main__":
    import asyncio
    from aiogram.utils.executor import start_polling

    async def on_startup(_):
        print("Бот запущен")

    start_polling(dp, skip_updates=True, on_startup=on_startup)
