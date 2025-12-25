import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = os.getenv("BOT_TOKEN")

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

# --- Старт ---
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
async def scripts_menu(message: types.Message):
    await message.answer("📂 Каталог скриптов:", reply_markup=sub_menu)

@dp.message_handler(text="📁 Полезные файлы")
async def files_menu(message: types.Message):
    await message.answer("📁 Полезные файлы:", reply_markup=sub_menu)

@dp.message_handler(text="📢 Полезные ТГК")
async def tgk_menu(message: types.Message):
    await message.answer("📢 Полезные ТГК:", reply_markup=sub_menu)

@dp.message_handler(text="👤 Обо мне")
async def about_me(message: types.Message):
    await message.answer("👤 Мой Telegram:\n@ego_njw")

# --- Назад ---
@dp.message_handler(text="⬅️ Назад")
async def back(message: types.Message):
    await message.answer("Главное меню:", reply_markup=main_menu)

# --- Пустые кнопки ---
@dp.message_handler(lambda m: m.text.startswith("Пусто"))
async def empty_buttons(message: types.Message):
    texts = {
        "Пусто 1": "СЮДА ВСТАВИШЬ СКРИПТ 1",
        "Пусто 2": "СЮДА ВСТАВИШЬ СКРИПТ 2",
        "Пусто 3": "СЮДА ВСТАВИШЬ СКРИПТ 3",
        "Пусто 4": "СЮДА ВСТАВИШЬ СКРИПТ 4",
        "Пусто 5": "СЮДА ВСТАВИШЬ СКРИПТ 5",
        "Пусто 6": "СЮДА ВСТАВИШЬ СКРИПТ 6",
    }
    await message.answer(texts.get(message.text, "Пусто"))

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
