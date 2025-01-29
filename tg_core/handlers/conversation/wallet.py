from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from logger import logger
from .State_manager import GET_WALLET_ADDRESS

from config import translations as __
from database import User
from tron import validate_tron_wallet_address




async def wallet_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Start the wallet conversation by asking the user for their wallet address.
    """
    user_id = update.effective_user.id
    lang = User.get_language(user_id)
    
    if User.has_wallet(user_id):
        await update.message.reply_text(__[lang]['wallet']['change'].format(
            wallet=User.get_wallet(user_id)))

    await update.message.reply_text(__[lang]['wallet']['get'])

    return GET_WALLET_ADDRESS


async def handle_wallet_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the user's wallet address input.
    """
    user_id = update.effective_user.id
    lang = User.get_language(user_id)
    
    wallet_address = update.message.text
    
    if validate_tron_wallet_address(wallet_address):
        logger.info(f"User {user_id} changed wallet address: {wallet_address}")

        User.set_wallet_address(user_id, wallet_address)
        
        await update.message.reply_text(__[lang]['wallet']['success'].format(wallet=wallet_address))
        return ConversationHandler.END


    await update.message.reply_text(__[lang]['wallet']['invalid'])
    return GET_WALLET_ADDRESS


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Cancel the conversation.
    """
    lang = User.get_language_by_update(update)
    await update.message.reply_text(__[lang]['wallet']['cancel'])
    return ConversationHandler.END

# Set up the ConversationHandler
wallet_Handler = ConversationHandler(
    entry_points=[CommandHandler('wallet', wallet_start)],  # Start the conversation with /wallet
    states={
        GET_WALLET_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_wallet_address)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]  # Allow the user to cancel the conversation
)