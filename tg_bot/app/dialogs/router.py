from aiogram import F
from aiogram.enums import ContentType
from aiogram.filters import Command

import bootstrap

import middlewares


from filters.filters import create_dynamic_filter
from service.keyboards.base import KeyboardsManager



def register_commands():
    import app.dialogs.windows as windows
    dp = bootstrap.MyDispatcher().getInstance()
    dp.callback_query.middleware(middlewares.Save_callback())
    dp.message.middleware(middlewares.Save_callback())
    dp.edited_message.register(windows.UpdateLocation, F.content_type == ContentType.LOCATION)
    dp.message.register(windows.MainHandler, Command(commands='start'))
    for button in KeyboardsManager.get_buttons():
        handler = button.create_dynamic_handler()
        dp.message.register(handler, create_dynamic_filter(button.text))
