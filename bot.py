import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputFile
from telegram.ext import (ApplicationBuilder, CallbackQueryHandler,
                          CommandHandler, ContextTypes, MessageHandler, filters, JobQueue)
import datetime
import csv
import os
import hashlib

TOKEN = os.getenv("TOKEN") or "8075247657:AAEOFQGogUIITMVpndzRR_jH-ZM84NRqa4Q"
CHANNEL_LINK = "https://t.me/+i-61vFGHsw45ZjRi"
GROUP_CHAT_ID = "-1002133175953"

SUBSCRIPTION_CSV = "subscriptions.csv"
ROBO_BASE = "https://auth.robokassa.ru/Merchant/Index.aspx"
MERCHANT_LOGIN = "Neyroph_bot"
PASSWORD1 = "dR07mRr4HoY8sGQb5Any"

TARIFFS = {
    "1": ("1 месяц", 990, 30),
    "3": ("3 месяца", 2690, 90),
    "6": ("6 месяцев", 4790, 180)
}

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Согласен", callback_data="agree")],
        [InlineKeyboardButton("Не согласен", callback_data="decline")]
    ]
    await update.message.reply_text(
        "Привет! Прежде чем мы начнём...\n\n"
        "⚠️ Мы заботимся о твоей конфиденциальности.\n\n"
        "Нажимая кнопку «Согласен», ты подтверждаешь, что ознакомлен(-а) с "
        "[Политикой обработки персональных данных](https://docs.google.com/document/d/1XHFjqbDKYhX5am-Ni2uQOO_FaoQhOcLcq7-UiZyQNlE/edit?usp=drive_link) "
        "и даёшь Согласие на обработку персональных данных.\n\n"
        "⬇️ Выбери вариант ниже:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        disable_web_page_preview=True,
        parse_mode='Markdown'
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "agree":
        keyboard = [
            [InlineKeyboardButton("👤 Создание персонажей", callback_data="characters")],
            [InlineKeyboardButton("🔒 Вступить в закрытый клуб", callback_data="club")]
        ]
        await query.edit_message_text(
            "Привет от Тани и Кости — команды NEYROPH! Мы делаем классные фото и видео и хотим, чтобы и у тебя получалось!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "characters":
        video_path = "video_placeholder.mp4"
        await context.bot.send_video(chat_id=query.from_user.id, video=InputFile(video_path))
        keyboard = [
            [InlineKeyboardButton("📚 Записаться на обучение", url="https://ai-avatar.ru/learning")],
            [InlineKeyboardButton("✉️ Написать в личные сообщения", url="https://t.me/ManagerNeyroph")],
            [InlineKeyboardButton("⬅️ В главное меню", callback_data="agree")]
        ]
        await context.bot.send_message(query.from_user.id,
            "Это вводный урок о персонажах. Здесь я рассказываю всякие штуки (ты потом заменишь текст)",
            reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "club":
        keyboard = [
            [InlineKeyboardButton("📅 Подписка на 1 месяц — 990₽", callback_data="pay_1")],
            [InlineKeyboardButton("📅 Подписка на 3 месяца — 2690₽", callback_data="pay_3")],
            [InlineKeyboardButton("📅 Подписка на 6 месяцев — 4790₽", callback_data="pay_6")]
        ]
        await query.edit_message_text(
            "Выбирай срок подписки и вступай в наш клуб!\n\n"
            "Оплачивая тариф, вы даёте согласие на регулярные списания, на обработку персональных данных и принимаете условия публичной оферты.",
            reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("pay_"):
        months = data.split("_")[1]
        title, price, _ = TARIFFS[months]
        invoice_id = int(datetime.datetime.now().timestamp())
        signature = f"{MERCHANT_LOGIN}:{price}:{invoice_id}:{PASSWORD1}"
        signature_md5 = hashlib.md5(signature.encode()).hexdigest()

        link = f"{ROBO_BASE}?MerchantLogin={MERCHANT_LOGIN}&OutSum={price}&InvoiceID={invoice_id}&Description=Подписка+на+{title}&SignatureValue={signature_md5}&Recurring=Y"

        await query.message.reply_text(
            f"🔐 Тариф: {title}\n💰 Сумма: {price}₽\n\nПосле оплаты ты получишь ссылку на вступление в клуб.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💳 Перейти к оплате", url=link)]])
        )

async def payment_success(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    await query.answer()
    # заглушка: принимаем успешную оплату вручную через callback
    months = 1
    username = user.username or user.first_name
    start = datetime.datetime.now()
    end = start + datetime.timedelta(days=30 * months)

    with open(SUBSCRIPTION_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([user.id, username, start.isoformat(), end.isoformat()])

    await context.bot.send_message(GROUP_CHAT_ID, f"✅ Пришла оплата от @{username}")
    await context.bot.send_message(user.id,
        f"🎉 Поздравляем! Ваша оплата прошла успешно!\n\nПерейдите по ссылке: {CHANNEL_LINK}\nОжидайте одобрения администратора (до 8ч). Вопросы — @ManagerNeyroph")

async def check_expired_subscriptions(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.now()
    rows = []
    expired = []

    if not os.path.exists(SUBSCRIPTION_CSV):
        return

    with open(SUBSCRIPTION_CSV, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            user_id, username, _, end_date = row
            if datetime.datetime.fromisoformat(end_date) < now:
                expired.append(int(user_id))
            else:
                rows.append(row)

    for uid in expired:
        try:
            await context.bot.send_message(uid, "⏳ Ваша подписка закончилась. Чтобы остаться в клубе — оплатите снова через /start")
        except:
            pass

    with open(SUBSCRIPTION_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(CallbackQueryHandler(payment_success, pattern="^confirm_payment$"))
    job_queue: JobQueue = app.job_queue
    job_queue.run_repeating(check_expired_subscriptions, interval=86400, first=60)
    app.run_polling()
