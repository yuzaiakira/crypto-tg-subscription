from telegram import Update
from telegram.ext import CallbackContext

from .lang_button import set_lang_button_callback
from .subscription_button import subscription_button_callback


async def callback_routing(update: Update, context: CallbackContext) -> None:
   # Ensure this is a callback query
    if not update.callback_query:
        return

    # Get the callback data
    query = update.callback_query.data

    # Route based on the callback data
    if query.startswith('set_lang'):
        await set_lang_button_callback(update, context)
    elif query.startswith('plan_'):
        await subscription_button_callback(update, context)


__all__ = ('callback_routing', )
