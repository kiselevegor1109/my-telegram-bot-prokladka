import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


BOT_TOKEN TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

CHANNEL_1_URL = os.getenv("CHANNEL_1_URL", "https://t.me/iGadGetGo")
CHANNEL_2_URL = os.getenv("CHANNEL_2_URL", "https://t.me/iGadgetGo_bot")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📢 ПОДПИСАТЬСЯ НА КАНАЛ", url=CHANNEL_1_URL)],
        [InlineKeyboardButton(text="🛍️ ПЕРЕЙТИ В МАГАЗИН", url=CHANNEL_2_URL)],
    ]
)


@dp.message(CommandStart())
async def send_buttons(message):
    user = message.from_user
    logging.info(
        "User started bot: id=%s username=%s first_name=%s",
        user.id,
        user.username,
        user.first_name,
    )
    await message.answer("🎉 Добро пожаловать в iGadgetGo!  \n \nУ нас вы найдете оригинальные iPhone по выгодным ценам с полной гарантией качества.  \n \n🚚 Для новых подписчиков — БЕСПЛАТНАЯ ДОСТАВКА НА ПЕРВЫЙ ЗАКАЗ! \n \n📢 Подпишитесь на нашу группу, чтобы быть в курсе:  \n• Самых свежих поступлений и новинок  \n• Специальных акций и эксклюзивных скидок  \n• Новостей из мира Apple и гаджетов  \n• Акционных предложений только для подписчиков  \n \n👇 Выберите действие:", reply_markup=keyboard)


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[
            logging.FileHandler("bot.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())


