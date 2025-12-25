import os
import subprocess
import tempfile

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# 🔐 берём токен из Railway Variables
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN не найден в переменных окружения")

user_lang = {}

MAX_CODE_LENGTH = 2000
TIMEOUT = 3

FORBIDDEN = [
    "import os", "import sys", "subprocess",
    "open(", "exec", "eval", "__",
    "fork", "while True"
]

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🐍 Python", callback_data="python"),
            InlineKeyboardButton("🟨 JavaScript", callback_data="js"),
        ],
        [
            InlineKeyboardButton("⚙️ C++", callback_data="cpp")
        ]
    ]

    await update.message.reply_text(
        "Выбери язык программирования:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# выбор языка
async def choose_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_lang[query.from_user.id] = query.data

    await query.message.reply_text(
        f"✅ Язык выбран: {query.data.upper()}\nТеперь отправь код."
    )

def is_safe(code: str) -> bool:
    if len(code) > MAX_CODE_LENGTH:
        return False
    return not any(bad in code for bad in FORBIDDEN)

# выполнение кода
async def run_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    code = update.message.text
    lang = user_lang.get(user_id)

    if not lang:
        await update.message.reply_text("❗ Сначала выбери язык через /start")
        return

    if not is_safe(code):
        await update.message.reply_text("⛔ Код отклонён (опасный или слишком большой)")
        return

    try:
        if lang == "python":
            result = subprocess.run(
                ["python3", "-c", code],
                capture_output=True,
                text=True,
                timeout=TIMEOUT
            )

        elif lang == "js":
            result = subprocess.run(
                ["node", "-e", code],
                capture_output=True,
                text=True,
                timeout=TIMEOUT
            )

        elif lang == "cpp":
            with tempfile.TemporaryDirectory() as tmp:
                cpp = os.path.join(tmp, "main.cpp")
                exe = os.path.join(tmp, "a.out")

                with open(cpp, "w") as f:
                    f.write(code)

                compile = subprocess.run(
                    ["g++", cpp, "-O2", "-o", exe],
                    capture_output=True,
                    text=True,
                    timeout=TIMEOUT
                )

                if compile.returncode != 0:
                    await update.message.reply_text("❌ Ошибка компиляции:\n" + compile.stderr)
                    return

                result = subprocess.run(
                    [exe],
                    capture_output=True,
                    text=True,
                    timeout=TIMEOUT
                )

        output = result.stdout or result.stderr or "Нет вывода"
        await update.message.reply_text(f"📤 Результат:\n{output}")

    except subprocess.TimeoutExpired:
        await update.message.reply_text("⏱ Превышено время выполнения")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(choose_lang))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, run_code))

    app.run_polling()

if __name__ == "__main__":
    main()
