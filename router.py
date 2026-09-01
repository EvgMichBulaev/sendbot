from aiogram import Router
from aiogram.types import Message
from aiogram import Bot

from handlers import quote_command

router = Router()


@router.message(quote_command)
async def handle_quote_command(message: Message, bot: Bot):
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
    except Exception as e:
        await message.answer(
            "❌ Не удалось отправить сообщение. "
            "Убедитесь, что бот может читать сообщения в этом чате."
        )
