import os
import subprocess
import tempfile
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

user_lang = {}
last_message = {}

# ------------------- КНОПКИ -------------------

MAIN_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("🧠 Компилятор", callback_data="compiler")],
    [InlineKeyboardButton("🌍 Hello World", callback_data="hello")],
    [InlineKeyboardButton("ℹ️ Обо мне", callback_data="about")]
])

COMPILER_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("🐍 Python", callback_data="python")],
    [InlineKeyboardButton("⚙️ C++", callback_data="cpp")],
    [InlineKeyboardButton("🟨 JavaScript", callback_data="js")],
    [InlineKeyboardButton("⬅ Назад", callback_data="back")]
])

HELLO_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("🧠 Brainfuck", callback_data="brainfuck")],
    [InlineKeyboardButton("🍳 Chef", callback_data="chef")],
    [InlineKeyboardButton("💀 Malbolge", callback_data="malbolge")],
    [InlineKeyboardButton("⬅ Назад", callback_data="back")]
])

HELLO_CODES = {
    "brainfuck": "++++++++++[>+++++++>++++++++++>+++>+<<<<-]>.>++.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.>.",
    "chef": "Hello World Souffle.\n\nIngredients.\n72 g haricot beans\n101 eggs\n108 g lard\n111 cups oil\n32 zucchinis\n119 ml water\n114 g red salmon\n100 g dijon mustard\n\nMethod.\nMix all.\nServe.",
    "malbolge": "(=<`#9]~6ZY32Vx/4Rs+0No-&Jk)\"Fh}|Bcy?`=*z]Kw%oG4UUS0/@-e+"
}

# ------------------- HELPERS -------------------

async def edit(update, text, keyboard=None):
    chat = update.effective_chat.id
    try:
        mid = last_message.get(chat)
        if mid:
            await update.get_bot().edit_message_text(
                chat_id=chat,
                message_id=mid,
                text=text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            return
    except:
        pass

    msg = await update.effective_chat.send_message(
        text=text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    last_message[chat] = msg.message_id


# ------------------- HANDLERS -------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await edit(update, "👋 *Добро пожаловать!*\nВыбери действие:", MAIN_MENU)


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "compiler":
        await edit(update, "🧠 Выбери язык:", COMPILER_MENU)

    elif q.data == "hello":
        await edit(update, "🌍 Hello World:", HELLO_MENU)

    elif q.data == "about":
        await edit(update, "👨‍💻 Создатель: @ego_njw\n\n🤖 Telegram Compiler Bot")

    elif q.data == "back":
        await edit(update, "Главное меню:", MAIN_MENU)

    elif q.data in ["python", "cpp", "js"]:
        user_lang[q.from_user.id] = q.data
        await edit(update, f"✍️ Напиши код на *{q.data.upper()}*")

    elif q.data in HELLO_CODES:
        await edit(update, f"```{HELLO_CODES[q.data]}```", InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅ Назад", callback_data="back")]
        ]))


async def run_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = user_lang.get(uid)
    code = update.message.text

    if not lang:
        return

    await edit(update, "⏳ Выполняется...")

    try:
        if lang == "python":
            r = subprocess.run(["python3", "-c", code], capture_output=True, text=True, timeout=3)

        elif lang == "js":
            r = subprocess.run(["node", "-e", code], capture_output=True, text=True, timeout=3)

        elif lang == "cpp":
            with tempfile.TemporaryDirectory() as d:
                src = f"{d}/a.cpp"
                exe = f"{d}/a.out"
                open(src, "w").write(code)
                c = subprocess.run(["g++", src, "-o", exe], capture_output=True, text=True)
                if c.returncode != 0:
                    await edit(update, f"❌ Ошибка компиляции:\n{c.stderr}")
                    return
                r = subprocess.run([exe], capture_output=True, text=True)

        await edit(update, f"✅ Результат:\n```\n{r.stdout or r.stderr}\n```",
                   InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Назад", callback_data="back")]]))

    except Exception as e:
        await edit(update, f"❌ Ошибка: {e}")


# ------------------- MAIN -------------------

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, run_code))
    app.run_polling()

if __name__ == "__main__":
    main()
