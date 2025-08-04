# bot.py

import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode

# 🔐 Твой Telegram Token (для теста вставим напрямую)
TOKEN = "8075247657:AAEOFQGogUIITMVpndzRR_jH-ZM84NRqa4Q"

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Простой хендлер на /start
@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("Привет! Бот успешно запущен 🎉")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
