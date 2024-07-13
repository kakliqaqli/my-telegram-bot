from aiogram.enums import ContentType
from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import RequestContact
from aiogram_dialog.widgets.markup.reply_keyboard import ReplyKeyboardFactory

from app.dialogs.windows.user_registration.methods import input_contact
from service.translator.common.translate_dataclasses import TranslationBase
from service.translator.patching.aiogram_dialog.widgets import TranslationFormat
from service.translator.base import TranslationService
from states.states import UserRegSG

UserRegWin = (
    Window(
        TranslationFormat(TranslationBase.UserRegEnterPhone.slag(mode='FORMATTING')),
        RequestContact(TranslationFormat(TranslationBase.UserRegShareContact.slag(mode='FORMATTING'))),
        MessageInput(func=input_contact, content_types=[ContentType.CONTACT]),
        parse_mode="markdown",
        state=UserRegSG.input_phone,
        markup_factory=ReplyKeyboardFactory(resize_keyboard=True)
    ),
)
