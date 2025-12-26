import os, subprocess, tempfile
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

user_lang = {}

# -------------------- MENUS --------------------

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

HELLO_TEXTS = {
    "brainfuck": "++++++++++[>+++++++>++++++++++>+++>+<<<<-]>.>++.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.>.",
    "chef": """Hello World Souffle.

Ingredients.
72 g haricot beans
101 eggs
108 g lard
111 cups oil
32 zucchinis
119 ml water
114 g red salmon
100 g dijon mustard

Method.
Put everything into the mixing bowl.
Liquefy.
Pour into baking dish.

Serves 1.""",
    "malbolge": "(=<`#9]~6ZY32Vx/4Rs+0No-&Jk)\"Fh}|Bcy?`=*z]Kw%oG4UUS0/@-e+"
}

# -------------------- START --------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_photo(
            photo=open("start.jpg", "rb"),
            caption="Добро пожаловать!\nВыбери действие:",
            reply_markup=MAIN_MENU
        )

# -------------------- MENU HANDLER --------------------

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "compiler":
        await q.message.edit_text("Выбери язык:", reply_markup=COMPILER_MENU)

    elif q.data == "hello":
        await q.message.edit_text("Hello World примеры:", reply_markup=HELLO_MENU)

    elif q.data == "about":
        await q.message.edit_text(
            "👨‍💻 Создатель: @ego_njw\n"
            "🤖 Telegram Compiler Bot\n"
            "⚙️ Sandbox + безопасность"
        )

    elif q.data == "back":
        await q.message.edit_text("Главное меню:", reply_markup=MAIN_MENU)

    elif q.data in ["python", "cpp", "js"]:
        user_lang[q.from_user.id] = q.data
        await q.message.reply_text(f"Язык выбран: {q.data.upper()}\nОтправь код.")

    elif q.data in HELLO_TEXTS:
        await q.message.reply_text(f"```{HELLO_TEXTS[q.data]}```", parse_mode="Markdown")

# -------------------- CODE EXECUTION --------------------

def safe_run(cmd):
    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=3
    )

async def run_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = user_lang.get(uid)
    code = update.message.text

    if not lang:
        return

    try:
        if lang == "python":
            r = safe_run(["python3", "-c", code])

        elif lang == "js":
            r = safe_run(["node", "-e", code])

        elif lang == "cpp":
            with tempfile.TemporaryDirectory() as t:
                cpp = f"{t}/main.cpp"
                exe = f"{t}/a.out"
                open(cpp, "w").write(code)
                c = safe_run(["g++", cpp, "-o", exe])
                if c.returncode != 0:
                    return await update.message.reply_text(c.stderr)
                r = safe_run([exe])

        await update.message.reply_text(r.stdout or r.stderr or "Нет вывода")

    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

# -------------------- MAIN --------------------

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, run_code))
    app.run_polling()

if __name__ == "__main__":
    main()
