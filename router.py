from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ContentType

from users.handlers import (
    quote_command,
    handle_quote_command,
    handle_files_command,
    handle_file_callback,
    handle_file_message,
)

router = Router()

router.message.register(handle_quote_command, quote_command)
router.message.register(handle_files_command, F.text == "/files")


@router.message(F.content_type.in_({ContentType.DOCUMENT, ContentType.PHOTO, ContentType.VIDEO, ContentType.AUDIO}))
async def handle_file(message: Message, bot: Bot):
    """Обрабатывает сообщения с файлами и сохраняет их в БД."""
    content_type = message.content_type

    if content_type == ContentType.DOCUMENT:
        await handle_file_message(message, "document")
    elif content_type == ContentType.PHOTO:
        await handle_file_message(message, "photo")
    elif content_type == ContentType.VIDEO:
        await handle_file_message(message, "video")
    elif content_type == ContentType.AUDIO:
        await handle_file_message(message, "audio")


@router.callback_query(F.data.startswith("file_"))
async def handle_file_callback_wrapper(callback: CallbackQuery, bot: Bot):
    """Обёртка для обработки callback от кнопок файлов."""
    await handle_file_callback(callback, callback.data, bot)
