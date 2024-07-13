from aiogram_dialog.setup import DialogRegistry

from app.dialogs.dialogs import DLGs


def register_dialogs(dp):
    for dialog in DLGs:
        print(dialog, flush=True)
        dp.include_router(dialog)