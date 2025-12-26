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

TOKEN = os.getenv("BOT_TOKEN")

LANGS = {
    "python": "🐍 Python",
    "js": "🟨 JavaScript",
    "cpp": "⚙️ C++",
    "csharp": "💎 C#",
    "brainfuck": "🧠 Brainfuck"
}

HELLO = {
    "python": 'print("Hello, World!")',
    "js": 'console.log("Hello, World!")',
    "cpp": '#include <iostream>\nint main(){std::cout<<"Hello, World!";}',
    "csharp": 'using System; class P{static void Main(){Console.WriteLine("Hello, World!");}}',
    "brainfuck": '++++++++++[>+++++++>++++++++++>+++>+<<<<-]>.>++.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.>.'
}

user_lang = {}

# ---------- Brainfuck ----------
def run_brainfuck(code):
    tape = [0] * 30000
    ptr = 0
    out = ""
    i = 0
    stack = []

    while i < len(code):
        c = code[i]
        if c == ">": ptr = (ptr + 1) % 30000
        elif c == "<": ptr = (ptr - 1) % 30000
        elif c == "+": tape[ptr] = (tape[ptr] + 1) % 256
        elif c == "-": tape[ptr] = (tape[ptr] - 1) % 256
        elif c == ".":
            out += chr(tape[ptr])
        elif c == "[":
            if tape[ptr] == 0:
                depth = 1
                while depth:
                    i += 1
                    if code[i] == "[": depth += 1
                    elif code[i] == "]": depth -= 1
            else:
                stack.append(i)
        elif c == "]":
            if tape[ptr] != 0:
                i = stack[-1]
            else:
                stack.pop()
        i += 1
    return out


# ---------- BOT HANDLERS ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton(v, callback_data=k)] for k, v in LANGS.items()]
    await update.message.reply_text(
        "Выбери язык программирования:",
        reply_markup=InlineKeyboardMarkup(kb)
    )


async def select_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_lang[q.from_user.id] = q.data

    await q.message.reply_text(
        f"Выбран язык: {LANGS[q.data]}\n\n"
        f"Напиши код или нажми /hello"
    )


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = user_lang.get(uid)
    if not lang:
        return await update.message.reply_text("Сначала выбери язык /start")

    await update.message.reply_text(f"```{HELLO[lang]}```", parse_mode="Markdown")


async def run_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    code = update.message.text
    lang = user_lang.get(uid)

    if not lang:
        return await update.message.reply_text("Сначала выбери язык /start")

    try:
        if lang == "python":
            p = subprocess.run(
                ["python3", "-c", code],
                capture_output=True,
                text=True,
                timeout=3
            )

        elif lang == "js":
            p = subprocess.run(
                ["node", "-e", code],
                capture_output=True,
                text=True,
                timeout=3
            )

        elif lang == "cpp":
            with tempfile.TemporaryDirectory() as tmp:
                cpp = f"{tmp}/a.cpp"
                exe = f"{tmp}/a.out"
                open(cpp, "w").write(code)
                c = subprocess.run(["g++", cpp, "-o", exe], capture_output=True, text=True)
                if c.returncode != 0:
                    return await update.message.reply_text(c.stderr)
                p = subprocess.run([exe], capture_output=True, text=True)

        elif lang == "csharp":
            with tempfile.TemporaryDirectory() as tmp:
                cs = f"{tmp}/Program.cs"
                open(cs, "w").write(code)
                p = subprocess.run(
                    ["dotnet", "run", "--project", tmp],
                    capture_output=True,
                    text=True
                )

        elif lang == "brainfuck":
            out = run_brainfuck(code)
            return await update.message.reply_text(out or "Пусто")

        await update.message.reply_text(p.stdout or p.stderr or "Нет вывода")

    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")


def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("hello", hello))
    app.add_handler(CallbackQueryHandler(select_lang))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, run_code))
    app.run_polling()


if __name__ == "__main__":
    main()
