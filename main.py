import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import BaseFilter
from aiogram.types import Message
from fastapi import FastAPI, Request
import uvicorn

from config import Settings

logging.basicConfig(level=logging.INFO)

settings = Settings()
bot = Bot(token=settings.bot_token)
dp = Dispatcher()

app = FastAPI()

COMMAND = "отправь мне"


class QuoteCommandFilter(BaseFilter):
    """Проверяет, что сообщение содержит команду 'отправь мне'."""

    def __init__(self, command: str = COMMAND):
        self.command = command

    async def __call__(self, message: Message) -> bool:
        if not message.text:
            return False
        return self.command.lower() in message.text.lower()


quote_command = QuoteCommandFilter()


@dp.message(quote_command)
async def handle_quote_command(message: Message):
    """Обрабатывает цитированные сообщения с командой 'отправь мне'."""
    if not message.reply_to_message:
        return

    quoted_message = message.reply_to_message
    user = message.from_user

    try:
        await bot.copy_message(
            chat_id=user.id,
            from_chat_id=quoted_message.chat.id,
            message_id=quoted_message.message_id,
        )
        logging.info(
            f"Sent message {quoted_message.message_id} from chat "
            f"{quoted_message.chat.id} to user {user.id}"
        )
    except Exception as e:
        logging.error(f"Failed to send quoted message: {e}")
        await message.answer(
            "❌ Не удалось отправить сообщение. "
            "Убедитесь, что бот может читать сообщения в этом чате."
        )


@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(url=settings.webhook_url)
    logging.info(f"Webhook set to {settings.webhook_url}")


@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    logging.info("Webhook deleted")


@app.post(settings.webhook_path)
async def webhook_endpoint(request: Request):
    """Обработчик вебхука от Telegram."""
    update = await request.json()
    await dp.feed_webhook_update(bot, update, msgpack=False)
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level="info",
    )
