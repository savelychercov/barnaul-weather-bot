from telebot import types

default_button = [{
    "text": "test",
    "url": None,
    "key": "key_test"
}]


def buttons(btns=None, inline: bool = True):
    if btns is None:
        btns = default_button
    keyboard = types.InlineKeyboardMarkup() if inline else types.ReplyKeyboardMarkup()
    for button_data in btns:
        button = types.InlineKeyboardButton(button_data["text"], button_data["url"], button_data["key"]) if inline else types.KeyboardButton(button_data["text"])
        keyboard.add(button)
    return keyboard
