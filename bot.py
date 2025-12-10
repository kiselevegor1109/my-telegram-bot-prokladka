import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# === КОНФИГУРАЦИЯ ===
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# ПОКА НЕ МЕНЯЙТЕ! URL мы вставим после деплоя на Render
WEBHOOK_URL = "https://igadgetgo-bot-zj5l.onrender.com"

CHANNEL_1_URL = os.getenv("CHANNEL_1_URL", "https://t.me/iGadGetGo")
CHANNEL_2_URL = os.getenv("CHANNEL_2_URL", "https://t.me/iGadgetGo_bot")

# === ИНИЦИАЛИЗАЦИЯ ===
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# === КЛАВИАТУРА ===
keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📢 ПОДПИСАТЬСЯ НА КАНАЛ", url=CHANNEL_1_URL)],
        [InlineKeyboardButton(text="🛍️ ПЕРЕЙТИ В МАГАЗИН", url=CHANNEL_2_URL)],
    ]
)

# === ОБРАБОТЧИКИ ===
@dp.message(CommandStart())
async def send_buttons(message: Message):
    user = message.from_user
    logging.info(
        "User started bot: id=%s username=%s first_name=%s",
        user.id,
        user.username,
        user.first_name,
    )
    await message.answer(
        "🎉 Добро пожаловать в iGadgetGo!\n\n"
        "У нас вы найдете оригинальные iPhone по выгодным ценам "
        "с полной гарантией качества.\n\n"
        "🚚 Для новых подписчиков — БЕСПЛАТНАЯ ДОСТАВКА НА ПЕРВЫЙ ЗАКАЗ!\n\n"
        "📢 Подпишитесь на нашу группу, чтобы быть в курсе:\n"
        "• Самых свежих поступлений и новинок\n"
        "• Специальных акций и эксклюзивных скидок\n"
        "• Новостей из мира Apple и гаджетов\n"
        "• Акционных предложений только для подписчиков\n\n"
        "👇 Выберите действие:",
        reply_markup=keyboard
    )

# === WEBHOOK НАСТРОЙКИ ===
async def on_startup(bot: Bot):
    await bot.set_webhook(f"{WEBHOOK_URL}/webhook")

# === ЗАПУСК ДЛЯ RENDER.COM ===
async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    
    # Настройка вебхука при старте
    await on_startup(bot)
    
    # Создание aiohttp приложения
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=BOT_TOKEN
    )
    # Регистрируем путь для вебхука
    webhook_requests_handler.register(app, path="/webhook")
    setup_application(app, dp, bot=bot)
    
    # Запуск сервера на порту, который предоставляет Render
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    
    print(f"Bot started on port {port}. Webhook URL: {WEBHOOK_URL}/webhook")
    
    # Бесконечный цикл
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
