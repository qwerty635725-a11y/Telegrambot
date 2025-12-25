import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# --- ENV ---
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# --- Главное меню ---
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(
    KeyboardButton("📂 Каталог скриптов"),
    KeyboardButton("📁 Полезные файлы")
)
main_menu.add(
    KeyboardButton("📢 Полезные ТГК"),
    KeyboardButton("👤 Обо мне")
)

# --- Подменю (6 кнопок) ---
sub_menu = ReplyKeyboardMarkup(resize_keyboard=True)
sub_menu.add(
    KeyboardButton("Пусто 1"),
    KeyboardButton("Пусто 2"),
    KeyboardButton("Пусто 3")
)
sub_menu.add(
    KeyboardButton("Пусто 4"),
    KeyboardButton("Пусто 5"),
    KeyboardButton("Пусто 6")
)
sub_menu.add(KeyboardButton("⬅️ Назад"))

# --- START ---
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    with open("start.jpg", "rb") as photo:
        await message.answer_photo(
            photo=photo,
            caption="👋 Привет! Добро пожаловать в бота со скриптами.",
            reply_markup=main_menu
        )

# --- Главное меню ---
@dp.message_handler(text="📂 Каталог скриптов")
async def scripts(message: types.Message):
    await message.answer("📂 Каталог скриптов:", reply_markup=sub_menu)

@dp.message_handler(text="📁 Полезные файлы")
async def files(message: types.Message):
    await message.answer("📁 Полезные файлы:", reply_markup=sub_menu)

@dp.message_handler(text="📢 Полезные ТГК")
async def tgk(message: types.Message):
    await message.answer("📢 Полезные ТГК:", reply_markup=sub_menu)

@dp.message_handler(text="👤 Обо мне")
async def about(message: types.Message):
    await message.answer("👤 Создатель:\n@ego_njw")

# --- Назад ---
@dp.message_handler(text="⬅️ Назад")
async def back(message: types.Message):
    await message.answer("Главное меню:", reply_markup=main_menu)

# --- Кнопки ПУСТО ---
@dp.message_handler(lambda m: m.text.startswith("Пусто"))
async def empty(message: types.Message):
    texts = {
        "Пусто 1": "ТЕКСТ СКРИПТА 1",
        "Пусто 2": "ТЕКСТ СКРИПТА 2",
        "Пусто 3": "ТЕКСТ СКРИПТА 3",
        "Пусто 4": "ТЕКСТ СКРИПТА 4",
        "Пусто 5": "ТЕКСТ СКРИПТА 5",
        "Пусто 6": "ТЕКСТ СКРИПТА 6",
    }
    await message.answer(texts.get(message.text, "Пусто"))

# --- Уведомление админу при старте ---
@dp.message_handler(commands=["admin"])
async def admin(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("✅ Админ доступ подтверждён")
    else:
        await message.answer("⛔ Нет доступа")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
