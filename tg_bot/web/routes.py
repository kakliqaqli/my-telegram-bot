import asyncio
import logging

from aiohttp.abc import Request
from aiohttp.web_response import Response

from service.managers.user_data_manager import UserData
from service.managers.meet_manager import RideSystem
from service.translator.base import TranslationService
import bootstrap
from states.states import OrderStates, MainSG

bot = bootstrap.MyBot().getInstance()


async def clear_user_cache(request: Request) -> Response:
    user_id = request.match_info.get('user_id')
    if user_id:
        UserData.cache.pop(int(user_id), None)
    return Response(status=200)


async def send_notification(request: Request) -> Response:
    data = await request.json()
    trans = TranslationService.base
    slag = trans.NotificationAcceptDriver.slag('CLEAR')
    text = TranslationService().translate(slag=slag, lang=data.get('lang'))
    await bot.send_message(data.get('user_id'), text)
    user_data = await UserData(user_id=data.get('user_id')).get_data()
    bg_manager = await user_data.create_bg_manager()
    await bg_manager.start(state=MainSG.show)
    return Response(status=200)


async def change_translation(request: Request) -> Response:
    data = await request.json()
    print(data, flush=True)
    TranslationService().load_translations(data.get('data'))
    return Response(status=200)


async def start_search(request: Request) -> Response:
    data = await request.json()
    print(data, flush=True)
    user_data = await UserData(user_id=data.get('user_id')).get_data()
    await RideSystem().add_request(user_data=user_data, request_data=data)
    bg_manager = await user_data.create_bg_manager()
    await bg_manager.start(state=OrderStates.in_search)
    return Response(status=200)