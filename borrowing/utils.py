import os

from telegram import Bot
from dotenv import load_dotenv

load_dotenv()


async def send_notification_to_telegram_bot(text: str) -> None:
    """Send a message to Telegram"""
    bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))

    await bot.send_message(
        chat_id=os.getenv("CHAT_ID"),
        text=text,
    )
