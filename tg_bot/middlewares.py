from typing import Callable, Any, Awaitable, Dict

from aiogram.dispatcher.middlewares import base
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog

import bootstrap
from service.managers.user_data_manager import UserData
from states.states import UserRegSG

bot = bootstrap.MyBot().getInstance()
dp = bootstrap.MyDispatcher().getInstance()


class Save_callback(base.BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        message = event
        user_id = message.from_user.id
        if isinstance(event, CallbackQuery):
            message = event.message
            user_id = message.chat.id
        user_data = await UserData(user_id=user_id).get_data()
        if user_data.data.ban:
            return
        print(data.get('event_router'), flush=True)
        dialog = data.get('event_router')
        if isinstance(dialog, Dialog):
            state_group = dialog.states_group()
        else:
            state_group = None
        print(state_group, flush=True)
        if not user_data.data.registered and state_group != UserRegSG:
            bg_manager = await user_data.create_bg_manager()
            await bg_manager.start(state=UserRegSG.input_phone)
            return
        return await handler(event, data)


