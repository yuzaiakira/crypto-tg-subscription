from telegram import Update
from telegram.ext import ContextTypes
import datetime
from tg_core.inlineKeyboard import language_selection_keyboard
from logger import logger
from config import translations as __
from database import User

async def membership(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user = User.get_user(user_id)
    lang = user.lang
    
    if user.has_membership:
        membership_expiry = user.get_membership_expiry.date()
        
        await update.message.reply_text(__[lang]['membership']['is_membership'].format(date=membership_expiry))
    else:
        await update.message.reply_text(__[lang]['membership']['no_membership']) 
    