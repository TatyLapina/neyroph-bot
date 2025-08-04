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

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Согласен", callback_data="agree"))
    keyboard.add(InlineKeyboardButton("Не согласен", callback_data="disagree"))

    await message.answer(
        "Привет! Прежде чем мы начнём...\n\n"
        "⚠️ Мы заботимся о твоей конфиденциальности.\n\n"
        "Нажимая кнопку «Согласен», ты подтверждаешь, что ознакомлен(-а) с "
        "[Политикой обработки персональных данных](https://docs.google.com/document/d/1XHFjqbDKYhX5am-Ni2uQOO_FaoQhOcLcq7-UiZyQNlE/edit?usp=drive_link) "
        "и даёшь Согласие на обработку персональных данных.\n\n"
        "⬇️ Выбери вариант ниже:",
        reply_markup=keyboard,
        disable_web_page_preview=True,
        parse_mode="Markdown"
    )

@dp.callback_query_handler(lambda c: c.data == "agree")
async def agree_handler(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("👤 Создание персонажей", callback_data="characters"),
        InlineKeyboardButton("🔒 Вступить в закрытый клуб", callback_data="club")
    )

    await bot.send_message(
        callback_query.from_user.id,
        "Добро пожаловать! Мы — Таня и Костя, основатели студии NEYROPH. "
        "Мы создаём классный визуал и хотим, чтобы у каждого была возможность делать круто — даже без опыта!\n\n"
        "Выбери, с чего хочешь начать:",
        reply_markup=keyboard
    )

@dp.callback_query_handler(lambda c: c.data == "disagree")
async def disagree_handler(callback_query: types.CallbackQuery):
    await bot.send_message(
        callback_query.from_user.id,
        "Без согласия мы не можем продолжить 😢"
    )

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
