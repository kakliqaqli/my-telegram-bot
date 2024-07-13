from aiogram.types import Message
from aiogram_dialog import DialogManager

import bootstrap
from service.managers.user_data_manager import UserData
from states.states import MainSG

bot = bootstrap.MyBot().getInstance()


async def input_contact(message: Message, MessageInput, manager: DialogManager):
    user_data = await UserData(manager).get_data()
    user_data.data.phone_number = message.contact.phone_number
    user_data.data.registered = True
    user_data.data.username = message.from_user.username
    await user_data.data.update()
    await manager.start(MainSG.show)