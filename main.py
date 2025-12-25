import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# ---------- СОСТОЯНИЯ ----------
class MenuState(StatesGroup):
    scripts = State()
    files = State()
    tgk = State()

# ---------- КНОПКИ ----------
main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add("📂 Каталог скриптов", "📁 Полезные файлы")
main_menu.add("📢 Полезные ТГК", "👤 Обо мне")

sub_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
sub_menu.add("Пусто 1", "Пусто 2", "Пусто 3")
sub_menu.add("Пусто 4", "Пусто 5", "Пусто 6")
sub_menu.add("⬅️ Назад")

# ---------- START ----------
@dp.message_handler(commands="start")
async def start(message: types.Message):
    await message.answer_photo(
        photo=open("start.jpg", "rb"),
        caption="👋 Добро пожаловать",
        reply_markup=main_menu
    )

# ---------- РАЗДЕЛЫ ----------
@dp.message_handler(text="📂 Каталог скриптов")
async def scripts(message: types.Message):
    await MenuState.scripts.set()
    await message.answer("📂 Каталог скриптов", reply_markup=sub_menu)

@dp.message_handler(text="📁 Полезные файлы")
async def files(message: types.Message):
    await MenuState.files.set()
    await message.answer("📁 Полезные файлы", reply_markup=sub_menu)

@dp.message_handler(text="📢 Полезные ТГК")
async def tgk(message: types.Message):
    await MenuState.tgk.set()
    await message.answer("📢 Полезные ТГК", reply_markup=sub_menu)

@dp.message_handler(text="👤 Обо мне")
async def about(message: types.Message):
    await message.answer("👤 Создатель: @ego_njw")

# ---------- НАЗАД ----------
@dp.message_handler(text="⬅️ Назад", state="*")
async def back(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Главное меню", reply_markup=main_menu)

# ---------- ПУСТЫЕ КНОПКИ ----------
@dp.message_handler(lambda m: m.text.startswith("Пусто"), state=MenuState.scripts)
async def scripts_text(message: types.Message):
    texts = {
        "Пусто 1": "Скрипт 1",
        "Пусто 2": "Скрипт 2",
        "Пусто 3": "Скрипт 3",
        "Пусто 4": "Скрипт 4",
        "Пусто 5": "Скрипт 5",
        "Пусто 6": "Скрипт 6",
    }
    await message.answer(texts[message.text])

@dp.message_handler(lambda m: m.text.startswith("Пусто"), state=MenuState.files)
async def files_text(message: types.Message):
    texts = {
        "Пусто 1": "Файл 1",
        "Пусто 2": "Файл 2",
        "Пусто 3": "Файл 3",
        "Пусто 4": "Файл 4",
        "Пусто 5": "Файл 5",
        "Пусто 6": "Файл 6",
    }
    await message.answer(texts[message.text])

@dp.message_handler(lambda m: m.text.startswith("Пусто"), state=MenuState.tgk)
async def tgk_text(message: types.Message):
    texts = {
        "Пусто 1": "https://t.me/channel1",
        "Пусто 2": "https://t.me/channel2",
        "Пусто 3": "https://t.me/channel3",
        "Пусто 4": "https://t.me/channel4",
        "Пусто 5": "https://t.me/channel5",
        "Пусто 6": "https://t.me/channel6",
    }
    await message.answer(texts[message.text])

# ---------- RUN ----------
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
