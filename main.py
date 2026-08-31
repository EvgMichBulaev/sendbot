import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram.enums import ParseMode

from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

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
    # Проверяем, есть ли цитируемое сообщение
    if not message.reply_to_message:
        return

    quoted_message = message.reply_to_message
    user = message.from_user

    try:
        # Отправляем цитируемое сообщение в личные сообщения
        await bot.copy_message(
            chat_id=user.id,
            from_chat_id=quoted_message.chat.id,
            message_id=quoted_message.message_id,
        )
        logging.info(
            f"Sent message {quoted_message.message_id} from chat {quoted_message.chat.id} "
            f"to user {user.id}"
        )
    except Exception as e:
        logging.error(f"Failed to send quoted message: {e}")
        await message.answer(
            "❌ Не удалось отправить сообщение. "
            "Убедитесь, что бот может читать сообщения в этом чате."
        )


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Bot stopped")
