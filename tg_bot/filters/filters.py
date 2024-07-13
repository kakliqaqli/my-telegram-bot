import asyncio
from typing import Dict

from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.common import Whenable

from service.keyboards.common.types import WhenButtonFilter
from service.managers.user_data_manager import UserData
from service.translator.base import TranslationService


def create_dynamic_filter(button: str) -> BaseFilter:
    class CheckButton(BaseFilter):
        async def __call__(self, message: Message) -> bool:
            lang = message.from_user.language_code
            translate_text = TranslationService.translate(lang=lang, slag=button)
            if message.text == translate_text:
                return True
            return False

    return CheckButton()


class IsDriverReg(WhenButtonFilter):
    """Проверка что пользователь водитель"""

    async def check(self, manager: DialogManager):
        user = await UserData(manager).get_data()
        print(bool(user.data.driver), 'SDFFFFFFFFFFFF', flush=True)
        return bool(user.data.driver)


class IsDriverActive(WhenButtonFilter):
    """Проверка что пользователь активный водитель"""

    async def check(self, manager: DialogManager):
        user = await UserData(manager).get_data()
        return user.data.driver and user.data.driver.accepted

