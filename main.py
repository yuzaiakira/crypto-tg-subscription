import os
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

from tg_core.handlers.command import start, plan, order, check, membership
from tg_core.handlers.conversation import wallet_Handler
from tg_core.handlers.callback import callback_routing
from tg_core.background import background_processing
from logger import logger


TG_TOKEN = os.getenv("TG_TOKEN")

async def background_job(app):
    await background_processing(app)


def main():
    app = ApplicationBuilder().token(TG_TOKEN).build()
    logger.info("Bot started")
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("plan", plan))
    app.add_handler(CommandHandler("order", order))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("membership", membership))
    
    # /wallet command conversation
    app.add_handler(wallet_Handler)
    
    app.add_handler(CallbackQueryHandler(callback_routing))

    # Configure scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        lambda: asyncio.run(background_job(app)),  # Use asyncio.run to create an event loop
        'interval',
        seconds=5,
        jitter=30
        )
    
    scheduler.start()

    app.run_polling()


if __name__ == "__main__":
    main()
