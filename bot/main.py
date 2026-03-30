import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
import aiohttp.web

TOKEN = os.getenv("BOT_TOKEN")
DOMAIN = os.getenv("DOMAIN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Бот работает!.")


@dp.message()
async def echo(message: types.Message):
    await message.answer(message.text)

async def healthcheck(request: aiohttp.web.Request):
    """Простая главная страница, чтобы сайт не отдавал 404"""
    return aiohttp.web.Response(
        text="Telegram Echo Bot is running successfully!",
        content_type="text/plain"
    )

async def on_startup(bot: Bot) -> None:
    webhook_url = f"https://{DOMAIN}/webhook"
    await bot.set_webhook(webhook_url)
    print(f"Webhook successfully set to: {webhook_url}")

async def main():
    app = aiohttp.web.Application()

    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    ).register(app, path="/webhook")

    app.router.add_get("/", healthcheck)

    setup_application(app, dp, bot=bot)

    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    site = aiohttp.web.TCPSite(runner, host="0.0.0.0", port=8080)
    await site.start()

    print(f"Bot started on http://0.0.0.0:8080")
    print(f"Webhook URL: https://{DOMAIN}/webhook")

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
