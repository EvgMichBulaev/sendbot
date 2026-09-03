import logging

from dao.database import delete_expired_files

logger = logging.getLogger(__name__)


async def cleanup_expired_files():
    """Удаляет все просроченные файлы из базы данных."""
    try:
        deleted = await delete_expired_files()
        if deleted > 0:
            logger.info(f"Deleted {deleted} expired files")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
