from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, BigInteger, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from dao.database import Base


class File(Base):
    __tablename__ = 'files'

    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    message_id: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    file_type: Mapped[str] = mapped_column(String(20), nullable=False)  # document, photo, video, audio
    file_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    caption: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    original_chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    original_message_id: Mapped[int] = mapped_column(Integer, nullable=False)
