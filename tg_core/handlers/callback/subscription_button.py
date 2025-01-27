from telegram import Update
from telegram.ext import CallbackContext

from database import User, Payment
from config import translations as __
from config import subscription_plan

# set language button
async def subscription_button_callback(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    query = update.callback_query
    lang = User.get_language(user_id)
    
    # check use has wallet address or not?
    if not User.has_wallet(user_id):
        await query.message.reply_text(__[lang]['wallet']['notic'])
        return
    
    # check subscription plan is valid?
    plan = subscription_plan.get(query.data)
    if not plan:
        await query.message.reply_text(__[lang]['plans']['invalid_plan'])
        return
     
    # check user has pyment and /cancel 
    pending = Payment.user_has_pending_payment(user_id)
    if pending:
        await query.message.reply_text(__[lang]['plans']['pending'])
        return
        
    user_wallet = User.get_wallet(user_id)
    peyment = Payment.create_user_payment(telegram_id=user_id, amount=plan['amount'], duration_days=plan['duration_days'])
    await query.message.reply_text(__[lang]['plans']['pay'].format(amount=peyment.amount,
                                                                   send_address=peyment.deposit_address,
                                                                   user_address=user_wallet),
                                   parse_mode='Markdown')
