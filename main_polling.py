import asyncio
import logging
from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import bot, dp, admins
from users.router import router
from utlite.cleanup import cleanup_expired_files

logging.basicConfig(level=logging.INFO)

dp.include_router(router)

async def set_commands():
    commands = [BotCommand(command='files', description='Список файлов для загрузки'),
                ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())

def setup_scheduler(bot: Bot):
    """Настраивает APScheduler для фоновых задач."""
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        cleanup_expired_files,
        "interval",
        hours=6,
        id="cleanup_expired_files",
        name="Удаление просроченных файлов",
        replace_existing=True,
    )
    scheduler.start()
    return scheduler

async def start_bot():
    await set_commands()
    for admin_id in admins:
        try:
            await bot.send_message(admin_id, f'Я запущен🥳.')

        except:
            pass


# Функция, которая выполнится, когда бот завершит свою работу
async def stop_bot():
    try:
        for admin_id in admins:
            await bot.send_message(admin_id, 'Бот остановлен. 😔')
    except:
        pass


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Запускаем планировщик для фоновых задач
    scheduler = setup_scheduler(bot)
    
    try:
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped")
