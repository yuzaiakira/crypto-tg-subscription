from telegram import Update
from telegram.ext import CallbackContext

from database import User
from config import translations as __


# set language button
async def set_lang_button_callback(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    user_lang = User.get_language(user_id)
    query = update.callback_query
    await query.answer()
    
    # Use a dictionary for scalable language mapping
    lang_mapping = {
        'set_lang_en': 'en',
        'set_lang_fa': 'fa'
    }
    
    # Get language code or None if not found
    lang = lang_mapping.get(query.data)

    if not lang:
        await query.message.reply_text(set_message = __[user_lang]['lang']['invalid'])
        return
    else:
        set_message = __[lang]['lang']['set']
        await query.answer(set_message)
        await query.message.reply_text(set_message)
        User.set_language(user_id, lang)      
