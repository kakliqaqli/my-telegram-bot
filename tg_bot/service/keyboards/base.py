from typing import List

from filters.filters import IsDriverReg, IsDriverActive
from service.keyboards.common.types import Keyboard, Button
from service.translator.base import TranslationService
from states.states import OrderStates, DriverRegSG, DriverProfileSG, DriverSearchSG, PayStates

trans = TranslationService.base


class KeyboardsManager:
    main_menu = Keyboard(buttons=[
        [Button(text=trans.MainWindow_order_button.slag('CLEAR'), state=OrderStates.start_search)],
        [Button(text=trans.MainWindow_reg_driver_button.slag('CLEAR'),
                state=DriverRegSG.input_photo, when=[IsDriverReg(reverse=True)])],
        [Button(text=trans.MainWindow_search_orders_button.slag('CLEAR'),
                state=DriverSearchSG.input_location, when=[IsDriverActive()])],
        [Button(text=trans.MainWindow_profile_button.slag('CLEAR'),
                state=DriverProfileSG.show, when=[IsDriverActive()])],
    ])

    @classmethod
    def get_buttons(cls) -> List[Button]:
        buttons = []
        for kbd in cls.__dict__.values():
            if isinstance(kbd, Keyboard):
                buttons.extend(kbd.get_buttons())
        return buttons
