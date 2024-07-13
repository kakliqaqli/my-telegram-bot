import os

from aiogram.types import Message
from aiogram_dialog import DialogManager

import bootstrap
from service.managers.user_data_manager import UserData
from service.translator.base import TranslationBase
from states.states import MainSG
from service.http2orm.models import Driver

bot = bootstrap.MyBot().getInstance()


async def input_photo(message: Message, MessageInput, manager: DialogManager):
    user_data = await UserData(manager).get_data()
    user_data.data.driver = Driver.empty_instance()
    file = await bot.get_file(message.photo[-1].file_id)
    user_data.data.driver.photo = f'https://api.telegram.org/file/bot{os.environ.get("TELEGRAM_BOT_TOKEN")}/{file.file_path}'
    await manager.next()


async def input_fullname(message: Message, MessageInput, manager: DialogManager):
    user_data = await UserData(manager).get_data()
    user_data.data.driver.fullname = message.text
    await manager.next()


async def input_car_number(message: Message, MessageInput, manager: DialogManager):
    user_data = await UserData(manager).get_data()
    user_data.data.driver.car_number = message.text
    user_data.data.driver.profile = user_data.data.id
    await user_data.data.driver.create()

    slag = TranslationBase.SuccessRegisteredDriver.slag('CLEAR')
    text = await user_data.get_translations(slag)
    await message.answer(text)
    await manager.start(MainSG.show)
