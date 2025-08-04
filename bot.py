import logging
import csv
import os
import hashlib
from datetime import datetime, timedelta
from asyncio import sleep
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.types import WebAppInfo

# --- Настройки ---
TOKEN = os.getenv("TOKEN") or "8075247657:AAEOFQGogUIITMVpndzRR_jH-ZM84NRqa4Q"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

GROUP_ID = -1000000000000  # ID группы "Оплаты"
CHANNEL_ID = -1000000000000  # ID закрытого клуба
CSV_FILE = "subscriptions.csv"
ROBOKASSA_MERCHANT_LOGIN = "Neyroph_bot"
ROBOKASSA_PASSWORD_1 = "dR07mRr4HoY8sGQb5Any"

# --- Команды ---
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
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

@dp.callback_query_handler(lambda c: c.data == 'disagree')
async def disagree_handler(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Жаль 😔 Если передумаешь — просто снова нажми /start.")

@dp.callback_query_handler(lambda c: c.data == 'agree')
async def agree_handler(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("👤 Создание персонажей", callback_data="create_characters"),
        InlineKeyboardButton("🔒 Вступить в закрытый клуб", callback_data="join_club")
    )
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=(
            "Привет! Мы Таня и Костя — основатели AI-студии Neyroph.\n"
    "Уже больше года профессионально работаем с нейросетями и визуалом: создаём сильные образы, мощные видео и креатив, который цепляет.\n\n"
    "За плечами — сотни выполненных заказов, десятки брендовых проектов, оформление блогов, клипов, YouTube-шоу, продуктов и визуальных концепций.\n"
    "Мы не просто «играемся с ИИ», а умеем выжимать максимум из технологий, чтобы решать задачи клиентов — быстро, точно и красиво.\n\n"
    "Одно из наших громких направлений — создание AI-персонажей под контент и монетизацию.\n"
    "Наш кейс Фаина — 24 млн просмотров, 70k подписчиков и 100k ₽ на продаже рекламы за 1 месяц — только с помощью роликов.\n\n"
    "Если ты хочешь погрузиться в мир нейросетей с головой — у тебя два варианта:\n\n"
    "1️⃣ Курс по созданию персонажа\n"
    "Научим с нуля: идея, образ, бренд, визуал, озвучка, продвижение, монетизация. Никакой воды — только практика и результат.\n\n"
    "2️⃣ Закрытый клуб Neyroph\n"
    "Узкий круг: всё о нейросетях, инструментах, промптах, трендах и нестандартных фишках. Доступ к знаниям и поддержке в любое время.\n\n"
    "👇 Выбирай, что тебе ближе — и присоединяйся!"
        ),
        reply_markup=keyboard
    )

@dp.callback_query_handler(lambda c: c.data == 'create_characters')
async def create_characters_handler(callback_query: types.CallbackQuery):
    await callback_query.answer()

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("✍️ Записаться на обучение", web_app=WebAppInfo(url="https://ai-avatar.ru/learning")),
        InlineKeyboardButton("📩 Написать в личные", url="https://t.me/ManagerNeyroph"),
        InlineKeyboardButton("⬅️ В главное меню", callback_data="agree")
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
        InlineKeyboardButton("⬅️ Назад", callback_data="agree")
    )
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=(
           "NEYROPH — закрытый клуб для тех, кто работает (или хочет работать) с генерацией изображений и видео с помощью нейросетей.\n"
    "Это не просто сборник новостей или шаблонов — это живая система прокачки, которая помогает расти, внедрять и зарабатывать с ИИ каждый день.\n\n"
    "Что внутри:\n\n"
    "🎓 Если ты новичок:\n"
    "- Пошаговые гайды и видеоуроки — всё понятно и без воды\n"
    "- Как писать сильные промпты, а не терять часы впустую\n"
    "- Стили съёмки, композиция, визуальные референсы\n"
    "- Готовые шаблоны и стартовые наборы — начнёшь в первый день\n"
    "- Обратная связь от нас — Таня и Костя — лично\n\n"
    "🚀 Если ты уже с опытом:\n"
    "- Обзоры новых платформ и тесты генерации\n"
    "- Работа с LoRA, видеогенерацией, анимацией\n"
    "- Как делать визуал под тренды, задачи брендов и клиентов\n"
    "- Наши авторские GPT-ассистенты — помогут, подскажут, ускорят\n"
    "- Реальные кейсы, быстрые инструкции и готовые промпты под задачи\n\n"
    "💥 Эксклюзив: Полный разбор кейса «Фаина»\n"
    "В клубе ты узнаешь:\n"
    "- Как мы придумали персонажа и чем вдохновлялись\n"
    "- Какие промпты используем, как генерируем видео и кадры\n"
    "- Что пишут в личку, как идёт монетизация\n"
    "- Все тонкости по контент-плану, сторителлингу и запуску — по шагам\n\n"
    "💬 Комьюнити, где ты не останешься один:\n"
    "- Активный чат с поддержкой от участников и нас\n"
    "- Разборы, советы, идеи и помощь 24/7\n"
    "- Никакого нытья, флуда и спама — только ценность и рост\n\n"
    "📦 Плюс:\n"
    "- Подборки лучших фишек и промптов (не публикуются в открытом доступе)\n"
    "- Мини-курсы и эксклюзивные материалы\n"
    "- Ответы от нас и ведущих участников — без ожидания и отписок\n\n"
    "NEYROPH — это как личный наставник, сообщество и практика в одном кармане.\n"
    "Ты не просто учишься. Ты действуешь — с поддержкой, уверенностью и фокусом.\n\n"
    "👇 Выбирай срок подписки и вступай в клуб прямо сейчас.\n\n"
    "_Оплачивая тариф, вы даёте согласие на регулярные списания, обработку персональных данных и принимаете условия публичной оферты._"
        ),
        reply_markup=keyboard
    )

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
    await bot.send_message(
        callback_query.from_user.id,
        f"✅ Вы выбрали подписку на {months} мес ({price}₽).\n\n"
        f"Перейдите по ссылке для оплаты:\n{url}"
    )

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
        except:
            pass
    with open(CSV_FILE, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(updated)

async def scheduler():
    while True:
        await check_subscriptions()
        await sleep(86400)

# --- Запуск ---
async def on_startup(dispatcher):
    from asyncio import ensure_future
    ensure_future(scheduler())

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
