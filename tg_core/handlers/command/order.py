from telegram import Update
from telegram.ext import ContextTypes

from config import translations as __
from database import User, Payment


async def order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    lang = User.get_language(user_id)
    Payment.cancel_all_user_orders(user_id)

    await update.message.reply_text( __[lang]['order']['canceling'],)
