import logging

from fastapi import FastAPI, Request
import uvicorn

from config import bot, dp, settings
from dao.database import engine, async_session_maker
from users.handlers import handle_quote_command, quote_command
from users.router import router
from utlite.cleanup import cleanup_expired_files

"""
Модуль инициализации и запуска FastAPI сервера для Telegram Bot.

Создаёт и настраивает приложение FastAPI, подключает все роутеры,
настраивает middleware для работы с базой данных, инициализирует
планировщик задач и устанавливает webhook для Telegram.

Ключевые компоненты:
- FastAPI приложение с CORS
- Lifespan контекст для управления жизненным циклом
- Подключение роутеров API и Telegram handlers
- Управление базой данных и планировщиком задач
- Установка и удаление webhook при старте/остановке
"""
from fastapi import FastAPI, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import uvicorn

from aiogram.types import Update



@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом FastAPI приложения.

    При запуске:
    - Инициализирует двигатель БД и сессии
    - Настраивает middleware для обработки запросов
    - Подключает роутеры
    - Устанавливает команды меню Telegram
    - Запускает планировщик задач (APScheduler)
    - Настраивает webhook для Telegram
    - Уведомляет админов о запуске

    При остановке:
    - Останавливает планировщик задач
    - Уведомляет админов об остановке
    - Закрывает сессию бота
    - Освобождает ресурсы БД

    Args:
        app: Экземпляр FastAPI приложения

    Yields:
        None
    """
    logging.info("Бот запускается...")
    app.state.db_engine = engine
    app.state.db_session_maker = async_session_maker
    dp.storage.db_session_maker = async_session_maker

    dp.include_router(router)


    await bot.set_my_commands([
        {"command": "start", "description": "Начало работы"},
        {"command": "menu", "description": "Основное меню"}
    ])

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        cleanup_expired_files,
        'interval',
        hours=1,
        id='cleanup_expired_files',
        replace_existing=True
    )
    scheduler.start()
    app.state.scheduler = scheduler
    logging.info("Планировщик задач запущен")

    webhook_url = settings.WEBHOOK_URL.rstrip("/") + settings.WEBHOOK_PATH
    await bot.set_webhook(webhook_url, drop_pending_updates=True)
    logging.info(f"Webhook установлен: {webhook_url}")

    yield

    logging.info("Бот останавливается...")
    scheduler.shutdown()
    await bot.session.close()
    await app.state.db_engine.dispose()


app = FastAPI(
    title="Telegram Bot API",
    version="1.0.0",
    lifespan=lifespan,
    description="HTTP API для взаимодействия с Telegram ботом, управление подписками и платежами"
)


@app.get("/", summary="Health Check", description="Проверка работоспособности сервера")
def health():
    """
    Корневой endpoint для проверки работоспособности сервиса.

    Возвращает:
        dict: Статус "ok" при успешной работе сервера
    """
    return {"status": "ok"}


# === Вебхук для Telegram ===
@app.post(
    settings.WEBHOOK_PATH,
    summary="Telegram Webhook",
    description="Принимает обновления от Telegram Bot API и передаёт их в aiogram Dispatcher"
)
async def telegram_webhook(update: dict):
    """
    Обработчик вебхука Telegram.

    Принимает обновления от Telegram и передаёт их в aiogram Dispatcher
    для дальнейшей обработки хендлерами.

    Args:
        update: Словарь с данными обновления от Telegram (Update)

    Returns:
        dict: {"ok": True} при успешной обработке или ошибке

    Note:
        Все ошибки обрабатываются внутри и не прерывают работу webhook
    """
    try:
        from aiogram.types import Update
        update_obj = Update.model_validate(update, context={"bot": bot})
        result = await dp.feed_webhook_update(bot, update_obj)
        if result:
            await dp.silent_call_request(bot, result)
    except Exception as e:
        logging.error(f"Ошибка при обработке апдейта: {e}")
        return {"ok": True}


if __name__ == "__main__":
    """
    Запуск FastAPI сервера напрямую.

    Запускает сервер uvicorn на всех интерфейсах (0.0.0.0)
    с включённым авто-перезагрузкой (reload) для разработки.

    Порт настраивается через settings.PORT (по умолчанию 8000).

    Note:
        В продакшене необходимо использовать gunicorn или другой WSGI сервер
    """
    logging.info(f"Запуск FastAPI сервера на порту {settings.PORT}...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=True,
        log_level="info"
    )

