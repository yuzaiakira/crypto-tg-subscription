from telegram import Update
from telegram.ext import ContextTypes

from config import translations as __
from database import User, Payment


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = User.get_language_by_update(update)
    
    Payment.check_pending_payments()
    # TODO: make it better
    await update.message.reply_text( __[lang]['order']['canceling'],)
