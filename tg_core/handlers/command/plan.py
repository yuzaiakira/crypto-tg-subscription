from telegram import Update
from telegram.ext import ContextTypes

from tg_core.inlineKeyboard import subscription_selection_keyboard
from config import translations as __
from database import User


async def plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = User.get_language_by_update(update)
    
    await update.message.reply_text(
        __[lang]['plans']['description'],
        reply_markup=subscription_selection_keyboard(lang),
    )
