import asyncio
from abc import abstractmethod
from copy import deepcopy
from dataclasses import dataclass
from typing import List, Union, Callable, Optional, Coroutine, Protocol, Tuple

from aiogram.fsm.state import State
from aiogram.types import KeyboardButton, Message
from aiogram.utils.keyboard import ReplyKeyboardMarkup
from aiogram_dialog import DialogManager
from aiogram_dialog.api.internal import RawKeyboard
from aiogram_dialog.widgets.kbd import Keyboard as KeyboardWidget
from aiogram_dialog.widgets.text import Text

import bootstrap
from service.translator.base import TranslationService

bot = bootstrap.MyBot().getInstance()
FUNC_TYPE = Union[Callable[[DialogManager], Optional[Coroutine]], Coroutine]


class WhenButtonFilterProtocol(Protocol):
    @abstractmethod
    async def check(self, dialog_manager: DialogManager) -> bool:
        """Абстрактный метод, который будет реализован подклассами для определения конкретных условий видимости."""
        raise NotImplementedError


class WhenButtonFilterBase:
    def __init__(self, reverse: bool = False) -> None:
        self._reverse = reverse


class WhenButtonFilter(WhenButtonFilterBase, WhenButtonFilterProtocol):
    async def __call__(self, dialog_manager: DialogManager) -> bool:
        reverter = lambda x: not x
        visible = await self.check(dialog_manager)
        if self._reverse:
            visible = reverter(visible)
        return visible

    async def check(self, dialog_manager: DialogManager) -> bool:
        raise NotImplementedError("Subclasses should implement this!")


@dataclass
class Button:
    text: str
    state: Union[State, None] = None
    checker: FUNC_TYPE = None
    func: FUNC_TYPE = None
    when: List[WhenButtonFilter] = None

    def converter_aiogram_type(self):
        return KeyboardButton(text=self.text)

    async def check_access(self, dialog_manager):
        if self.when:
            checkers = []
            for when in self.when:
                checkers.append(await when(dialog_manager))
            return all(checkers)
        return True

    def create_dynamic_handler(self):
        class Handler:
            @staticmethod
            async def handler(_, dialog_manager: DialogManager):
                if self.func:
                    await self.func(dialog_manager)
                if self.state:
                    if self.checker and (await self.checker(dialog_manager)):
                        return
                    if dialog_manager.has_context():
                        if dialog_manager.current_context().state.group == self.state.group:
                            await dialog_manager.switch_to(state=self.state)
                            await dialog_manager.show()
                            return
                        else:
                            await dialog_manager.done()
                    await dialog_manager.start(state=self.state)
                else:
                    return

        return Handler().handler


class Keyboard:
    def __init__(self, buttons: List[List[Button]], one_time: bool = True):
        self.buttons = buttons
        self.one_time = one_time

    async def render(self, lang, dialog_manager: DialogManager) -> ReplyKeyboardMarkup:
        async def check_buttons(row):
            tasks = [button.check_access(dialog_manager) for button in row]
            results = await asyncio.gather(*tasks)
            return [
                KeyboardButton(text=TranslationService.translate(button.text, lang))
                for button, access in zip(row, results) if access
            ]

        tasks = [check_buttons(row) for row in deepcopy(self.buttons)]
        rendered_buttons = await asyncio.gather(*tasks)
        return ReplyKeyboardMarkup(keyboard=rendered_buttons, one_time_keyboard=self.one_time, resize_keyboard=True)

    def get_buttons(self) -> List[Button]:
        all_buttons = [button for row in self.buttons for button in row]
        return all_buttons

    def get_widget(self, when: Union[str, None] = None, additional_message: Union[Text, None] = None):
        return ReplayWidget(when=when, additional_message=additional_message, keyboard=self)


class ReplayWidget(KeyboardWidget):
    def __init__(self, keyboard: Keyboard, additional_message: Union[Text, None] = None,
                 when: Union[str, Callable, None] = None):
        super().__init__(when=when)
        self.keyboard = keyboard
        self.additional_message = additional_message

    async def _render_keyboard(self, data: dict, dialog_manager: DialogManager) -> RawKeyboard:
        if dialog_manager.is_preview():
            return []
        lang = dialog_manager.middleware_data["event_from_user"].language_code
        user_id = dialog_manager.middleware_data["event_from_user"].id
        keyboard_rendered = await self.keyboard.render(lang=lang, dialog_manager=dialog_manager)
        if self.additional_message:
            text = await self.additional_message.render_text({}, dialog_manager)
            await bot.send_message(user_id, text, reply_markup=keyboard_rendered)
            return []
        return keyboard_rendered.keyboard
