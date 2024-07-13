from typing import Optional

from aiogram.types import User as TGUser, Chat
from aiogram_dialog import DialogManager
from aiogram_dialog.manager.bg_manager import BgManager
from cachetools import TTLCache

import bootstrap
from service.translator.base import TranslationService
from service.http2orm.models import User

bot = bootstrap.MyBot().getInstance()
dp = bootstrap.MyDispatcher().getInstance()


class UserData:
    cache = TTLCache(maxsize=10000, ttl=3600)

    def __init__(self, dialog_manager: DialogManager = None, user_id: Optional[int] = None):
        if not any([dialog_manager, user_id]):
            raise ValueError("Dialog_manager any user_id must be provided")
        self.dialog_manager = dialog_manager
        self.user_id = user_id or self.get_user_id(dialog_manager)
        self.data: Optional[User] = None

    async def get_data(self) -> 'UserData':
        if self.user_id in self.cache:
            self.data = self.cache[self.user_id]
        else:
            self.data, _ = await User.get_or_create(id=self.user_id)
            print(self.data, flush=True)
            self.cache[self.user_id] = self.data
        return self

    async def get_translations(self, slag: str) -> str:
        user = self.data or (await self.get_data()).data
        return TranslationService.translate(slag, user.lang)

    @classmethod
    def get_user_id(cls, dialog_manager: DialogManager):
        return dialog_manager.middleware_data["event_from_user"].id

    async def create_bg_manager(self) -> BgManager:
        user = TGUser(id=self.user_id, is_bot=False, first_name="First name", language_code=self.data.lang)
        chat = Chat(id=self.user_id, type="private")
        return BgManager(user=user, chat=chat, bot=bot, router=dp.sub_routers[0], intent_id=None, stack_id="", load=True)
