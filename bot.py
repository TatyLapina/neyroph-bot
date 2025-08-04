import logging
import csv
import os
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

TOKEN = os.getenv("TOKEN") or "8075247657:AAEOFQGogUIITMVpndzRR_jH-ZM84NRqa4Q"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import hashlib
import csv
import os
from datetime import datetime, timedelta
from asyncio import sleep

GROUP_ID = -1000000000000  # ← замени на ID своей группы "Оплаты"
CHANNEL_ID = -1000000000000  # ← замени на ID закрытого клуба
CSV_FILE = "subscriptions.csv"
ROBOKASSA_MERCHANT_LOGIN = "Neyroph_bot"
ROBOKASSA_PASSWORD_1 = "dR07mRr4HoY8sGQb5Any"

@dp.callback_query_handler(lambda c: c.data == 'agree')
async def agree_handler(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("👤 Создание персонажей", callback_data="create_characters"),
        InlineKeyboardButton("🔒 Вступить в закрытый клуб", callback_data="join_club")
    )
    text = (
        "Привет! Мы Таня и Костя — основатели студии NEYROPH 🎥📸\n\n"
        "Мы умеем делать классный визуал с помощью нейросетей и делаем так, чтобы это умел каждый!\n\n"
        "Выбирай, с чего начнём 👇"
    )
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text=text,
                                reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == 'create_characters')
async def create_characters_handler(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("✍️ Записаться на обучение", url="https://ai-avatar.ru/learning"),
        InlineKeyboardButton("📩 Написать в личные", url="https://t.me/ManagerNeyroph"),
        InlineKeyboardButton("⬅️ В главное меню", callback_data="back_to_main")
    )
    await bot.send_video(callback_query.from_user.id, open("lesson_placeholder.mp4", "rb"))
    await bot.send_message(callback_query.from_user.id,
                           "Это вводный урок — я рассказываю тут про то, как создаются персонажи, на что обращать внимание и как всё устроено.",
                           reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == 'join_club')
async def join_club_handler(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("📅 1 мес — 990₽", callback_data="pay_1"),
        InlineKeyboardButton("📅 3 мес — 2690₽", callback_data="pay_3"),
        InlineKeyboardButton("📅 6 мес — 4790₽", callback_data="pay_6"),
        InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")
    )
    text = (
        "NEYROPH — это закрытый клуб для тех, кто работает с генерацией изображений и видео с помощью нейросетей.\n\n"
        "🎓 Для новичков: гайды, шаблоны, видеоуроки\n"
        "🚀 Для опытных: стили, LoRA, видео, GPT-ассистенты\n"
        "💬 Комьюнити: активный чат, поддержка\n"
        "📦 Плюс: эксклюзив, вдохновение, мини-курсы\n\n"
        "Оплачивая, вы принимаете оферту и согласны на списания."
    )
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text=text,
                                reply_markup=keyboard)
@dp.callback_query_handler(lambda c: c.data == 'disagree')
async def disagree_handler(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Жаль 😔 Если передумаешь — просто снова нажми /start.")

# запуск
if __name__ == "__main__":
    from aiogram import executor

async def on_startup(dispatcher):
    from asyncio import create_task
    create_task(scheduler())

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
    
@dp.callback_query_handler(lambda c: c.data == 'back_to_main')
async def back_to_main(callback_query: types.CallbackQuery):
    await start_handler(callback_query.message)
def generate_payment_url(user_id: int, months: int, amount: int) -> str:
    inv_id = int(datetime.now().timestamp())
    description = f"NEYROPH: {months} мес"
    signature = f"{ROBOKASSA_MERCHANT_LOGIN}:{amount}:{inv_id}:{ROBOKASSA_PASSWORD_1}"
    crc = hashlib.md5(signature.encode()).hexdigest()
    return (
        f"https://auth.robokassa.ru/Merchant/Index.aspx?"
        f"MerchantLogin={ROBOKASSA_MERCHANT_LOGIN}&"
        f"InvId={inv_id}&OutSum={amount}&Description={description}&"
        f"Email={user_id}@tg.com&SignatureValue={crc}&IsTest=1"
    )

@dp.callback_query_handler(lambda c: c.data.startswith("pay_"))
async def handle_payment(callback_query: types.CallbackQuery):
    plans = {"pay_1": (1, 990), "pay_3": (3, 2690), "pay_6": (6, 4790)}
    months, price = plans[callback_query.data]
    url = generate_payment_url(callback_query.from_user.id, months, price)
    await bot.send_message(callback_query.from_user.id,
        f"✅ Вы выбрали подписку на {months} мес ({price}₽).\n\n"
        f"Перейдите по ссылке для оплаты:\n{url}")

@dp.message_handler(lambda message: message.text.startswith("/paid"))
async def fake_payment_handler(message: types.Message):
    args = message.text.split()
    if len(args) != 3:
        await message.reply("Используй: /paid [user_id] [месяцев]")
        return
    user_id = int(args[1])
    months = int(args[2])
    username = (await bot.get_chat(user_id)).username or f"id{user_id}"
    now = datetime.now()
    expiry = now + timedelta(days=30 * months)
    with open(CSV_FILE, "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([user_id, username, now.date(), expiry.date(), months])
    await bot.send_message(GROUP_ID,
        f"💰 Оплата от @{username}\nТариф: {months} мес\nСумма: {990 if months==1 else 2690 if months==3 else 4790}₽")
    await bot.send_message(user_id,
        "🎉 Оплата прошла!\n\nВступайте в клуб:\nhttps://t.me/+i-61vFGHsw45ZjRi\n"
        "Если вас не приняли за 8ч — напишите @ManagerNeyroph")

async def check_subscriptions():
    if not os.path.exists(CSV_FILE):
        return
    with open(CSV_FILE, newline='') as f:
        reader = csv.reader(f)
        rows = list(reader)
    updated = []
    for row in rows:
        try:
            user_id = int(row[0])
            expiry = datetime.strptime(row[3], "%Y-%m-%d")
            if expiry < datetime.now():
                await bot.kick_chat_member(CHANNEL_ID, user_id)
            else:
                updated.append(row)
        except: pass
    with open(CSV_FILE, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(updated)

async def scheduler():
    while True:
        await check_subscriptions()
        await sleep(86400)  # 1 раз в день

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("✅ Согласен", callback_data="agree"),
        InlineKeyboardButton("❌ Не согласен", callback_data="disagree")
    )
    await message.answer(
        "Привет! Прежде чем мы начнём...\n\n"
        "⚠️ Мы заботимся о твоей конфиденциальности.\n\n"
        "Нажимая кнопку «Согласен», ты подтверждаешь, что ознакомлен(-а) с "
        "[Политикой обработки персональных данных](https://docs.google.com/document/d/1XHFjqbDKYhX5am-Ni2uQOO_FaoQhOcLcq7-UiZyQNlE/edit?usp=drive_link) "
        "и даёшь Согласие на обработку персональных данных.\n\n"
        "⬇️ Выбери вариант ниже:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )



