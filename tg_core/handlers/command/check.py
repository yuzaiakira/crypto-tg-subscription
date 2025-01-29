from telegram import Update
from telegram.ext import ContextTypes
from logger import logger
from config import translations as __
from database import User, Payment


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    lang = User.get_language(user_id)
    
    user = User.get_user(user_id)
    payment = Payment.check_user_payments(user_id)
    pending_order = Payment.user_has_pending_payment(user_id)
    
    logger.info(f"check command -> payment: {payment}")
    logger.info(f"check command -> pending_order: {pending_order}")
    
    if payment:
        new_membership = str(user.get_membership_expiry.date())
        await update.message.reply_text(__[lang]['order']['accept'].format(date=new_membership))
    elif pending_order:
        await update.message.reply_text(__[lang]['order']['unable'])
    else:
        await update.message.reply_text(__[lang]['order']['no_order'])