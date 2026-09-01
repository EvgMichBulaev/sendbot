import logging

from aiogram.filters import BaseFilter
from aiogram.types import Message

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
