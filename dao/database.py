from datetime import datetime
from typing import List, Optional
from config import database_url
from sqlalchemy import func, TIMESTAMP, Integer, select
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession


engine = create_async_engine(url=database_url)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession)


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    @classmethod
    @property
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'


async def save_file(
    chat_id: int,
    message_id: int,
    user_id: int,
    file_type: str,
    file_name: Optional[str],
    caption: Optional[str],
    message_text: Optional[str],
    original_chat_id: int,
    original_message_id: int,
    expires_at: Optional[datetime] = None,
) -> "File":
    """Сохраняет метаданные файла в БД."""
    from dao.model import File
    
    if expires_at is None:
        from datetime import timedelta
        expires_at = datetime.utcnow() + timedelta(hours=24)
    
    async with async_session_maker() as session:
        file_record = File(
            chat_id=chat_id,
            message_id=message_id,
            user_id=user_id,
            file_type=file_type,
            file_name=file_name,
            caption=caption,
            message_text=message_text,
            original_chat_id=original_chat_id,
            original_message_id=original_message_id,
            expires_at=expires_at,
        )
        session.add(file_record)
        await session.commit()
        await session.refresh(file_record)
        return file_record


async def get_user_files(user_id: int) -> List["File"]:
    """Получает все файлы, сохранённые пользователем."""
    from dao.model import File
    
    async with async_session_maker() as session:
        result = await session.execute(
            select(File)
            .where(File.user_id == user_id)
            .order_by(File.created_at.desc())
        )
        return list(result.scalars().all())


async def get_all_files() -> List["File"]:
    """Получает все файлы в базе данных."""
    from dao.model import File
    
    async with async_session_maker() as session:
        result = await session.execute(
            select(File)
            .order_by(File.created_at.desc())
        )
        return list(result.scalars().all())


async def delete_file(file_id: int) -> bool:
    """Удаляет файл из БД."""
    from dao.model import File
    
    async with async_session_maker() as session:
        file_record = await session.get(File, file_id)
        if file_record:
            await session.delete(file_record)
            await session.commit()
            return True
        return False


async def delete_expired_files() -> int:
    """Удаляет все просроченные файлы. Возвращает количество удалённых."""
    from dao.model import File
    
    deleted_count = 0
    async with async_session_maker() as session:
        result = await session.execute(
            select(File).where(File.expires_at < datetime.utcnow())
        )
        expired_files = list(result.scalars().all())
        for file_record in expired_files:
            await session.delete(file_record)
            deleted_count += 1
        if deleted_count > 0:
            await session.commit()
    return deleted_count