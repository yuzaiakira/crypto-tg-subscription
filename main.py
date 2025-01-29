import os
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

from tg_core.handlers.command import start, plan, order, check
from tg_core.handlers.conversation import wallet_Handler
from tg_core.handlers.callback import callback_routing
from logger import logger

TG_TOKEN = os.getenv("TG_TOKEN")

def main():
    app = ApplicationBuilder().token(TG_TOKEN).build()
    logger.info("Bot started")
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("plan", plan))
    app.add_handler(CommandHandler("order", order))
    app.add_handler(CommandHandler("check", check))
    
    
    
    app.add_handler(wallet_Handler)
    
    app.add_handler(CallbackQueryHandler(callback_routing))

    app.run_polling()


if __name__ == "__main__":
    main()
