import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# === КОНФИГУРАЦИЯ ===
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    print("❌ ОШИБКА: Переменная TELEGRAM_BOT_TOKEN не установлена!")
    print("👉 Проверьте на Render.com: ваш сервис → Environment → Environment Variables")
    sys.exit(1)

WEBHOOK_URL = "https://igadgetgo-bot-zj5l.onrender.com"

CHANNEL_1_URL = os.getenv("CHANNEL_1_URL", "https://t.me/iGadGetGo")
CHANNEL_2_URL = os.getenv("CHANNEL_2_URL", "https://t.me/iGadgetGo_bot")

# === КЛАВИАТУРА ===
keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📢 ПОДПИСАТЬСЯ НА КАНАЛ", url=CHANNEL_1_URL)],
        [InlineKeyboardButton(text="🛍️ ПЕРЕЙТИ В МАГАЗИН", url=CHANNEL_2_URL)],
    ]
)

# === ОБРАБОТЧИК /start КОМАНДЫ ===
async def handle_start_command(message: Message):
    user = message.from_user
    logging.info(f"🔵 КОМАНДА /start от пользователя: id={user.id}, username={user.username}")
    await send_welcome_message(message)

# === ОБРАБОТЧИК ТЕКСТА "start" (кнопка) ===
async def handle_start_text(message: Message):
    user = message.from_user
    logging.info(f"🟢 КНОПКА START от пользователя: id={user.id}, username={user.username}")
    await send_welcome_message(message)

# === ОБЩАЯ ФУНКЦИЯ ПРИВЕТСТВИЯ ===
async def send_welcome_message(message: Message):
    welcome_text = (
        "🎉 Добро пожаловать в iGadgetGo!\n\n"
        "У нас вы найдете оригинальные iPhone по выгодным ценам "
        "с полной гарантией качества.\n\n"
        "🚚 Для новых подписчиков — БЕСПЛАТНАЯ ДОСТАВКА НА ПЕРВЫЙ ЗАКАЗ!\n\n"
        "📢 Подпишитесь на нашу группу, чтобы быть в курсе:\n"
        "• Самых свежих поступлений и новинок\n"
        "• Специальных акций и эксклюзивных скидок\n"
        "• Новостей из мира Apple и гаджетов\n"
        "• Акционных предложений только для подписчиков\n\n"
        "👇 Выберите действие:"
    )
    await message.answer(welcome_text, reply_markup=keyboard)

# === ДИАГНОСТИЧЕСКИЙ ОБРАБОТЧИК ===
async def debug_handler(message: Message):
    logging.info(f"📊 ДИАГНОСТИКА: text='{message.text}', type={message.content_type}, user={message.from_user.id}")
    return False  # Продолжаем обработку другими хендлерами

# === ЗАПУСК ДЛЯ RENDER.COM ===
async def main():
    # 1. ИНИЦИАЛИЗАЦИЯ
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # 2. Регистрация обработчиков
    # Команда /start
    dp.message.register(handle_start_command, CommandStart())
    # Текст "start" (без слеша) - для кнопки
    dp.message.register(handle_start_text, F.text.lower() == "start")
    # Диагностика всех сообщений
    dp.message.register(debug_handler)
    
    # 3. Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    # 4. Установка вебхука
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logging.info("✅ Старый вебхук удален")
        
        result = await bot.set_webhook(
            url=f"{WEBHOOK_URL}/webhook",
            drop_pending_updates=True
        )
        logging.info(f"✅ Webhook установлен: {WEBHOOK_URL}/webhook")
        logging.info(f"✅ Telegram подтвердил: {result}")
    except Exception as e:
        logging.error(f"❌ Ошибка вебхука: {e}")
    
    # 5. Создание aiohttp приложения
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=BOT_TOKEN
    )
    
    webhook_requests_handler.register(app, path="/webhook")
    setup_application(app, dp, bot=bot)
    
    # 6. Запуск сервера
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    
    logging.info(f"✅ Бот запущен на порту {port}")
    logging.info("✅ Ожидаю сообщения...")
    
    # 7. Бесконечный цикл
    await asyncio.Future()

if __name__ == "__main__":
    print("🚀 Запуск бота iGadgetGo...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
