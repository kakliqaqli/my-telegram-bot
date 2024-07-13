import asyncio
import logging
import os

import aiohttp
import aiohttp_jinja2
import jinja2
from aiogram.types import BotCommandScopeDefault, BotCommand
from aiogram_dialog.setup import setup_dialogs
from aiogram_dialog.tools import render_preview
from aiohttp import web

import bootstrap
from app.dialogs import router, register_dialogs
from app.dialogs.dialogs import error_handler
from service.http2orm.models import Language
from service.translator.base import TranslationService, TranslationBase
from web import init_routes

# from web.models import User

logging.basicConfig(level=logging.DEBUG)

app = web.Application(client_max_size=1024 ** 3)
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(os.path.join(os.getcwd(), "build")))


async def main():
    init_routes(app)
    bot = bootstrap.MyBot().getInstance()
    dp = bootstrap.MyDispatcher().getInstance()
    scheduler = bootstrap.Scheduler().getInstance()
    scheduler.start()
    router.register_commands()
    languages = await Language.get(raw=True)
    TranslationService().load_translations(languages)
    TranslationService.base.set_mode('CLEAR')
    print(TranslationService.base.DriverReg_enter_fullname, flush=True)
    print(TranslationBase.DriverReg_enter_fullname, flush=True)
    # print(await User.get_or_create().filter(id='dsfsdf').fetch(), flush=True)
    dp.errors.register(error_handler)
    register_dialogs(dp)
    setup_dialogs(dp)
    # await render_preview(dp, "preview.html", simulate_events=True)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8004)
    print(site.name)
    await site.start()
    await bot.set_my_commands([BotCommand(command="start", description="Запустить бота")],
                              scope=BotCommandScopeDefault())
    await dp.start_polling(bot, )


if __name__ == '__main__':
    asyncio.run(main())
