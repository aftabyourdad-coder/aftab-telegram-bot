# Aftab Telegram Bot

## Files
- `bot.py` — Telegram bot code
- `requirements.txt` — Python dependency
- `Procfile` — worker start command for compatible hosting platforms
- `.gitignore` — keeps secrets and local user data out of Git

## Before running
1. Create a bot with Telegram's official BotFather and copy its token.
2. Set an environment variable named `BOT_TOKEN` to that token.
3. Install dependencies: `pip install -r requirements.txt`
4. Start: `python bot.py`

Never paste your bot token into `bot.py`, GitHub, screenshots, or public chats.
If a token was exposed, revoke it with BotFather and create a new one.

## Commands
- `/start` — start the bot and register the chat for messages
- `/help` — help
- `/myid` — show your Telegram user ID
- `/broadcast message` — owner-only broadcast to people who have started the bot

Owner Telegram ID is set in `bot.py` as `7769850348`.

## Email checker note
This checks email syntax and allows only `hi2.in` and `telegmail.com`.
It does not check whether an inbox exists or can receive mail.

## Important hosting note
The bot stores opted-in chat IDs in `users.json`. Some free hosting services erase local files when an instance restarts or redeploys, so the broadcast user list may reset. Do not upload `users.json` to a public repository.
