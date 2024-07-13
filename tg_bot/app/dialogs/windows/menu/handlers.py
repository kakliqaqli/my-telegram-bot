import datetime

from aiogram import types, Bot
from aiogram.types import Location, User, Chat
from aiogram_dialog import DialogManager
from babel.util import UTC
from pydantic_core import TzInfo

import bootstrap
from service.http2orm.models import Trip
from service.managers.meet_manager import RideSystem
from service.managers.user_data_manager import UserData
from states.states import MainSG

bot: Bot = bootstrap.MyBot().getInstance()


async def start(message: types.Message, dialog_manager: DialogManager, text=None):
    try:
        await dialog_manager.reset_stack()
    except:
        ...
    await dialog_manager.start(MainSG.show)


async def chat(message: types.Message, dialog_manager: DialogManager):
    await dialog_manager.done()
    # await message.reply(config.chat, parse_mode="markdown")
