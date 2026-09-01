import logging
from typing import Optional

from aiogram import Bot, types
from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select
from dao.database import save_file, get_user_files, delete_file, async_session_maker
from dao.model import File


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

COMMAND_TEXT = "отправь мне"


class QuoteCommandFilter(BaseFilter):
    """Проверяет, что сообщение содержит команду 'отправь мне'."""

    def __init__(self, command: str = COMMAND_TEXT):
        self.command = command

    async def __call__(self, message: Message) -> bool:
        if not message.text:
            logging.warning(f"Filter: no text in message from user {message.from_user.id}")
            return False
        if not message.reply_to_message:
            logging.warning(
                f"Filter: no reply_to_message in message from user {message.from_user.id}: "
                f"text='{message.text}'"
            )
            return False
        matches = self.command.lower() in message.text.lower()
        logging.info(
            f"Filter: text='{message.text}', has_reply={bool(message.reply_to_message)}, "
            f"matches={matches}"
        )
        return matches


quote_command = QuoteCommandFilter()


FILE_TYPE_EMOJI = {
    "document": "📄",
    "photo": "📷",
    "video": "🎥",
    "audio": "🎵",
}


async def handle_file_message(message: Message, file_type: str):
    """Общий обработчик для сообщений с файлами."""
    file_name = None
    caption = None

    if file_type == "document" and message.document:
        file_name = message.document.file_name
        caption = message.caption
    elif file_type == "photo":
        caption = message.caption
        # Для фото берём последнее (самое большое) разрешение
        photo = message.photo[-1]
        file_name = f"{photo.file_size}px"
    elif file_type == "video" and message.video:
        file_name = message.video.file_name
        caption = message.caption
    elif file_type == "audio" and message.audio:
        file_name = message.audio.file_name
        caption = message.caption

    await save_file(
        chat_id=message.chat.id,
        message_id=message.message_id,
        user_id=message.from_user.id,
        file_type=file_type,
        file_name=file_name,
        caption=caption,
        original_chat_id=message.chat.id,
        original_message_id=message.message_id,
    )

    emoji = FILE_TYPE_EMOJI.get(file_type, "📎")
    type_label = {
        "document": "документ",
        "photo": "фото",
        "video": "видео",
        "audio": "аудио",
    }.get(file_type, "файл")

    await message.answer(f"{emoji} {type_label.capitalize()} сохранён!")


async def handle_files_command(message: Message):
    """Обработчик команды /files — показывает список файлов пользователя."""
    user_files = await get_user_files(message.from_user.id)

    if not user_files:
        await message.answer("У вас пока нет сохранённых файлов.")
        return

    builder = InlineKeyboardBuilder()

    for file_record in user_files:
        emoji = FILE_TYPE_EMOJI.get(file_record.file_type, "📎")
        display_name = file_record.file_name or f"{file_record.file_type} ({file_record.file_size if hasattr(file_record, 'file_size') else 'unknown'})"
        
        # Ограничиваем длину имени файла
        if len(display_name) > 30:
            display_name = display_name[:27] + "..."

        button_text = f"{emoji} {display_name}"
        builder.button(
            text=button_text,
            callback_data=f"file_{file_record.id}",
        )

    builder.adjust(1)

    await message.answer(
        "📁 Ваши сохранённые файлы:\n\n"
        "Нажмите на файл, чтобы получить его.",
        reply_markup=builder.as_markup(),
    )


async def handle_file_callback(callback: types.CallbackQuery, data: str, bot: Bot):
    """Обработчик нажатия на файл — пересылает файл пользователю."""
    file_id = int(data.replace("file_", ""))
    user_id = callback.from_user.id

    # Получаем файл из БД
    async with async_session_maker() as session:
        result = await session.execute(select(File).where(File.id == file_id, File.user_id == user_id))
        file_record = result.scalar_one_or_none()

    if not file_record:
        await callback.answer("Файл не найден или у вас нет к нему доступа.")
        return

    try:
        await bot.copy_message(
            chat_id=user_id,
            from_chat_id=file_record.original_chat_id,
            message_id=file_record.original_message_id,
        )
        await callback.answer("Файл отправлен!")
    except Exception as e:
        logging.error(f"Error sending file {file_id}: {e}")
        await callback.answer("Не удалось отправить файл.")

    # Удаляем файл из БД после отправки
    await delete_file(file_id, user_id)
