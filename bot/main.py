import asyncio
import os
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
import aiohttp.web

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TOKEN = os.getenv("BOT_TOKEN")
DOMAIN = os.getenv("DOMAIN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("👋 Бот работает через webhook!")

@dp.message()
async def echo(message: types.Message):
    await message.answer(f"Эхо: {message.text}")

async def healthcheck(request):
    return aiohttp.web.Response(text="✅ Bot is running via webhook!", status=200)

async def on_startup(bot: Bot):
    await asyncio.sleep(3)
    if not DOMAIN:
        logging.error("❌ DOMAIN не указан в .env")
        return
    
    webhook_url = f"https://{DOMAIN}/webhook"
    try:
        result = await bot.set_webhook(webhook_url, drop_pending_updates=True)
        if result:
            logging.info(f"✅ Webhook УСПЕШНО установлен: {webhook_url}")
        else:
            logging.warning("⚠️ set_webhook вернул False")
    except Exception as e:
        logging.error(f"❌ Ошибка при установке webhook: {e}")

async def main():
    logging.info("🚀 Запуск Telegram Echo Bot...")

    app = aiohttp.web.Application()
    
    # Главная страница
    app.router.add_get("/", healthcheck)
    
    # Webhook для Telegram
    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    ).register(app, path="/webhook")

    # Важно! Подключаем on_startup
    setup_application(app, dp, bot=bot, on_startup=on_startup)

    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    site = aiohttp.web.TCPSite(runner, host="0.0.0.0", port=8080)
    await site.start()

    logging.info(f"✅ Сервер слушает порт 8080")
    logging.info(f"🌐 Целевой webhook: https://{DOMAIN}/webhook")

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
