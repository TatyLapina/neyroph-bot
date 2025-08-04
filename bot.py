# bot.py

import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
import os

TOKEN = "8075247657:AAEOFQGogUIITMVpndzRR_jH-ZM84NRqa4Q"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start_handler(message: Message):
    await message.answer("Привет! Бот успешно запущен 🎉")

async def main():
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
