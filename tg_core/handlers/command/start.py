from telegram import Update
from telegram.ext import ContextTypes

from tg_core.inlineKeyboard import language_selection_keyboard
from tg_core.logger import logger
from config import translations as __
from database import User

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    lang = User.get_language_by_update(update)
    
    logger.info(f"New user {user_id}")
    
    await update.message.reply_text(
        __[lang]['start'].format(name=update.effective_user.first_name),
        reply_markup=language_selection_keyboard(),
    )

