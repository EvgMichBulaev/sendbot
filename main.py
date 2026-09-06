import logging

from fastapi import FastAPI, Request
import uvicorn

from config import bot, dp, settings
from users.handlers import handle_quote_command, quote_command

logging.basicConfig(level=logging.INFO)

app = FastAPI()

dp.message(handle_quote_command, quote_command)


@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(url=settings.WEBHOOK_URL)
    logging.info(f"Webhook set to {settings.WEBHOOK_URL}")


@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    logging.info("Webhook deleted")


@app.post(settings.WEBHOOK_PATH)
async def webhook_endpoint(request: Request):
    """Обработчик вебхука от Telegram."""
    update = await request.json()
    await dp.feed_webhook_update(bot, update, msgpack=False)
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.PORT,
        log_level="info",
    )
