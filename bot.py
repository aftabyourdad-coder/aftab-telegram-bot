import os
import re
import json
import time
import threading
import telebot

TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = 7769850348
DATA_FILE = "users.json"
MAX_BROADCAST_LINES = 50

if not TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is missing.")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
lock = threading.Lock()

EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)
ALLOWED_DOMAINS = {"hi2.in", "telegmail.com"}


def load_users():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(int(x) for x in data)
    except (FileNotFoundError, json.JSONDecodeError, TypeError, ValueError):
        return set()


def save_users(users):
    with lock:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted(users), f)


def remember_user(chat_id):
    users = load_users()
    if chat_id not in users:
        users.add(chat_id)
        save_users(users)


def check_email(value):
    value = value.strip()
    if not EMAIL_PATTERN.fullmatch(value):
        return False, "Invalid email format"
    domain = value.rsplit("@", 1)[1].lower()
    if domain not in ALLOWED_DOMAINS:
        return False, "Format is valid, but domain is not supported"
    return True, "Valid format and supported domain"


@bot.message_handler(commands=["start"])
def start(message):
    remember_user(message.chat.id)
    bot.reply_to(
        message,
        "👋 Welcome!\n\n"
        "Send an email address to check its format.\n"
        "Supported domains: <code>@hi2.in</code> and "
        "<code>@telegmail.com</code>\n\n"
        "Commands: /help and /myid"
    )


@bot.message_handler(commands=["help"])
def help_command(message):
    remember_user(message.chat.id)
    bot.reply_to(
        message,
        "📌 <b>How to use</b>\n"
        "• Send one email address per message.\n"
        "• This checks syntax and supported domain only; "
        "it does not confirm that an inbox exists.\n\n"
        "/start — Start the bot\n"
        "/myid — Show your Telegram ID\n"
        "/help — Show help"
    )


@bot.message_handler(commands=["myid"])
def myid(message):
    remember_user(message.chat.id)
    bot.reply_to(message, f"Your Telegram ID: <code>{message.from_user.id}</code>")


@bot.message_handler(commands=["broadcast"])
def broadcast(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "⛔ Only the bot owner can use this command.")
        return

    text = message.text.partition(" ")[2].strip()
    if not text:
        bot.reply_to(message, "Usage: <code>/broadcast Your message</code>")
        return

    users = load_users()
    if not users:
        bot.reply_to(message, "No users have started the bot yet.")
        return

    sent = 0
    failed = 0
    status = bot.reply_to(message, f"Sending to {len(users)} opted-in users…")

    for chat_id in list(users):
        try:
            bot.send_message(chat_id, text)
            sent += 1
            time.sleep(0.08)
        except Exception:
            failed += 1

    bot.edit_message_text(
        f"✅ Broadcast finished.\nSent: {sent}\nFailed: {failed}",
        chat_id=status.chat.id,
        message_id=status.message_id
    )


@bot.message_handler(func=lambda message: bool(message.text) and not message.text.startswith("/"))
def validate_email(message):
    remember_user(message.chat.id)
    lines = [line.strip() for line in message.text.splitlines() if line.strip()]

    if len(lines) > MAX_BROADCAST_LINES:
        bot.reply_to(message, f"Please send at most {MAX_BROADCAST_LINES} lines at a time.")
        return

    results = []
    for item in lines:
        ok, reason = check_email(item)
        icon = "✅" if ok else "❌"
        results.append(f"{icon} <code>{item}</code> — {reason}")

    bot.reply_to(message, "\n".join(results))


if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling(skip_pending=True, timeout=30, long_polling_timeout=30)
