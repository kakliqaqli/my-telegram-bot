import os
from datetime import timedelta, datetime
from typing import Dict, List, Protocol
from typing import Optional

from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, InlineKeyboardButton, Location, Message
from aiogram.types import LabeledPrice
from aiogram_dialog import ShowMode
from aiogram_dialog.api.internal import RawKeyboard, Widget, KeyboardWidget
from aiogram_dialog.api.protocols import DialogManager, DialogProtocol
from aiogram_dialog.widgets.input import BaseInput
from aiogram_dialog.widgets.kbd import Group
from aiogram_dialog.widgets.kbd import Keyboard
from aiogram_dialog.widgets.text import Text
from babel.core import Locale
from babel.dates import format_timedelta
import bootstrap
from service.managers.meet_manager import RideSystem
from service.managers.user_data_manager import UserData

APIClient = None
bot = bootstrap.MyBot().getInstance()

scheduler = bootstrap.Scheduler().getInstance()


class DynamicLocation(Keyboard):
    def __init__(
            self,
            *target_states: State,
            driver_id: Text = None,
    ):
        self.id = 'DynamicLocation'
        super().__init__(id=self.id)
        self.target_states = target_states
        self.driver_id = driver_id

    async def _render_keyboard(
            self,
            data: Dict,
            manager: DialogManager,
    ) -> []:
        user = await UserData(manager).get_data()
        message = user.data.AdditionalFields.location_message
        print(message, flush=True)
        if manager.current_context().state in self.target_states and self.driver_id:
            driver_id = await self.driver_id.render_text(data, manager)
            driver = RideSystem().driver_manager.drivers.get(int(driver_id))
            location = driver.current_location
            print(location, flush=True)
            if not message:
                new_message = await bot.send_location(user.user_id, location.latitude, location.longitude,live_period=86000)
                user.data.AdditionalFields.location_message = new_message
            elif self.are_locations_different(location, message.location):
                new_message = await message.edit_live_location(location.latitude, location.longitude)
                user.data.AdditionalFields.location_message = new_message
        else:
            if message:
                try:
                    await message.delete()
                except:
                    pass
                finally:
                    user.data.AdditionalFields.location_message = None
        return []

    def are_locations_different(self, loc1, loc2, precision=3):
        return round(loc1.latitude, precision) != round(loc2.latitude, precision) or \
            round(loc1.longitude, precision) != round(loc2.longitude, precision)


class StarRating(Keyboard):
    def __init__(
            self,
            id: str = 'StarRating',
    ):
        super().__init__(id=id)
        self.selected: int
        self.id = id

    async def _render_keyboard(
            self,
            data: Dict,
            manager: DialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        if not hasattr(self, 'selected'):
            self.selected = 0
        kbd = [
            [InlineKeyboardButton(text='☆' if i+1 > self.selected else '🌟', callback_data=str(i+1)) for i in range(5)]]
        return kbd

    async def process_callback(self, callback: CallbackQuery, dialog: DialogProtocol, manager: DialogManager) -> bool:
        if callback.data.isdigit():
            self.selected = int(callback.data)
            manager.current_context().dialog_data.update({'review_rating': int(callback.data)})
            return True
        else:
            return False




