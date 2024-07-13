from aiogram.enums import ContentType
from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Format

from app.dialogs.windows.driver_profile.methods import input_photo, input_car_number, profile_getter, input_fullname
from service.translator.common.translate_dataclasses import TranslationBase
from service.translator.patching.aiogram_dialog.widgets import TranslationFormat
from states.states import DriverProfileSG

DriverProfileWin = (
    Window(
        DynamicMedia('driver.photo', when='driver.photo'),
        Format('*{driver.fullname}* — {driver.car_number}'),
        SwitchTo(TranslationFormat(TranslationBase.DriverProfile_photo.slag(mode='FORMATTING')), state=DriverProfileSG.input_photo, id='edit_photo'),
        SwitchTo(TranslationFormat('Фио'), state=DriverProfileSG.input_fullname, id='edit_car_number'),
        SwitchTo(TranslationFormat(TranslationBase.DriverProfile_car_number.slag(mode='FORMATTING')), state=DriverProfileSG.input_car_number, id='edit_car_number'),
        getter=profile_getter,
        parse_mode="markdown",
        state=DriverProfileSG.show,
    ),
    Window(
        TranslationFormat(TranslationBase.DriverProfile_input_value.slag(mode='FORMATTING')),
        MessageInput(func=input_car_number, content_types=[ContentType.TEXT]),
        SwitchTo(TranslationFormat(TranslationBase.DriverProfile_back.slag(mode='FORMATTING')), state=DriverProfileSG.show, id='back'),
        parse_mode="markdown",
        state=DriverProfileSG.input_car_number,
    ),
    Window(
        TranslationFormat(TranslationBase.DriverProfile_input_value.slag(mode='FORMATTING')),
        MessageInput(func=input_photo, content_types=[ContentType.PHOTO]),
        SwitchTo(TranslationFormat(TranslationBase.DriverProfile_back.slag(mode='FORMATTING')), state=DriverProfileSG.show, id='back'),
        parse_mode="markdown",
        state=DriverProfileSG.input_photo,
    ),
    Window(
        TranslationFormat(TranslationBase.DriverProfile_input_value.slag(mode='FORMATTING')),
        MessageInput(func=input_fullname, content_types=[ContentType.TEXT]),
        SwitchTo(TranslationFormat(TranslationBase.DriverProfile_back.slag(mode='FORMATTING')), state=DriverProfileSG.show, id='back'),
        parse_mode="markdown",
        state=DriverProfileSG.input_fullname,
    ),
)
