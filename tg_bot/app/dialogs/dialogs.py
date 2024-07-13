from aiogram.dispatcher.event.bases import UNHANDLED
from aiogram_dialog import Dialog, DialogManager, LaunchMode
from aiogram_dialog.api.exceptions import UnknownIntent

import bootstrap
from app.dialogs.universal_methods import on_close
from app.dialogs.windows.driver_profile.menu import DriverProfileWin
from app.dialogs.windows.driver_registration.menu import DriverRegWin
from app.dialogs.windows.driver_search.menu import DriverSearchWin
from app.dialogs.windows.menu.handlers import start
from app.dialogs.windows.menu.menu import MainWin
from app.dialogs.windows.order.menu import OrderWin
from app.dialogs.windows.user_registration.menu import UserRegWin

# from app.dialogs.windows.profil.menu import ProfilWin

bot = bootstrap.MyBot().getInstance()

from aiogram import types
from aiogram.filters import BaseFilter


class StartsWithFilter(BaseFilter):
    async def __call__(self, callback_query: types.CallbackQuery):
        return callback_query.data.startswith('accept') or callback_query.data.startswith('sendcode')


async def error_handler(event, dialog_manager: DialogManager):
    """Example of handling UnknownIntent Error and starting new dialog"""
    print(event, flush=True)

    if event.update.callback_query:
        message = event.update.callback_query.message
        await event.update.callback_query.message.delete()
    elif event.update.message:
        message = event.update.message
        await event.update.callback_query.message.delete()
    else:
        return UNHANDLED
    if isinstance(event.exception, UnknownIntent):
        await start(message, dialog_manager)
    else:
        await bot.send_message(message.chat.id, "Произошла непредвиденная ошибка. Нажмите или отправьте команду /start")


# @dlg_router.callback_query()
# async def handle_start_query(call: CallbackQuery, dialog_manager: DialogManager):
#    if call.data.startswith("check"):
#        await on_check_registration(call, None, dialog_manager)

DLGs = (
    Dialog(*MainWin, launch_mode=LaunchMode.ROOT, on_close=on_close),
    Dialog(*DriverRegWin, launch_mode=LaunchMode.ROOT, on_close=on_close),
    Dialog(*UserRegWin, launch_mode=LaunchMode.SINGLE_TOP, on_close=on_close),
    Dialog(*OrderWin, launch_mode=LaunchMode.SINGLE_TOP, on_close=on_close),
    Dialog(*DriverProfileWin, launch_mode=LaunchMode.SINGLE_TOP, on_close=on_close),
    Dialog(*DriverSearchWin, launch_mode=LaunchMode.SINGLE_TOP, on_close=on_close),
)
    #Dialog(*DriverWin, launch_mode=LaunchMode.SINGLE_TOP, on_start=load_dialog_data),
    # ProfilDLG = Dialog(*ProfilWin, launch_mode=LaunchMode.SINGLE_TOP),
    #Dialog(*PayWin, launch_mode=LaunchMode.SINGLE_TOP),
