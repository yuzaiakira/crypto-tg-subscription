from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import translations as __


# Inline keyboard for language selection
def language_selection_keyboard() -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton("English", callback_data='set_lang_en')],
                [InlineKeyboardButton("فارسی", callback_data='set_lang_fa')]]
    
    return InlineKeyboardMarkup(keyboard) 


# Inline keyboard for subscription selection
def subscription_selection_keyboard(lang: str) -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton(__[lang]['plans']['plans_list'][0], callback_data='plan_0')],
                [InlineKeyboardButton(__[lang]['plans']['plans_list'][1], callback_data='plan_1')],
                [InlineKeyboardButton(__[lang]['plans']['plans_list'][2], callback_data='plan_2')],
                ]
    return InlineKeyboardMarkup(keyboard) 