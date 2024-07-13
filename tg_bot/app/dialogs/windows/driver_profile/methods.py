import os

from aiogram.types import Message
from aiogram_dialog import DialogManager

import bootstrap
from service.managers.user_data_manager import UserData
from states.states import DriverProfileSG
from service.http2orm.models import Driver

bot = bootstrap.MyBot().getInstance()


async def input_photo(message: Message, MessageInput, manager: DialogManager):
    user_data = await UserData(manager).get_data()
    user_data.data.driver = Driver.empty_instance()
    file = await bot.get_file(message.photo[-1].file_id)
    user_data.data.driver.photo = f'https://api.telegram.org/file/bot{os.environ.get("TELEGRAM_BOT_TOKEN")}/{file.file_path}'
    await user_data.data.driver.update()
    await manager.switch_to(DriverProfileSG.show)


async def input_fullname(message: Message, MessageInput, manager: DialogManager):
    user_data = await UserData(manager).get_data()
    user_data.data.driver.fullname = message.text
    await user_data.data.driver.update()
    await manager.switch_to(DriverProfileSG.show)


async def input_car_number(message: Message, MessageInput, manager: DialogManager):
    user_data = await UserData(manager).get_data()
    user_data.data.driver.car_number = message.text
    await user_data.data.driver.update()
    await manager.switch_to(DriverProfileSG.show)


async def profile_getter(dialog_manager: DialogManager, **kwargs):
    user = await UserData(dialog_manager).get_data()
    return {'driver': user.data.driver}
