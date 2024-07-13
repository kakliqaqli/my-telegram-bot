from aiogram.enums import ContentType
from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput

from app.dialogs.windows.driver_registration.methods import input_photo, input_car_number, input_fullname
from service.translator.patching.aiogram_dialog.widgets import TranslationFormat
from service.translator.base import TranslationBase
from states.states import DriverRegSG
DriverRegWin = (
    Window(
        TranslationFormat(TranslationBase.DriverReg_send_photo.slag(mode='FORMATTING')),
        MessageInput(func=input_photo, content_types=[ContentType.PHOTO]),
        parse_mode="markdown",
        state=DriverRegSG.input_photo,
    ),
    Window(
        TranslationFormat(TranslationBase.DriverReg_enter_fullname.slag(mode='FORMATTING')),
        MessageInput(func=input_fullname, content_types=[ContentType.TEXT]),
        parse_mode="markdown",
        state=DriverRegSG.input_fullname,
    ),
    Window(
        TranslationFormat(TranslationBase.DriverReg_enter_car_number.slag(mode='FORMATTING')),
        MessageInput(func=input_car_number, content_types=[ContentType.TEXT]),
        parse_mode="markdown",
        state=DriverRegSG.input_car_number,
    ),
)
